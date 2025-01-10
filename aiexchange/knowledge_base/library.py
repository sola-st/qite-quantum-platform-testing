import docker
from rich.console import Console

from aiexchange.tools.docker_tools import (
    get_file_content_in_docker,
    get_grep_output_in_docker,
)
from aiexchange.tools.token_counter import count_tokens
import re
from typing import List


def get_chained_file_contents(
        filenames: list, version_number: str, max_tokens: int, console=None) -> str:
    """
    Retrieves the contents of the provided filenames from a Docker container,
    formats the contents with line numbers, and returns the concatenated result.
    Args:
    filenames (list): The list of filenames to retrieve contents for.
    version_number (str): The version number used to construct the Docker image name.
    Returns:
    str: The concatenated and formatted contents of the files, with each line numbered.
    """

    file_contents = []
    if console is None:
        console = Console(color_system=None)
    console.log("Chained File Contents:")
    for filename in filenames:
        console.log(f"File: {filename}")
        content = get_file_content_in_docker(
            image_name=f"qiskit_image_{version_number}", file_path=filename)
        if content:
            num_tokens = count_tokens("gemini-1.5-flash", content)
            n_lines = content.count('\n')
            console.log(f"\t - Tokens: {num_tokens} - LOC: {n_lines}")
            lines = content.split('\n')
            formatted_lines = [
                f"{str(i+1).zfill(4)}| {line}" for i, line in enumerate(lines)]
            file_contents.append(
                f"File: {filename}\n" + "\n".join(formatted_lines))
        file_separator = "\n" + "=" * 80 + "\n"
    if len(file_contents) == 0:
        return "No files found."
    chained_content = file_separator.join(file_contents)
    tokens_length = count_tokens("gemini-1.5-flash", chained_content)
    if tokens_length > max_tokens:
        proportion_to_remove = (tokens_length - max_tokens) / tokens_length
        # remove the same proportion of characters from each file
        new_file_contents = []
        for content in file_contents:
            new_content = content[:int(
                len(content) * (1 - proportion_to_remove))] + "\n... TRUNCATED ..."
            new_file_contents.append(new_content)
        chained_content = file_separator.join(new_file_contents)
    return chained_content


def get_files_from_entity(
        entity_name: str, version_number: str, console=None) -> List[str]:
    """
    Get the files in which the entity is defined.

    Args:
        entity_name (str): The name of the entity to search for.
        version_number (str): The version number used to construct the Docker image name.
        console (Console, optional): The console object for logging. Defaults to None.

    Returns:
        List[str]: A list of file paths where the entity is defined.
    """
    if console is None:
        console = Console(color_system=None)
    console.log(f"Entity: {entity_name}")
    base_dir = "/usr/local/lib/python3.10/site-packages/qiskit"
    grep_query = f"def {entity_name}\\(" if entity_name[0].islower(
    ) else f"class {entity_name}:|class {entity_name}\\("
    result = get_grep_output_in_docker(
        image_name=f"qiskit_image_{version_number}",
        pattern=grep_query,
        file_dir=base_dir,
        context_size=0,
        compress=False,
        regex_enabled=True,
    )
    # result = qiskit/circuit/quantumcircuit.py:class QuantumCircuit:\n
    file_paths = []
    for line in result.splitlines():
        if ".py:" in line:
            match = re.match(r"^(.*\.py):", line)
            if match:
                file_path = match.group(1)
                file_paths.append(file_path)
    return list(set(file_paths))
