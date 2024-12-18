import click
import shutil
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from datetime import datetime
from rich.console import Console
import papermill as pm
from analysis_and_reporting.ddmin_target_file import minimize_instructions
from generators.docker_tooling import run_program_in_docker

"""Script that analyzes and dissects an error message.

Arguments:
    --path_error_json: Path to the * _error.json file.
    --path_program: Path to the program file.
    --report_folder: Path to the destination folder where the new report
        subfolder will be created.
    --clue_message: Clue message to be used by the ddmin tool.

The error message is a path to a json file containing:
- exception_message: The exception message.
- stack_trace: The stack trace of the exception.
- current_file: The file where the exception was raised.
- involved_functions: The functions involved in the current context.

It creates a new subfolder in the report_folder.
To decide the name of the subfolder, it uses the current date and time
in the format: YYYY_MM_DD__HH_MM.
It copies the json file and its associated program to a newly created subfolder.
It runs the ddmin tool to minimize the error, using the clue_message.
It executes the minimized program using Docker.

Example:
    python -m analysis_and_reporting.triage --path_error_json error.json \
        --path_program program.py --report_folder reports/v001_manual/011 \
        --clue_message 'Error in line 10' \

# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- avoid function with a single line which is a function call
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

console = Console()


@click.command()
@click.option(
    '--path_error_json', required=True, type=click.Path(exists=True),
    help='Path to the *_error.json file.')
@click.option(
    '--path_program', type=click.Path(exists=True), default=None,
    help='Path to the program file.')
@click.option(
    '--parent_report_folder', required=True, type=click.Path(),
    help='Path to the destination folder where the new report subfolder will be created.'
)
@click.option(
    '--clue_message', required=True,
    help='Clue message to be used by the ddmin tool.'
)
@click.option(
    '--analysis_notebook', required=True, type=click.Path(exists=True),
    default="notebooks/010_Triage_Not_Equivalence.ipynb",
    help='Path to the analysis notebook file.'
)
def analyze_and_report_cli(
        path_error_json: str, path_program: str, parent_report_folder: str,
        clue_message: str, analysis_notebook: str) -> None:
    """Analyzes and dissects an error message."""
    analyze_and_report(
        path_error_json, path_program, parent_report_folder, clue_message,
        analysis_notebook)


def analyze_and_report(
        path_error_json: str, path_program: str, parent_report_folder: str,
        clue_message: str, analysis_notebook: str) -> None:
    """Analyzes and dissects an error message."""
    error_json_path = Path(path_error_json)
    if not path_program:
        # and replace with .py
        program_path = Path(str(error_json_path)[:-18] + '.py')
        print("Inferred program path:", program_path)
    else:
        program_path = Path(path_program)
    parent_report_folder_path = Path(parent_report_folder)
    report_folder_path = create_report_folder(parent_report_folder_path)
    copy_files_to_report_folder(
        error_json_path, program_path, report_folder_path)
    # error in the report folder
    # this is needed so that everything now is relative to this folder
    error_json_path_in_report = report_folder_path / error_json_path.name
    minimize_instructions(
        input_folder=report_folder_path,
        path_to_error=error_json_path_in_report,
        clue_message=clue_message)
    minimized_program_path = Path(
        str(error_json_path_in_report)[:-5] + '_min.py')
    # report_folder_path = Path("reports/v001_manual/2024_11_04__14_48/")
    run_program_in_docker(
        folder_with_file=report_folder_path,
        file_name=minimized_program_path.name,
        console=console)
    run_analysis_ipynb_on_minimized_program(
        minimized_program_path=minimized_program_path,
        report_folder_path=report_folder_path,
        analysis_notebook=Path(analysis_notebook))


def create_report_folder(report_folder_path: Path) -> Path:
    """Creates a new subfolder in the report folder."""
    timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M')
    new_folder = report_folder_path / timestamp
    new_folder.mkdir(parents=True, exist_ok=True)
    console.log(f"Created report folder: {new_folder}")
    return new_folder


def copy_files_to_report_folder(error_json_path: Path, program_path: Path,
                                report_folder_path: Path) -> None:
    """Copies the json file and its associated program to the report folder."""
    shutil.copy(error_json_path, report_folder_path / error_json_path.name)
    shutil.copy(program_path, report_folder_path / program_path.name)
    console.log(f"Copied files to: {report_folder_path}")


def extract_circuit_variable_name(program_path: Path) -> str:
    """Extract the name of the circuit variable from the qasm file path.

    Examples:
    - qiskit_circuit_5q_10g_7553_24d42f_76b26a_error_min_qc_qiskit.qasm
    >> qc
    - qiskit_circuit_5q_10g_7553_24d42f_76b26a_error_min_random_qc_pytket.qasm
    >> random_qc
    """
    # remove up to error_min_
    assert "error_min_" in str(
        program_path), f"error_min_ not found in {program_path}. You must provide a path with error_min_"
    program_path = str(program_path)
    start = program_path.find('error_min_') + 10
    program_path = program_path[start:]
    # remove the last platform name
    end = program_path.rfind('_')
    if end == -1:
        return ""
    program_path = program_path[:end]
    return program_path


def get_qasm_pairs(report_folder_path: Path) -> List[Tuple[str, str]]:
    """Get the pairs of qasm files in the report folder that refer to the same
    circuit variable."""
    qasm_files = list(report_folder_path.glob('*.qasm'))
    qasm_pairs = []
    while qasm_files:
        qasm_a = qasm_files.pop()
        qasm_a_name = extract_circuit_variable_name(qasm_a)
        qasm_b = None
        for qasm_file in qasm_files:
            qasm_b_name = extract_circuit_variable_name(qasm_file)
            if qasm_a_name == qasm_b_name:
                qasm_b = qasm_file
                qasm_files.remove(qasm_file)
                break
        if qasm_b:
            qasm_pairs.append((str(qasm_a), str(qasm_b)))
    return qasm_pairs


def run_analysis_ipynb_on_minimized_program(
        minimized_program_path: Path, report_folder_path: Path,
        analysis_notebook: Path) -> None:
    """Runs the analysis notebook on the qasm files (if any)."""
    qasm_files = list(report_folder_path.glob('*.qasm'))
    if not qasm_files:
        console.log("No QASM files found.")
        return

    qasm_pairs = get_qasm_pairs(report_folder_path)

    for qasm_pair in qasm_pairs:
        console.log(f"QASM pair: {qasm_pair}")
        qasm_a = qasm_pair[0]
        qasm_b = qasm_pair[1]
        variable_name = extract_circuit_variable_name(qasm_a)

        parameters = {
            'PATH_QASM_A': qasm_a,
            'PATH_QASM_B': qasm_b,
            'PATH_PYTHON_FILE': str(minimized_program_path)}

        output_notebook = report_folder_path / \
            f'analysis_output_{variable_name}.ipynb'
        try:
            pm.execute_notebook(
                input_path=str(analysis_notebook),
                output_path=str(output_notebook),
                parameters=parameters)
            console.log(f"Analysis notebook executed: {output_notebook}")
        except Exception as e:
            console.log(f"Error executing analysis notebook: {e}")


if __name__ == '__main__':
    analyze_and_report_cli()
