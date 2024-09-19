"""Script that runs python files in an input folder and gets their qasm.

This script processes Python files in the input folder, replaces the last part
with a snippet that is needed to extract the qasm from the any quantum circuit
objects in the global scope, and saves the modified files to the output folder.
For each QuantumCircuit object in the global scope, it converts it to Pytket
circuit and saves the both the original Qiskit circuit and the Pytket circuit
as qasm files.
The new files have the name of the python file as prefix (except the extension)
and then the suffix is a uuid of length 6 followed by _pytket.qasm or
_qiskit.qasm respectively.

Input parameters:
    --input_folder: str folder with the .py files to execute
    --image_name: str, the docker image name to run (default: qiskit_runner)

The new logic is directly append to each python file in the input folder, then
the file is run in a docker container. The output is stored in the output folder
by this new logic appended to the file.

Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports

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

This is an example of how to use pytket and qiskit to extract qasm from a their
circuit objects and save them to files.
```python



```
"""

import click
from pathlib import Path
from typing import Optional
from rich.console import Console
import subprocess
import uuid
import os
import shutil
import tempfile
import docker

console = Console()


def append_qasm_extraction_snippet(file: Path) -> str:
    """Appends a QASM extraction snippet to the provided Python file."""
    # get folder of this script
    current_folder = Path(__file__).parent
    # get file extend_with_qasm_extraction.py
    snippet_file = current_folder / "extend_with_qasm_extraction.py"
    snippet = snippet_file.read_text()
    content = file.read_text()
    return content + "\n" + snippet


# Initialize rich console for logging
console = Console()


def run_file_in_docker(file_path: Path, image_name: str) -> bool:
    """Run a Python file in a Docker container and return True if successful."""
    client = docker.from_env()

    # Create a temporary directory to mount to Docker
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = Path(temp_dir) / "to_execute.py"
        shutil.copy(file_path, temp_file_path)

        try:
            # Run the file in the Docker container
            container = client.containers.run(
                image=image_name,
                volumes={str(temp_dir): {'bind': '/workspace', 'mode': 'rw'}},
                command='python /workspace/to_execute.py',
                detach=True,
                stdout=True,
                stderr=True
            )

            # Wait for the container to finish and capture the exit code
            exit_code = container.wait()['StatusCode']

            # copy back all the new files to the file_path folder
            # except to_execute.py
            for item in Path(temp_dir).iterdir():
                if item.name == "to_execute.py":
                    continue
                # replace to_execute with the original file name
                new_name = item.name.replace("to_execute.py", file_path.stem)
                shutil.copy(item, file_path.parent / new_name)

            # Collect and log the output from the container
            logs = container.logs(stdout=True, stderr=True).decode()
            container.remove()

            # Print logs in yellow
            console.log(
                f"[yellow]Output of {file_path.name}:[/yellow]\n{logs}")

            return exit_code == 0

        except docker.errors.APIError as e:
            console.log(f"[red]Error running {file_path.name}: {e}[/red]")
            return False


def process_python_file(
        file: Path, image_name: str) -> None:
    """Appends QASM extraction logic to the file and runs it in Docker."""
    modified_content = append_qasm_extraction_snippet(file=file)
    temp_file = file.with_suffix(".pyc")
    # breakpoint()
    temp_file.write_text(modified_content)
    run_file_in_docker(file_path=temp_file, image_name=image_name)
    # temp_file.unlink()


def process_files_in_folder(
        input_folder: Path, image_name: str) -> None:
    """Processes all Python files in the input folder."""
    python_files = list(input_folder.glob("*.py"))
    for file in python_files:
        process_python_file(
            file=file, image_name=image_name)


@click.command()
@click.option('--input_folder', required=True, type=click.Path(
    exists=True, file_okay=False),
    help="Folder with .py files to process.")
@click.option('--image_name', required=True, default='qiskit_runner',
              help="Docker image to run the Python files.")
def main(input_folder: str, image_name: str) -> None:
    """Main function to append QASM logic to Python files and run them in Docker."""
    input_folder_path = Path(input_folder)
    process_files_in_folder(
        input_folder=input_folder_path,
        image_name=image_name)


if __name__ == '__main__':
    main()
