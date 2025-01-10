#!/usr/bin/env python
# coding: utf-8

import tempfile
import docker
from bs4 import BeautifulSoup
import requests
import dspy
from typing import List, Tuple, Dict, Any, Optional
from pandarallel import pandarallel
import os
import time
import re
import sys
import json
from pathlib import Path
import uuid
import random

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
from tqdm.auto import tqdm
from rich.console import Console
import numpy as np
import fpsample
from sklearn.metrics.pairwise import cosine_distances

from aiexchange.tools.docker_tools import (
    get_file_content_in_docker,
    get_grep_output_in_docker,
    run_qiskit_code_in_docker
)

from aiexchange.feedback.log_understanding import (
    is_code_fixed,
    extract_filenames_from_traceback,
    extract_objects_from_traceback
)
from aiexchange.feedback.model_understanding import (
    remove_backticks_lines
)
from aiexchange.knowledge_base.library import (
    get_chained_file_contents,
    get_files_from_entity
)
from aiexchange.tools.token_counter import count_tokens

from aiexchange.tools.base_model_setup import (
    BASE_MODEL, LARGE_CONTEXT_MODEL, EMBEDDING_MODEL
)

import google.generativeai as genai


tqdm.pandas()
pandarallel.initialize(progress_bar=True)

FOLDER_WITH_API_MIGRATION_KNOWLEDGE = Path(
    "data/changelogs/v001/api_migration_docs")
FOLDER_DATASET = Path("data/finetuning/datasets/generated")
PATH_API_JSON = Path("data/finetuning/apis/old_version/entities.json")


# Global variable to control interactive mode
INTERACTIVE_MODE = False
SLEEP_TIME = 5  # Configurable timeout for autonomous mode
N_PROGRAMS = 10  # Number of programs to generate
FIXING_ATTEMPTS = 3  # Number of attempts to fix the code


def wait_for_user():
    if INTERACTIVE_MODE:
        input("Press Enter to continue...")
    else:
        time.sleep(SLEEP_TIME)


def fetch_markdown_from_url(
        url: str, max_retries: int = 5, retry_interval: int = 5) -> str:
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                if text:
                    return text
                else:
                    continue
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                raise e


def get_stackoverflow_inspiration() -> str:
    url = "https://www.isimonbrown.co.uk/dicestack/?site=stackoverflow&min_score=10&tagged=&answer_status=any"
    page_content = fetch_markdown_from_url(url)
    start_index = page_content.find("Answer status")
    if start_index != -1:
        page_content = page_content[start_index:]
        lines = page_content.split('\n')
        lines = lines[3:-20]
        cleaned_lines = [re.sub(r'^\d+', '', line) for line in lines]
        cleaned_lines = [line for line in cleaned_lines if line.strip()]
        page_content = '\n'.join(cleaned_lines)
    return page_content


class BrainstormQiskitTitles(dspy.Signature):
    """Generate fictional titles for questions on quantum computing using qiskit v0.45. Only Qiskit library should be used, focus on qiskit compiler, skip aqua and ignis. (No external libraries)"""

    inspiring_titles: str = dspy.InputField(
        desc="Inspiring titles from StackOverflow")
    inspiring_api: str = dspy.InputField(
        desc="Inspiring API documentation")
    num_titles: int = dspy.InputField(desc="Number of titles to generate")
    generated_titles: List[str] = dspy.OutputField(
        desc="List of generated titles")


class ExpandQiskitTitleToDescription(dspy.Signature):
    """Expand a title to a full description of a question on Stack Overflow about Qiskit."""

    title: str = dspy.InputField(desc="Title of the question")
    inspiring_api: str = dspy.InputField(
        desc="Inspiring API documentation")
    expanded_description: str = dspy.OutputField(
        desc="Expanded description of the question")


class ImplementQiskitAnswer(dspy.Signature):
    """Implement a Qiskit answer in Qiskit v0.45 and return only the Python code snippet."""

    title: str = dspy.InputField(desc="Title of the question")
    expanded_description: str = dspy.InputField(
        desc="Expanded description of the question")
    inspiring_api: str = dspy.InputField(
        desc="Inspiring API documentation")
    code_snippet: str = dspy.OutputField(
        desc="Self-contained Python code snippet for the implementation. It must use something from the inspiring Qiskit API.")


class ChipInAndHelp(dspy.Signature):
    """Help another user with a wrong answer by providing a corrected implementation."""

    title: str = dspy.InputField(desc="Title of the question")
    description: str = dspy.InputField(desc="Description of the question")
    inspiring_api: str = dspy.InputField(
        desc="Inspiring API documentation")
    implementation: str = dspy.InputField(
        desc="Original implementation code snippet")
    log_output: str = dspy.InputField(
        desc="Log output of the original implementation")
    extra_context: str = dspy.InputField(
        desc="Extra context to help fix the code (e.g. API doc, docstrings, file contents, migration guides, release notes, etc.)")
    corrected_code: str = dspy.OutputField(
        desc="Self-contained corrected Python code snippet. It must use something from the inspiring Qiskit API.")


def upgrade_qiskit_code(
        migration_documents: List[str],
        snippet: str, log_output: str = None) -> str:
    assert len(
        migration_documents) > 0, "There should be at least one migration document."
    model = genai.GenerativeModel("gemini-1.5-flash")
    instruction = "Given this documentation about the API migration, upgrade the given code snippet to use qiskit v1. reply only with code."
    prompt = "\n".join(
        migration_documents[:3]) + f"\n{instruction}\n```python\n{snippet}\n```"
    if log_output:
        prompt += f"\n\nThe logs from the previous run:\n```\n{log_output}\n```"
    model.count_tokens(prompt)
    breakpoint()
    response = model.generate_content(prompt)
    return response.text


def get_existing_titles(folder: str) -> List[str]:
    """
    Read all JSON files in the specified folder, load them, and return their 'title' field.

    Args:
        folder (str): The path to the folder containing JSON files.

    Returns:
        List[str]: A list of titles extracted from the JSON files.
    """
    titles = []
    for file_path in Path(folder).glob("*.json"):
        with open(file_path, 'r') as file:
            data = json.load(file)
            if 'title' in data:
                titles.append(data['title'])
    return titles


def select_diverse_set_of_titles(
        candidate_titles: List[str],
        already_selected_titles: List[str],
        num_titles: int) -> List[str]:
    global EMBEDDING_MODEL

    # Convert the generated titles to embeddings
    titles_embeddings = EMBEDDING_MODEL.encode(
        candidate_titles + already_selected_titles, batch_size=32,
        show_progress_bar=True)

    candidate_titles_embeddings = titles_embeddings[:len(candidate_titles)]
    already_selected_titles_embeddings = titles_embeddings[len(
        candidate_titles):]

    # Calculate the cosine distances between candidate titles and already selected titles
    distances = cosine_distances(
        candidate_titles_embeddings, already_selected_titles_embeddings)

    # Sum the distances for each candidate title to get a measure of how far each candidate is from the selected titles
    summed_distances = distances.sum(axis=1)

    # Get the indices of the candidate titles sorted by their summed distances in descending order
    sorted_indices = np.argsort(summed_distances)[::-1]

    # Select the top num_titles candidate titles
    diverse_titles = [candidate_titles[i] for i in sorted_indices[:num_titles]]

    return diverse_titles


console = Console(color_system=None)


def main():
    docs = load_migration_docs()
    qiskit_titles_generator = dspy.ChainOfThought(BrainstormQiskitTitles)
    n_programs_generated = 0
    all_api_data = json.load(open(PATH_API_JSON, "r"))

    while n_programs_generated < N_PROGRAMS:
        all_titles_and_apis = generate_titles(
            qiskit_titles_generator, all_api_data)
        selected_titles_and_apis = select_titles(all_titles_and_apis)
        console.log("Selected Diverse Titles:")
        selected_titles = [title for title, _ in selected_titles_and_apis]
        console.log(selected_titles)
        wait_for_user()

        for title, inspiring_api in selected_titles_and_apis:
            process_title(title, docs, inspiring_api)
            n_programs_generated += 1


def load_migration_docs() -> List[str]:
    docs = []
    for file in FOLDER_WITH_API_MIGRATION_KNOWLEDGE.glob("*.md"):
        doc = Path(file).read_text()
        docs.append(doc)
        total_tokens = count_tokens("gemini-1.5-flash", doc)
        console.log(f"Read {file} > {total_tokens} tokens")
    return docs


def generate_titles(
        qiskit_titles_generator: dspy.ChainOfThought, all_api_data) -> List[
        Tuple[str, str]]:
    all_titles_and_api = []
    console.log("Generated Titles:")
    for _ in range(3):
        inspiring_questions_titles = get_stackoverflow_inspiration()
        inspiring_api = json.dumps(random.choice(all_api_data), indent=4)
        console.log("Inspiring API:")
        console.log(inspiring_api)
        lm = dspy.LM(BASE_MODEL)
        dspy.configure(lm=lm)
        response = retry_request(
            qiskit_titles_generator,
            inspiring_titles=inspiring_questions_titles,
            inspiring_api=inspiring_api,
            num_titles=20
        )
        new_titles = response.generated_titles
        all_titles_and_api.extend([
            (title, inspiring_api) for title in new_titles])
        console.log(response.generated_titles)
    return all_titles_and_api


def retry_request(generator: dspy.ChainOfThought, **kwargs) -> Any:
    retries = 5
    for attempt in range(retries):
        try:
            response = generator(**kwargs)
            return response
        except Exception as e:
            console.log(f"Error: {e}")
            if attempt < retries - 1:
                console.log("Retrying...")
                time.sleep(60)
            else:
                console.log("Failed after multiple attempts.")
                raise e


def select_titles(all_titles_and_apis: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    all_titles = [title for title, _ in all_titles_and_apis]
    selected_titles = select_diverse_set_of_titles(
        candidate_titles=list(set(all_titles)),
        already_selected_titles=get_existing_titles(FOLDER_DATASET),
        num_titles=5
    )
    selected_titles_and_apis = [
        (title, inspiring_api)
        for title, inspiring_api in all_titles_and_apis
        if title in selected_titles]
    return selected_titles_and_apis


def process_title(title: str, docs: List[str], inspiring_api: str) -> None:
    intent_code = str(uuid.uuid4())
    console.log("Title:")
    console.log(title)
    description_response = expand_title_to_description(title, inspiring_api)
    description = description_response.expanded_description
    console.log("Expanded Description:")
    console.log(description)
    wait_for_user()

    implementation_response = implement_answer(
        title, description, inspiring_api)
    i_snippet = implementation_response.code_snippet
    console.log("FIRST - Code Snippet:")
    console.log(i_snippet)

    old_version_logs = run_qiskit_code_in_docker(
        i_snippet, "qiskit_image_0.45.0")
    console.log("Old Version Logs:")
    console.log(old_version_logs)

    if is_code_fixed(old_version_logs):
        i_attempts = [i_snippet]
        i_errors = [old_version_logs]
    else:
        i_snippet, i_attempts, i_errors = fix_code(
            title, description, inspiring_api,
            implementation_response.code_snippet, old_version_logs,
            version_number="0.45.0")

    old_version_logs = i_errors[-1]

    if is_code_fixed(old_version_logs):
        save_code(i_snippet, intent_code, "OLD")

        console.log("Upgrading the code...")
        u_snippet = upgrade_qiskit_code(
            migration_documents=docs, snippet=i_snippet)
        console.log("Upgraded Code:")
        console.log(u_snippet)

        new_version_logs = run_qiskit_code_in_docker(
            u_snippet, "qiskit_image_1.2.0")
        console.log("New Version Logs:")
        console.log(new_version_logs)

        if is_code_fixed(new_version_logs):
            u_attempts = [u_snippet]
            u_errors = [new_version_logs]
        else:
            u_snippet, u_attempts, u_errors = fix_code(
                title, description, inspiring_api,
                u_snippet, new_version_logs, version_number="1.2.0", docs=docs)
            new_version_logs = u_errors[-1]

        if is_code_fixed(new_version_logs):
            save_code(u_snippet, intent_code, "NEW")

        save_data(
            title, description, inspiring_api,
            i_snippet, i_attempts, i_errors,
            u_snippet, u_attempts, u_errors,
            intent_code)


def expand_title_to_description(title: str, inspiring_api: str) -> Any:
    lm = dspy.LM(BASE_MODEL)
    dspy.configure(lm=lm)
    expand_qiskit_title_to_description = dspy.ChainOfThought(
        ExpandQiskitTitleToDescription)
    return expand_qiskit_title_to_description(
        title=title, inspiring_api=inspiring_api)


def implement_answer(title: str, description: str, inspiring_api: str) -> Any:
    lm = dspy.LM(BASE_MODEL)
    dspy.configure(lm=lm)
    implement_qiskit_answer = dspy.ChainOfThought(ImplementQiskitAnswer)
    return implement_qiskit_answer(
        title=title, expanded_description=description,
        inspiring_api=inspiring_api)


def fix_code(title: str, description: str, inspiring_api: str,
             snippet: str, logs: str,
             version_number: str, docs: List[str] = []) -> Tuple[str, List[str],
                                                                 List[str]]:
    chip_in_and_help = dspy.ChainOfThought(ChipInAndHelp)
    attempts = [snippet]
    errors = [logs]

    assert version_number == "0.45.0" or version_number == "1.2.0", "Only 0.45.0 and 1.2.0 versions are supported."
    if version_number == "1.2.0":
        assert len(
            docs) > 0, "Migration documents are required for 1.2.0 version."

    if version_number == "0.45.0":
        lm = dspy.LM(BASE_MODEL)
        dspy.configure(lm=lm)
    elif version_number == "1.2.0":
        lm = dspy.LM(LARGE_CONTEXT_MODEL)
        dspy.configure(lm=lm)

    for i in range(FIXING_ATTEMPTS):
        if is_code_fixed(logs):
            break
        # Extract filenames and objects from the logs
        explicit_file_names = extract_filenames_from_traceback(logs)
        objects_mentioned = extract_objects_from_traceback(logs)
        file_names_from_objects = [
            get_files_from_entity(
                entity_name=object_name, version_number=version_number)
            for object_name in objects_mentioned
        ]
        file_names_from_objects = [
            files[0] for files in file_names_from_objects if files]
        file_names = explicit_file_names + file_names_from_objects
        # Bring in the context from the respective files
        extra_context = get_chained_file_contents(
            file_names, version_number, max_tokens=5000, console=console)
        if version_number == "1.2.0":
            extra_context += "\n" + "\n".join([
                f"Migration Document {i+1}:\n{doc}"
                for i, doc in enumerate(docs)])
        chip_in_response = chip_in_and_help(
            title=title,
            description=description,
            inspiring_api=inspiring_api,
            implementation=snippet,
            log_output=logs,
            extra_context=extra_context)
        console.log(f"Corrected Code (fixer attempt {i}):")
        console.log(chip_in_response.corrected_code)

        snippet = chip_in_response.corrected_code
        attempts.append(snippet)

        logs = run_qiskit_code_in_docker(
            snippet, f"qiskit_image_{version_number}")
        console.log(f"{version_number} Version Logs:")
        console.log(logs)
        errors.append(logs)
        wait_for_user()

    return snippet, attempts, errors


def save_code(snippet: str, intent_code: str, version: str) -> None:
    unique_filename = f"{intent_code}_{version}.py"
    with open(FOLDER_DATASET / unique_filename, "w") as file:
        file.write(remove_backticks_lines(snippet))


def save_data(
        title: str, description: str, inspiring_api: str,
        i_snippet: str, i_attempts: List[str],
        i_errors: List[str],
        u_snippet: str, u_attempts: List[str],
        u_errors: List[str],
        intent_code: str) -> None:
    inspiring_api_dict = json.loads(inspiring_api)
    data = {
        "title": title,
        "description": description,
        "inspiring_api": inspiring_api_dict,
        "old_version": {
            "code": i_snippet,
            "attempted_fixes": [
                {"code": snippet, "log": log}
                for snippet, log in zip(i_attempts, i_errors)
            ]
        },
        "new_version": {
            "code": u_snippet,
            "attempted_fixes": [
                {"code": snippet, "log": log}
                for snippet, log in zip(u_attempts, u_errors)
            ]
        }
    }
    with open(FOLDER_DATASET / f"{intent_code}.json", "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
