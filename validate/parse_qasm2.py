"""Try to parse all QASM files in the given directory using QASM2 Qiskit.

This script is used to validate the QASM2 parser in Qiskit. It tries to parse
all QASM files in the given directory and prints the result of the parsing.
Scan the file in sorted order (alphabetical).

Parameters:
--input_folder: str, the path to the folder containing the QASM files.
--image_name: str, the name of the image to use for the Docker container.
    (default: qiskit_runner)

It uses docker python package to run the Qiskit image in a container and
parse the QASM files. Each file is parsed using a single command on the image.
Convert python script into a single line bash command to run in the container.
```python
from qiskit import qasm2
qasm2.load(<ACTUAL_FILE_PATH>)
```
Remember to mount the input folder as a volume in the container.
The docker workdir is /workspace and the input folder should be mounted at /workspace.
Convert the input folder to an absolute path before mounting it.
The execution in the container should be robust to count exactly when a parsing
fails because of the file.
There should be a counter of the number of files that were parsed successfully
and the number of files that failed to parse. Print the counter at the end of
the execution.

Store the list of correctly parsed files and the list of failed files in a
JSON file in the same folder with name qasm2_parser_result.json.
The fields in the JSON file should be:
- success: List[str], the list of successfully parsed files.
- failure:
    List[Dict[str, str]], the list of failed files with the error message.
    The dictionary should have the keys 'file' and 'error'.
- success_count: int, the number of files parsed successfully.
- failure_count: int, the number of files failed to parse.
- percentage_of_success: float, the percentage of files parsed successfully.


# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib every time that paths are checked, created or composed.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate

Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports
"""


import json
from pathlib import Path
from typing import List, Dict, Tuple
import click
import docker
from rich.console import Console

console = Console()


def validate_qasm_files(input_folder: Path, image_name: str,
                        platform_name: str) -> None:
    """Validate QASM files by running Qiskit parser in Docker container."""
    qasm_files = _get_sorted_qasm_files(input_folder=input_folder)
    success_files, failure_files = _process_files(
        qasm_files=qasm_files, image_name=image_name,
        input_folder=input_folder, platform_name=platform_name)
    _save_results_to_json(input_folder=input_folder,
                          success_files=success_files,
                          failure_files=failure_files,
                          platform_name=platform_name)


def _get_sorted_qasm_files(input_folder: Path) -> List[Path]:
    """Retrieve a sorted list of QASM files in the input folder."""
    qasm_files = sorted(input_folder.glob("*.qasm"))
    if not qasm_files:
        console.print(f"No QASM files found in {input_folder}")
    return qasm_files


def _process_files(qasm_files: List[Path],
                   image_name: str, input_folder: Path, platform_name: str) -> Tuple[List[str],
                                                                                     List[Dict[str, str]]]:
    """Process and parse each QASM file in the Docker container."""
    success_files = []
    failure_files = []
    for qasm_file in qasm_files:
        success, message = _run_docker_container(
            image_name=image_name, qasm_file=qasm_file,
            input_folder=input_folder, platform_name=platform_name)
        if success:
            success_files.append(str(qasm_file.name))
        else:
            failure_files.append(
                {"file": str(qasm_file.name),
                 "error": message})
    return success_files, failure_files


def _run_docker_container(
        image_name: str, qasm_file: Path, input_folder: Path, platform_name: str) -> Tuple[bool, str]:
    """Run the Docker container to parse the QASM file."""
    if platform_name == "qiskit":
        command = _compose_docker_command_qiskit(qasm_file=qasm_file)
    elif platform_name == "pytket":
        command = _compose_docker_command_pytket(qasm_file=qasm_file)
    elif platform_name == "pennylane":
        command = _compose_docker_command_pennylane(qasm_file=qasm_file)
    console.print(
        f"Parsing file {qasm_file.name} in Docker image {image_name}")
    return _execute_in_docker(
        image_name=image_name, command=command, input_folder=input_folder)


def _compose_docker_command_qiskit(qasm_file: Path) -> str:
    """Compose the bash command to run the QASM2 parser."""
    return f"python -c 'from qiskit import qasm2; qasm2.load(\"{qasm_file.name}\"); print(\"Parsed successfully\")'"


def _compose_docker_command_pytket(qasm_file: Path) -> str:
    """Compose the bash command to run the QASM2 parser."""
    return f"python -c 'from pytket.qasm import circuit_from_qasm_str; circuit_from_qasm_str(open(\"{qasm_file.name}\", \"r\").read()); print(\"Parsed successfully\")'"


def _compose_docker_command_pennylane(qasm_file: Path) -> str:
    """Compose the bash command to run the QASM2 parser."""
    return f"python -c 'import pennylane as qml; qml.from_qasm(open(\"{qasm_file.name}\", \"r\").read()); print(\"Parsed successfully\")'"


def _execute_in_docker(
        image_name: str, command: str, input_folder: Path) -> Tuple[bool, str]:
    """Execute the command inside the Docker container and handle parsing."""
    client = docker.from_env()
    abs_folder = input_folder.resolve()
    try:
        output = client.containers.run(
            image=image_name,
            command=command,
            volumes={str(abs_folder): {'bind': '/workspace', 'mode': 'ro'}},
            working_dir='/workspace'
        )
        console.print(f"Output: {output.decode()}")
        return True, output.decode()
    except docker.errors.ContainerError as e:
        console.print(f"Error parsing: {e}", style="bold red")
        return False, str(e)


def _save_results_to_json(
        input_folder: Path, success_files: List[str],
        failure_files: List[Dict[str, str]], platform_name: str) -> None:
    """Save the result of parsing to a JSON file."""
    total_files = len(success_files) + len(failure_files)
    success_count = len(success_files)
    failure_count = len(failure_files)
    percentage_of_success = (
        success_count / total_files) * 100 if total_files > 0 else 0

    result = {
        "success": success_files,
        "failure": failure_files,
        "success_count": success_count,
        "failure_count": failure_count,
        "percentage_of_success": percentage_of_success
    }

    output_file = input_folder / f"qasm2_parser_result_{platform_name}.json"
    with output_file.open("w") as f:
        json.dump(result, f, indent=4)

    console.print(f"Results saved to {output_file}")


@click.command()
@click.option('--input_folder', type=click.Path(exists=True, file_okay=False, path_type=Path),
              required=True, help="The path to the folder containing the QASM files.")
@click.option('--image_name', default='qiskit_runner', show_default=True,
              required=True, help="The name of the Docker image.")
@click.option('--platform_name', type=click.Choice(
    ['qiskit', 'pytket', 'pennylane']),
    default='qiskit', show_default=True, required=True,
    help="The name of the platform.")
def main(input_folder: Path, image_name: str, platform_name: str) -> None:
    """Main command to parse all QASM files using Qiskit in Docker."""
    validate_qasm_files(
        input_folder=input_folder, image_name=image_name,
        platform_name=platform_name)


if __name__ == '__main__':
    main()
