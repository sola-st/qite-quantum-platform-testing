import click
from pathlib import Path
from typing import List, Dict
from rich.console import Console
import random
import shutil
import json
from datetime import datetime

"""Script to sample json data to label in label studio.

It iterates over all the json file in a folder (recursively) and selects a
random sample of them to label. The sample is saved in a new folder.

The loading is done in dask to use lazy loading and avoid loading all the data
in memory.

Arguments:
--input_folder: str, path to the folder containing the json files.
    (default: program_bank/v005)
    multiple input folders can be provided.
--output_folder: str, path to the folder where the sample will be saved.
    The folder will be created if it does not exist.
    (default: data/labeling/sample)

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

# Example usage:
# python -m labeling.sample_crashes --input_folder program_bank/v005 --output_folder data/labeling/sample
"""

import dask.bag as db

console = Console()


def ensure_output_folder_exists(output_folder: Path) -> None:
    """Ensure the output folder exists."""
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)


def get_json_files(input_folders: List[Path]) -> List[Path]:
    """Get all json files from input folders."""
    json_files = []
    for folder in input_folders:
        json_files.extend(folder.rglob('*.json'))
    return json_files


def sample_files(files: List[Path], sample_size: int) -> List[Path]:
    """Sample a subset of files."""
    return random.sample(files, sample_size)


def get_content_between_tags(
        content: str, start_tag: str, end_tag: str) -> str:
    """Get the content between two tags."""
    start_index = content.find(start_tag)
    if start_index == -1:
        return ""
    start_index += len(start_tag)
    end_index = content.find(end_tag, start_index)
    if end_index == -1:
        return ""
    return content[start_index:end_index]


def get_file_content(path_json_error: Path, python_filename: str) -> Dict[str, str]:
    """Get the content of a file.

    We assume that the json error is stored in the same folder of the python file.
    """
    python_file = path_json_error.parent / python_filename
    qasm_compressed = get_compressed_QASM_files(path_json_error)
    with python_file.open('r') as f:
        python_content = f.read()
        return {
            'original_filepath_python': str(python_file),
            'content_python_file': python_content,
            'content_gates': get_content_between_tags(
                python_content,
                start_tag="<START_GATES>",
                end_tag="<END_GATES>").strip(),
            'qasm_compressed': qasm_compressed
        }


def get_all_related_QASM_files(path_json_error: Path) -> List[Path]:
    """Get all related QASM files."""
    # remove the extension from the filename
    filename = path_json_error.stem
    # given qiskit_circuit_32q_10g_9183_bb397f_73e91e_error
    # remove the last part to get qiskit_circuit_32q_10g_9183_bb397f
    filename = "_".join(filename.split("_")[:-2])
    # search for all files starting with the filename
    return list(path_json_error.parent.rglob(f'{filename}*.qasm'))


def get_compressed_QASM_files(path_json_error: Path) -> List[Path]:
    all_qasm_files = get_all_related_QASM_files(path_json_error)
    all_file_content = [(file, file.read_text()) for file in all_qasm_files]
    qasm_string = ""
    for file, content in all_file_content:
        qasm_string += f"// {file}\n{content}\n"
    return qasm_string


def copy_files_to_output(
        sampled_files: List[Path],
        output_folder: Path) -> None:
    """Copy sampled files to the output folder and add filepath field."""
    for file in sampled_files:
        with file.open('r') as f:
            data = json.load(f)
        data['original_filepath_error'] = str(file)
        content_info = get_file_content(
            path_json_error=file,
            python_filename=data['current_file']
        )
        # add the content of the python file to the json
        data.update(content_info)
        new_file_path = output_folder / file.name
        with new_file_path.open('w') as f:
            json.dump({
                "data": data
            }, f, indent=4)


@ click.command()
@ click.option('--input_folder', multiple=True, type=click.Path(
    exists=True, file_okay=False, path_type=Path),
    required=True, default=['program_bank/v005'])
@ click.option('--output_folder', type=click.Path(
    file_okay=False, path_type=Path),
    required=True, default='data/labeling/sample')
@ click.option('--sample_size', type=int, required=True, default=10)
@ click.option('--random_seed', type=int, required=True, default=42)
def main(
        input_folder: List[Path],
        output_folder: Path, sample_size: int, random_seed: int) -> None:
    """Main function to sample json data for labeling."""
    random.seed(random_seed)
    # add the date and time to the output folder _%YY_%mm_%dd__%H_%M
    time_suffix = datetime.now().strftime("_%Y_%m_%d__%H_%M")
    output_folder = output_folder / \
        f"sample_n{sample_size}_s{random_seed}_{time_suffix}"
    ensure_output_folder_exists(output_folder)
    json_files = get_json_files(input_folder)
    sampled_files = sample_files(json_files, sample_size)
    copy_files_to_output(sampled_files, output_folder)
    console.log(f"Sampled {len(sampled_files)} files to {output_folder}")


if __name__ == '__main__':
    main()
