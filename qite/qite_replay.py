import click
from pathlib import Path
import shutil
import json
from rich.console import Console
from typing import Dict, Any, List

from qite.processors.qiskit_processor import QiskitProcessor
from qite.processors.pytket_processor import PytketProcessor
from qite.processors.pennylane_processor import PennyLaneProcessor
from qite.processors.platform_processor import PlatformProcessor
from qite.transform_ops import transform_lookup
from qite.base.primitives import Transformer
import logging

"""Script to reply the QITE algorithm given some metadata.

Args:
    --metadata_path: str. Path to the metadata file saved in JSON format.
    --input_input_folder: str. Path to the input folder containing the QASM files.
    --output_debug_folder: str. Path to the output folder where the debug files will be stored.

It uses the info in the metadata to reconstruct the appropriate platform processor and run again the QITE algorithm.

The relevant file is first copied to the debug folder and then the QITE algorithm is run again in that folder with the given metadata.


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
Make sure to add a function and call that function only in the main cli command.
The goal is to be able to import that function also from other files.
"""


console = Console(color_system="auto")


def load_metadata(metadata_path: Path) -> Dict[str, Any]:
    """Load metadata from a JSON file."""
    with open(metadata_path, 'r') as f:
        return json.load(f)


def copy_qasm_file(
        metadata: Dict[str, Any],
        input_folder: Path, output_folder: Path) -> Path:
    """Copy the QASM file to the output folder."""
    rel_path_qasm = metadata["input_qasm"]
    only_file_name = Path(rel_path_qasm).name
    qasm_file = Path(input_folder) / only_file_name
    output_qasm_file = output_folder / qasm_file.name
    if qasm_file == output_qasm_file:
        return output_qasm_file
    shutil.copy(qasm_file, output_qasm_file)
    return output_qasm_file


def pick_relevant_transformers(metadata: Dict[str, Any]) -> List[Transformer]:
    """Pick the relevant transformers based on metadata."""
    transformers = []
    for transformer_name in metadata["transformer_functions"]:
        transformer = transform_lookup.get(transformer_name)
        if transformer is None:
            raise ValueError(f"Unsupported transformer: {transformer_name}")
        transformers.append(transformer)
    return transformers


def setup_processor(
        metadata: Dict[str, Any],
        output_folder: Path) -> PlatformProcessor:
    """Set up the platform processor based on metadata."""
    processor_name = metadata["platform"]
    if processor_name == "qiskit":
        processor = QiskitProcessor(
            metadata_folder=output_folder,
            error_folder=output_folder,
            output_folder=output_folder
        )
    elif processor_name == "pytket":
        processor = PytketProcessor(
            metadata_folder=output_folder,
            error_folder=output_folder,
            output_folder=output_folder
        )
    elif processor_name == "pennylane":
        processor = PennyLaneProcessor(
            metadata_folder=output_folder,
            error_folder=output_folder,
            output_folder=output_folder
        )
    else:
        raise ValueError(f"Unsupported platform: {processor_name}")

    transformers = pick_relevant_transformers(metadata)
    for transformer in transformers:
        processor.add_transformer(transformer)
    return processor


def run_qite(
        metadata_path: str, input_folder: str, output_debug_folder: str,
        print_intermediate_qasm: bool = False):
    """Run the QITE algorithm based on metadata."""
    metadata_path = Path(metadata_path)
    input_folder = Path(input_folder)
    output_debug_folder = Path(output_debug_folder)
    output_debug_folder.mkdir(parents=True, exist_ok=True)
    metadata = load_metadata(metadata_path=metadata_path)
    qasm_file = copy_qasm_file(
        metadata=metadata,
        input_folder=input_folder,
        output_folder=output_debug_folder
    )
    processor = setup_processor(
        metadata=metadata,
        output_folder=output_debug_folder
    )
    processor.execute_qite_loop(
        qasm_file=str(qasm_file),
        raise_any_exception=True,
        print_intermediate_qasm=print_intermediate_qasm,
        predefined_output_filename=Path(metadata["output_qasm"]).name
    )


def run_qite_chain(
        metadata_paths: List[str],
        input_folder: str, output_debug_folder: str,
        print_intermediate_qasm: bool = False):
    """Run the QITE algorithm based on a chain of metadata.

    Each metadata contains the "input_qasm" and the "output_qasm"
    which should be used as output file.
    """
    logger = logging.getLogger(__name__)
    for metadata_path in metadata_paths:
        logger.info(f"Running QITE with metadata: {metadata_path}")
        run_qite(
            metadata_path=metadata_path,
            input_folder=input_folder,
            output_debug_folder=output_debug_folder,
            print_intermediate_qasm=print_intermediate_qasm
        )


@click.command()
@click.option('--metadata_path', required=True, type=str,
              help='Path to the metadata file saved in JSON format.')
@click.option('--input_folder', required=True, type=str,
              help='Path to the input folder containing the QASM files.')
@click.option('--output_debug_folder', required=True, type=str,
              help='Path to the output folder where the debug files will be stored.')
def main(metadata_path: str, input_folder: str, output_debug_folder: str):
    run_qite(
        metadata_path=metadata_path,
        input_folder=input_folder,
        output_debug_folder=output_debug_folder
    )


if __name__ == '__main__':
    main()

# Example usage:
# python -m qite.qite_replay --metadata_path program_bank/v024/run006/error/0000005_33b7d0_50615d_error.json --input_folder program_bank/v024/run006 --output_debug_folder program_bank/v024/run006/debug
