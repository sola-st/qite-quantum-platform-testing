"""Script to identify the platform to report a bug, using LLM.

Inputs:
- input_folder: str, path to the folder containing the input files.
- target_circuit: str, name of the target circuit.
    e.g. qiskit_circuit_5q_10g_2_76cdf0.py
- target_error: str, name of the input file.
    e.g. qiskit_circuit_5q_10g_2_76cdf0_e6c9dd_error.json

Outputs:
- new file in the input folder, named:
    e.g. qiskit_circuit_5q_10g_2_76cdf0_e6c9dd_error.triage.json

Note that the folder structure is as follows:
/
qiskit_circuit_5q_10g_2_76cdf0.py
qiskit_circuit_5q_10g_2_76cdf0_qc_qiskit.qasm
qiskit_circuit_5q_10g_2_76cdf0_qc_pennylane.qasm
qiskit_circuit_5q_10g_2_76cdf0_qc_pytket.qasm
qiskit_circuit_5q_10g_2_76cdf0_e6c9dd_error.json
qiskit_circuit_5q_10g_2_76cdf0_927acc_error.json
qiskit_circuit_5q_10g_2_76cdf0_7a2ffe_error.json
qiskit_circuit_5q_10g_2_76cdf0_3eeae3_error.json

We use a template jinja present in the folder of this script file, and called:
paltform_identification.jinja

It contains the following fields:
Sure, here is a summary of the fields in the Jinja template along with their descriptions:

1. **file_name**: The name of the file being analyzed in the cross-platform test campaign.
2. **list_of_qasm_files**: A list of QASM files generated during the test campaign.
3. **list_of_error_messages**: A list of error messages encountered during the test campaign, including stack traces and involved functions.
4. **error_message_in_JSON**: A specific error message formatted in JSON that needs to be reported.

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

import re
from pathlib import Path
from typing import List, Dict, Any
import json
import click
from rich.console import Console
from jinja2 import Template

console = Console()


def load_jinja_template(template_path: Path) -> Template:
    """Loads the Jinja template."""
    with template_path.open() as file:
        return Template(file.read())


def load_json(file_path: Path) -> Dict[str, Any]:
    """Loads a JSON file."""
    with file_path.open() as file:
        return json.load(file)


def get_qasm_files(input_folder: Path, target_circuit: str) -> List[Path]:
    """Gets QASM files associated with the target circuit."""
    return list(input_folder.glob(f"{target_circuit}_qc_*.qasm"))


def get_error_messages(input_folder: Path, target_circuit: str) -> List[Dict[str, Any]]:
    """Retrieves error messages in JSON format."""
    target_files = list(input_folder.glob(f"{target_circuit}_*_error.json"))
    # keep only those that have f"{target_circuit}_[a-zA-Z0-9]*_error.json"
    # use regex
    filtered_files = [
        error_file
        for error_file in target_files
        if re.match(f"{target_circuit}_[a-zA-Z0-9]*_error.json", error_file.name)
    ]
    return [
        load_json(error_file) for error_file in filtered_files
    ]


def format_file_list(file_list: List[Path]) -> List[str]:
    """Formats a list of Path objects as strings.

    Using only filenames without the full path. And making them in a bullet list.
    """
    text = "\n".join([f"- {file.name}" for file in file_list])
    return text


def format_pretty_json(json_data: List[Dict[str, Any]]) -> str:
    """Formats JSON data in a pretty way."""
    text = "\n".join([json.dumps(data, indent=4) for data in json_data])
    return text


def save_triage_report(output_path: Path, content: str) -> None:
    """Saves the triage report as a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)


@click.command()
@click.option('--input_folder', required=True, type=click.Path(
    exists=True, file_okay=False),
    help='Path to the folder containing the input files.')
@click.option(
    '--target_circuit', required=True, type=str,
    help='Name of the target circuit.'
)
@click.option(
    '--target_error', required=True, type=str,
    help='Name of the error file to process.'
)
@click.option('--template_path', default="platform_identification.jinja",
              type=click.Path(exists=True, dir_okay=False),
              help='Path to the Jinja template for triage report generation.')
def main(
        input_folder: str, target_circuit: str, target_error: str,
        template_path: str) -> None:
    """
    CLI tool to generate a platform triage report for a bug in a quantum circuit cross-platform test.
    """
    input_folder_path = Path(input_folder)
    target_error_path = input_folder_path / target_error

    # remove ending .py from the target_circuit
    if target_circuit.endswith(".py"):
        target_circuit = target_circuit[:-3]

    console.log(f"Processing target circuit: {target_circuit}")
    console.log(f"Loading error file: {target_error_path}")

    # Load the Jinja template and error JSON
    template = load_jinja_template(template_path=Path(template_path))
    error_json = load_json(file_path=target_error_path)

    # Collect QASM files and error messages
    qasm_files = get_qasm_files(
        input_folder=input_folder_path, target_circuit=target_circuit)
    error_messages = get_error_messages(
        input_folder=input_folder_path, target_circuit=target_circuit)

    console.log(f"Found {len(qasm_files)} QASM files")
    console.log(f"Found {len(error_messages)} error files")

    # Generate triage report
    report_content = template.render(
        file_name=error_json.get("file_name"),
        list_of_qasm_files=format_file_list(qasm_files),
        list_of_error_messages=format_pretty_json(error_messages),
        error_message_in_JSON=format_pretty_json([error_json])
    )
    # remove bias of naming of often seein qiskit code
    report_content = report_content.replace(
        "qiskit_circuit", "quantum_program")

    # Define the output file name
    output_filename = f"{Path(target_error).stem}.triage.json"
    output_file_path = input_folder_path / output_filename

    # Save the triage report
    save_triage_report(output_path=output_file_path, content=report_content)

    console.log(f"Report generated and saved to: {output_file_path}")


if __name__ == "__main__":
    main()
