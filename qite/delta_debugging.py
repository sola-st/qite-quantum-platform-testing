"""CLI for Delta Debugging on QASM Files"""

import json
import tempfile
import shutil
from pathlib import Path
import click
from qite.qite_replay import run_qite
from analysis_and_reporting.ddmin import DDMin


def load_error_json(error_json_path):
    with open(error_json_path, 'r') as f:
        return json.load(f)


def run_qite_wrapper(
        metadata_path, input_folder, output_debug_folder, clue: str = None):
    try:
        run_qite(
            metadata_path=metadata_path,
            input_folder=input_folder,
            output_debug_folder=output_debug_folder)
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
    clue = error_data.get('error', '')
    print(f"Error clue from metadata: {clue}")
    user_input = input(
        "Enter a new clue or press Enter to use the existing clue: ").strip()
    return user_input if user_input else clue


@click.command()
@click.option('--error_json', required=True, type=str,
              help='Path to the error JSON file.')
@click.option('--output_folder', required=False, type=str, default='.',
              help='Path to the output folder for storing debug files.')
@click.option('--input_folder', required=True, type=str,
              help='Path to the folder containing the QASM input file.')
def main(error_json, output_folder, input_folder):
    error_data = load_error_json(error_json)
    clue = ask_user_to_confirm_clue(error_data)
    input_qasm_filename = Path(error_data['input_qasm']).name
    input_qasm = Path(input_folder) / input_qasm_filename
    metadata_path = error_json

    tmpdir = Path(tempfile.mkdtemp())
    print(f"Temporary directory created at {tmpdir}")
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
            clue=clue)

    with open(input_qasm, 'r') as f:
        qasm_lines = f.readlines()

    minimized_qasm_lines = ddmin(test, qasm_lines)

    Path(output_folder).mkdir(parents=True, exist_ok=True)
    minimized_qasm_file = Path(output_folder) / input_qasm_filename
    with open(minimized_qasm_file, 'w') as f:
        f.writelines(minimized_qasm_lines)

    print(f"Minimized QASM file saved to {minimized_qasm_file}")
    print(f"Temporary directory retained at {tmpdir}")


if __name__ == '__main__':
    main()

# Example usage:
# Assuming the script is located at /home/paltenmo/projects/crossplatform/qite/delta_debugging.py
# and the error JSON file is located at /home/paltenmo/projects/crossplatform/qite/error.json

# Run the delta debugger using the following command:
# python -m qite.delta_debugging --error_json program_bank/v024/2025_02_05__17_57/error/0000012_109bc1_65b230_error.json --output_folder program_bank/v024/2025_02_05__17_57/minimized --input_folder program_bank/v024/2025_02_05__17_57
