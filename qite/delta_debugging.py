"""CLI for Delta Debugging on QASM Files"""

import json
import tempfile
import shutil
from pathlib import Path
import click
from qite.qite_replay import run_qite
from qite.inspection.ddmin import DDMin
from rich.console import Console


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
    input_qasm_filename = Path(error_data['input_qasm']).name
    input_qasm = Path(input_folder) / input_qasm_filename
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
    metadata_content['input_qasm'] = str(tmpdir / "test.qasm")
    with open(tmp_metadata_path, 'w') as f:
        json.dump(metadata_content, f)

    def test(qasm_lines):
        tmp_qasm_file = tmpdir / "test.qasm"
        with open(tmp_qasm_file, 'w') as f:
            f.writelines(qasm_lines)
        return run_qite_wrapper(
            metadata_path=tmp_metadata_path,
            input_folder=tmpdir,
            output_debug_folder=output_debug_folder,
            clue=clue,
            print_intermediate_qasm=False)

    with open(input_qasm, 'r') as f:
        qasm_lines = f.readlines()

    minimized_qasm_lines = ddmin(test, qasm_lines)

    Path(output_folder).mkdir(parents=True, exist_ok=True)
    minimized_qasm_file = Path(output_folder) / input_qasm_filename
    with open(minimized_qasm_file, 'w') as f:
        f.writelines(minimized_qasm_lines)

    metadata_content['input_qasm'] = str(minimized_qasm_file)
    with open(tmp_metadata_path, 'w') as f:
        json.dump(metadata_content, f)

    console.print(
        f"[bold green]Minimized QASM file saved to:[/bold green] "
        f"{minimized_qasm_file}")
    console.print(
        f"[bold green]Temporary directory retained at:[/bold green] "
        f"{tmpdir}")

    console.rule("[bold blue]Minimized QASM Content[/bold blue]")
    with open(minimized_qasm_file, 'r') as f:
        console.print(f.read())

    console.rule("[bold blue]Metadata Content[/bold blue]")
    console.print(json.dumps(metadata_content, indent=2))

    console.rule("[bold blue]Intermediate QASM[/bold blue]")
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
