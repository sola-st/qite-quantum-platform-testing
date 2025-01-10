from pathlib import Path
import docker
from rich.console import Console

from aiexchange.tools.docker_tools import (
    get_file_content_in_docker,
    get_grep_output_in_docker,
)
from aiexchange.tools.token_counter import count_tokens
import re
from typing import List
from aiexchange.tools.docker_tools import run_script_in_docker


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


def preprocess_extract_entities(
        image_name: str, directory_to_scan: str, output_dir: str,
        console=None) -> str:
    """
    Use aiexchange/knowledge_base/scan_functions.py to extract entities from the specified directory
    inside a Docker container.
    The output is stored in a JSON file in the specified output directory with the name entities.json.

    Args:
        image_name (str): The name of the Docker image to run.
        directory (str): The directory inside the Docker container to scan for entities.
        console (Console, optional): The console object for logging. Defaults to None.

    Returns:
        str: The output logs from running the script inside the Docker container.
    """

    current_folder = Path(__file__).parent
    script_path = current_folder / "scan_functions.py"
    local_output_folder = str(Path(output_dir).resolve())
    options = {
        "path_to_local_folder": directory_to_scan,
        "output_path": "/workspace/output_folder/entities.json",
    }

    if console is None:
        console = Console(color_system=None)
    console.log(
        f"Running entity extraction on directory: {directory_to_scan} in Docker container: {image_name}")

    result = run_script_in_docker(
        script_path=script_path,
        image_name=image_name,
        options=options,
        output_dir=local_output_folder,
        console=console
    )

    return result
