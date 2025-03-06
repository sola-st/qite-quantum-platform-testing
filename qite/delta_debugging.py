"""CLI for Delta Debugging on QASM Files"""

import os
import json
import tempfile
import shutil
from functools import partial
from pathlib import Path
import click
from qite.qite_replay import run_qite
from qite.inspection.ddmin import DDMin
from rich.console import Console
from typing import List
from qite.convert_to_qasm import (
    get_qc_qiskit_from_file,
    convert_and_export_to_qasm
)


console = Console(color_system="auto")


def load_error_json(error_json_path):
    with open(error_json_path, 'r') as f:
        return json.load(f)


def run_qite_wrapper(
        metadata_path, input_folder, output_debug_folder, clue: str = None,
        print_intermediate_qasm: bool = False):
    try:
        run_qite(
            metadata_path=metadata_path,
            input_folder=input_folder,
            output_debug_folder=output_debug_folder,
            print_intermediate_qasm=print_intermediate_qasm)
        return True
    except Exception as e:
        print(f"Error: {e}")
        if clue and clue in str(e):
            return False
        print(f"Different error... (Expected: {clue})")
        return True


def ddmin(test, c):
    debugger = DDMin(c, test)
    return debugger.execute()


def ask_user_to_confirm_clue(error_data):
    """
    Ask the user to confirm or provide a new clue for the error.

    Parameters:
    error_data (dict): The error data loaded from the JSON file.

    Returns:
    str: The clue to be used for error identification.
    """
    clue = error_data.get('error', '')
    console.rule("[bold red]Error Clue Confirmation[/bold red]")
    console.print(
        f"[bold yellow]Error clue from metadata:[/bold yellow] {clue}")
    user_input = input(
        "Enter a new clue or press Enter to use the existing clue: ").strip()
    return user_input if user_input else clue


def run_conversion_wrapper(
        metadata_path: str, input_folder: Path, output_debug_folder: Path,
        clue: str = None, print_intermediate_qasm: bool = False) -> bool:
    try:
        input_py = str(Path(input_folder) / "test.py")
        qc = get_qc_qiskit_from_file(file_path=input_py)
        metadata = json.load(open(metadata_path, 'r'))
        platform = metadata.get('platform')
        _ = convert_and_export_to_qasm(
            qiskit_circ=qc,
            output_dir=str(output_debug_folder),
            circuit_input_file_name=Path(input_py).name,
            circuit_file_name=Path(input_py).stem + ".qasm",
            platform=platform,
            raise_any_exception=True)
        return True
    except Exception as e:
        print(f"Error: {e}")
        if clue and clue in str(e):
            return False
        print(f"Different error... (Expected: {clue})")
        return True


def test_qite(
        qasm_lines: List[str],
        tmpdir: Path, tmp_metadata_path: Path, clue: str) -> bool:
    tmp_qasm_file = tmpdir / "test.qasm"
    with open(tmp_qasm_file, 'w') as f:
        f.writelines(qasm_lines)
    return run_qite_wrapper(
        metadata_path=tmp_metadata_path,
        input_folder=tmpdir,
        output_debug_folder=tmpdir / "debug",
        clue=clue,
        print_intermediate_qasm=False)


def test_converter(
        py_lines: List[str],
        tmpdir: Path, tmp_metadata_path: Path, clue: str) -> bool:
    tmp_py_file = tmpdir / "test.py"

    with open(tmp_py_file, 'w') as f:
        f.writelines(py_lines)
    print("Running test on file content")
    print(open(tmp_py_file, 'r').read())
    print(f"in tmp folder {tmpdir}:")
    print(os.listdir(tmpdir))
    return run_conversion_wrapper(
        metadata_path=tmp_metadata_path,
        input_folder=tmpdir,
        output_debug_folder=tmpdir / "debug",
        clue=clue,
        print_intermediate_qasm=False)


@click.command()
@click.option('--error_json', required=True, type=str,
              help='Path to the error JSON file.')
@click.option('--output_folder', required=False, type=str, default=None,
              help='Path to the output folder for storing debug files.')
@click.option('--input_folder', required=False, type=str, default=None,
              help='Path to the folder containing the QASM input file.')
def main(error_json, output_folder, input_folder):
    error_data = load_error_json(error_json)

    if not output_folder and not input_folder:
        input_folder = Path(error_data['input_qasm']).parent
        output_folder = input_folder / "minimized"
        console.rule("[bold red]Folders Not Provided[/bold red]")
        console.print(
            f"[bold yellow]Input folder not provided. Using:[/bold yellow]\n"
            f"\t[bold green]INPUT  FOLDER:[/bold green] \t{input_folder}")
        console.print(
            f"[bold yellow]Output folder not provided. Using:[/bold yellow]\n"
            f"\t[bold green]OUTPUT FOLDER:[/bold green] \t{output_folder}")
        console.print(
            "[bold cyan]Press Enter to confirm or provide the correct paths as arguments "
            "using --output_folder and --input_folder options. Press Ctrl+C to exit.[/bold cyan]")
        input()

    clue = ask_user_to_confirm_clue(error_data)
    # input_qasm_filename = Path(error_data['input_qasm']).name
    # input_qasm = Path(input_folder) / input_qasm_filename
    metadata_path = error_json

    tmpdir = Path(tempfile.mkdtemp())
    console.rule("[bold blue]QASM Delta Debugging[/bold blue]")
    console.print(
        f"[bold green]Temporary directory created at:[/bold green] {tmpdir}")
    output_debug_folder = tmpdir / "debug"
    output_debug_folder.mkdir(parents=True, exist_ok=True)

    # Create a copy of the metadata content and store it in the tmp folder
    tmp_metadata_path = tmpdir / "metadata.json"
    with open(metadata_path, 'r') as f:
        metadata_content = json.load(f)
    if 'input_py' in metadata_content:
        # error in the converter
        input_file = Path(input_folder) / metadata_content['input_py']
        metadata_content['input_py'] = str(tmpdir / "test.py")
        test_func = test_converter
    else:
        # error in the QITE
        input_file = Path(input_folder) / metadata_content['input_qasm']
        metadata_content['input_qasm'] = str(tmpdir / "test.qasm")
        test_func = test_qite
    with open(tmp_metadata_path, 'w') as f:
        json.dump(metadata_content, f)

    with open(input_file, 'r') as f:
        file_to_min_lines = f.readlines()

    print("Files in tmp folder:")
    print(os.listdir(tmpdir))

    test_func_ddmin = partial(
        test_func, tmpdir=tmpdir, tmp_metadata_path=tmp_metadata_path,
        clue=clue)
    minimized_file_lines = ddmin(test_func_ddmin, file_to_min_lines)

    Path(output_folder).mkdir(parents=True, exist_ok=True)
    # minimized_qasm_file = Path(output_folder) / input_qasm_filename
    minimized_input_file = Path(output_folder) / Path(input_file).name
    with open(minimized_input_file, 'w') as f:
        f.writelines(minimized_file_lines)

    if 'input_py' in metadata_content:
        # error in the converter
        metadata_content['input_py'] = str(minimized_input_file)
    else:
        # error in the QITE
        metadata_content['input_qasm'] = str(minimized_input_file)
    with open(tmp_metadata_path, 'w') as f:
        json.dump(metadata_content, f)

    console.print(
        f"[bold green]Minimized file saved to:[/bold green] "
        f"{minimized_input_file}")
    console.print(
        f"[bold green]Temporary directory retained at:[/bold green] "
        f"{tmpdir}")

    console.rule("[bold blue]Minimized Content[/bold blue]")
    with open(minimized_input_file, 'r') as f:
        console.print(f.read())

    console.rule("[bold blue]Metadata Content[/bold blue]")
    console.print(json.dumps(metadata_content, indent=2))

    if "input_py" not in metadata_content:
        console.rule("[bold blue]Intermediate[/bold blue]")
        run_qite_wrapper(
            metadata_path=tmp_metadata_path,
            input_folder=output_folder,
            output_debug_folder=output_debug_folder,
            clue=clue,
            print_intermediate_qasm=True)


if __name__ == '__main__':
    main()

# Example usage:
# Assuming the script is located at /home/paltenmo/projects/crossplatform/qite/delta_debugging.py
# and the error JSON file is located at /home/paltenmo/projects/crossplatform/qite/error.json

# Run the delta debugger using the following command:
# python -m qite.delta_debugging --error_json program_bank/v024/2025_02_05__17_57/error/0000012_109bc1_65b230_error.json --output_folder program_bank/v024/2025_02_05__17_57/minimized --input_folder program_bank/v024/2025_02_05__17_57
