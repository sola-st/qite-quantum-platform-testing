"""
Processes quantum programs from the LintQ dataset.

Arguments:
--folder_with_py: Path to the folder containing Python files (default: program_bank/LintQ_dataset/).
--output_folder: Path to the output folder (default: program_bank).

Creates a subfolder with the format: YYYY_MM_DD__HH_MM__lintq, where the prefix is the date and time of the script run.

Steps:
1. Iterate over all programs in the LintQ dataset.
2. Run each program in a controlled Docker container using the latest Qiskit version (1.2).
3. Discard programs that crash or exceed a specified runtime (e.g., 1 minute).
4. Save successfully running programs as Python files in the output folder.
5. Log error messages with stack traces of failed programs in a JSON file.
6. Save each file (Python or JSON) in a folder named after the original program but with a different extension.
7. Execute each successful program
Create a temporary folder, copy the program, mount the folder in the docker.
Append to the program a script to collect all Qiskit circuits and store each circuit in a pickle file.
    Use this function to run in Docker:
    ```
    from generators.docker_tooling import run_program_in_docker_w_timeout
    def run_program_in_docker_w_timeout(
        folder_with_file: Path, file_name: str, timeout: int = 60, console=None) -> None:
    ```
    Append this script the program before executing it in Docker:
    ```
      # get all the global variables which are QuantumCircuit objects
  all_qiskit_circuits = [
    {"var_name": name, "circuit": v}
    for name, v in globals().items() if isinstance(v, QuantumCircuit)]
    # store all the circuits in a pickle file
    filename = os.path.basename(__file__)
    for var_name, circuit in all_qiskit_circuits:
        output_name = f"{filename}_{var_name}.pkl"
        with open(output_name, "wb") as f:
            pickle.dump(circuit, f)
    print(f"Stored all Qiskit circuits in {filename}")
    print("COMPLETED_SUCCESSFULLY")
    ```
Note that each circuit is saved with the name of the program and the global variable for provenance.
8. Copy all the pickle files in the temporary folder to the output folder. (make sure tha the temporary folder is still alive when doing this copy). This copy is done after the program is executed and outside the docker.

The final output is a folder containing all the Qiskit circuits.

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
- make sure that any output folder exists before storing file in it, otherwise create it.

Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports

"""

import os
import json
import pickle
import shutil
import tempfile
import click
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from rich.console import Console
from qiskit import QuantumCircuit
from tqdm import tqdm
from generators.docker_tooling import run_program_in_docker_w_timeout

console = Console()


def ensure_output_folder_exists(output_folder: Path) -> None:
    """Ensure the output folder exists, create if necessary."""
    output_folder.mkdir(parents=True, exist_ok=True)


def create_subfolder(output_folder: Path) -> Path:
    """Create a timestamped subfolder in the output folder."""
    timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M')
    subfolder = output_folder / f"{timestamp}__lintq"
    ensure_output_folder_exists(subfolder)
    return subfolder


def get_python_files(folder_with_py: Path) -> List[Path]:
    """Get all Python files from the specified folder."""
    return list(folder_with_py.glob("*.py"))


def log_error(output_folder: Path, file_name: str, error: Exception) -> None:
    """Log error with stack trace into a JSON file."""
    error_log = {
        "file": file_name,
        "error_message": str(error),
        "stack_trace": repr(error)
    }
    error_file = output_folder / f"{file_name}.json"
    with error_file.open("w") as f:
        json.dump(error_log, f, indent=4)


def append_qiskit_circuit_script(program_code: str) -> str:
    """Append code to collect and store all Qiskit circuits in a pickle."""
    circuit_script = """
# get all the global variables which are QuantumCircuit objects
import os
import pickle
all_qiskit_circuits = [
    {"var_name": name, "circuit": v}
    for name, v in globals().items() if isinstance(v, QuantumCircuit)]
# store all the circuits in a pickle file
filename = os.path.basename(__file__)
for circuit_data in all_qiskit_circuits:
    var_name = circuit_data['var_name']
    circuit = circuit_data['circuit']
    output_name = f"{filename}_{var_name}.pkl"
    with open(output_name, "wb") as f:
        pickle.dump(circuit, f)
print(f"Stored all Qiskit circuits in {filename}")
print("COMPLETED_SUCCESSFULLY")
"""
    return program_code + circuit_script


def run_program_and_collect_circuits(
    folder_with_py: Path, file_name: str,
    temp_folder: Path, output_folder: Path,
    timeout: int
) -> None:
    """Run the program inside Docker, collect Qiskit circuits, and handle errors."""
    temp_file = temp_folder / file_name
    try:
        # Copy the program to a temporary folder and append the circuit script
        program_path = folder_with_py / file_name
        program_code = program_path.read_text()
        program_code_with_script = append_qiskit_circuit_script(program_code)
        temp_file.write_text(program_code_with_script)

        # Run the program in Docker
        run_program_in_docker_w_timeout(
            folder_with_file=temp_folder,
            file_name=file_name,
            console=console,
            timeout=timeout
        )

        # Move all pickle files to the output folder
        move_pickles_to_output(temp_folder, output_folder, file_name)

    except Exception as e:
        log_error(output_folder, file_name, e)


def move_pickles_to_output(
        temp_folder: Path, output_folder: Path, file_name: str) -> None:
    """Move pickle files from the temporary folder to the output folder."""
    for pickle_file in temp_folder.glob(f"{file_name}_*.pkl"):
        shutil.move(str(pickle_file), output_folder / pickle_file.name)


@click.command()
@click.option(
    '--folder_with_py',
    default='program_bank/LintQ_dataset/',
    required=True,
    type=click.Path(exists=True),
    help='Path to the folder containing Python files.'
)
@click.option(
    '--output_folder',
    default='program_bank',
    required=True,
    type=click.Path(),
    help='Path to the output folder.'
)
@click.option(
    '--timeout',
    default=60,
    required=True,
    type=int,
    help='Maximum runtime in seconds for each program.'
)
def main(folder_with_py: str, output_folder: str, timeout: int) -> None:
    """Processes quantum programs from the LintQ dataset."""
    folder_with_py = Path(folder_with_py)
    output_folder = Path(output_folder)
    subfolder = create_subfolder(output_folder)

    python_files = get_python_files(folder_with_py)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_folder = Path(temp_dir)

        # sort them alphabetically
        python_files.sort()

        for python_file in tqdm(python_files):
            # print(f"Processing {python_file.name}...")
            run_program_and_collect_circuits(
                folder_with_py=folder_with_py,
                file_name=python_file.name,
                temp_folder=temp_folder,
                output_folder=subfolder,
                timeout=timeout
            )


if __name__ == "__main__":
    main()
