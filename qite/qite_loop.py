import click
import random
import yaml

from pathlib import Path
from typing import Optional, List
from rich.console import Console

from qite.processors.qiskit_processor import QiskitProcessor
from qite.processors.pytket_processor import PytketProcessor
from qite.processors.pennylane_processor import PennyLaneProcessor

from qite.transforms.pytket_transforms import list_pytket_transformers
from qite.transforms.pennylane_transforms import list_pennylane_transformers
from qite.transforms.qiskit_transforms import list_qiskit_transformers

from qite.base.primitives import Transformer

import signal
# from validate.bqskit_processor import (
#     BQSKitProcessor,
#     BQSKitOptimizer
# )

"""Cmd line that applies the QITE algorithm to all the generated QASM programs.

Arguments:
    --input_folder: str - Folder containing the QASM programs.
    --number_of_rounds: int - Number of rounds of the QITE algorithm.

At each round the algorithm performs the following steps:
1. Pick one PlatformProcessor at random.
2. Pick a QASM program at random.
3. Apply the PlatformProcessor to the QASM program.
4. Repeat the above steps for all the QASM programs.

The algorithm generates a new QASM program for each round and stores it in the output folder.

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


console = Console(color_system=None)


PLATFORMS = {
    "qiskit": {
        "processor_class": QiskitProcessor,
        "transformers": list_qiskit_transformers
    },
    "pytket": {
        "processor_class": PytketProcessor,
        "transformers": list_pytket_transformers
    },
    "pennylane": {
        "processor_class": PennyLaneProcessor,
        "transformers": list_pennylane_transformers
    }
}


def apply_qite_algorithm(
        input_folder: str, number_of_rounds: int, n_transform_iter: int,
        platforms_to_run: List[str]) -> None:
    input_path = Path(input_folder)
    qasm_files = sorted(list(input_path.glob("*.qasm")))
    qasm_to_process_this_round = qasm_files

    for round_num in range(number_of_rounds):
        console.log(f"Round {round_num + 1}/{number_of_rounds}")
        qasm_generated_this_round = []
        for qasm_file in qasm_to_process_this_round:
            new_qasm = process_qasm_file(
                qasm_file=qasm_file,
                n_transform_iter=n_transform_iter,
                platforms_to_run=platforms_to_run)
            if new_qasm:
                qasm_generated_this_round.append(new_qasm)
        qasm_to_process_this_round = sorted(qasm_generated_this_round)
        n_generated = len(qasm_to_process_this_round)
        console.log(f"Generated {n_generated} new QASM programs.")


def process_qasm_file(
        qasm_file: Path, n_transform_iter: int,
        platforms_to_run: List[str]) -> Optional[Path]:
    console.log(f"QITE ({n_transform_iter}) -> {qasm_file}")
    metadata_folder = qasm_file.parent / "metadata"
    error_folder = qasm_file.parent / "error"
    metadata_folder.mkdir(exist_ok=True)
    error_folder.mkdir(exist_ok=True)

    processors = []
    for platform in platforms_to_run:
        platform_info = PLATFORMS[platform]
        processor_class = platform_info["processor_class"]
        transformers: List[Transformer] = platform_info["transformers"]
        processor = processor_class(
            metadata_folder=metadata_folder,
            error_folder=error_folder,
            output_folder=qasm_file.parent
        )
        selected_transformers = (
            random.sample(transformers, n_transform_iter)
            if n_transform_iter < len(transformers)
            else transformers
        )
        for transformer in selected_transformers:
            processor.add_transformer(transformer)
        processors.append(processor)

    # # PLATFORM: BQSKIT
    # processor = BQSKitProcessor(
    #     metadata_folder=metadata_folder,
    #     error_folder=error_folder,
    #     output_folder=qasm_file.parent
    # )
    # processor.add_transformer(BQSKitOptimizer())
    # processors.append(processor)

    # randomly pick a processor
    processor = random.choice(processors)

    try:
        def handler(signum, frame):
            raise TimeoutError("Processing timed out")

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(10)  # Set the timeout to 60 seconds

        try:
            final_path = processor.execute_qite_loop(str(qasm_file))
            if final_path:
                return Path(final_path)
        finally:
            signal.alarm(0)  # Disable the alarm
        # console.log(
        #     f"Processed {qasm_file} successfully. Output: {final_path}")
    except Exception as e:
        console.log(f"Error processing {qasm_file}: {e}")
        # console.print_exception()
        # raise e

    return None


@click.command()
@click.option('--input_folder', required=True, type=str,
              help='Folder containing the QASM programs.')
@click.option('--number_of_rounds', required=True, type=int,
              help='Number of rounds of the QITE algorithm.')
@click.option('--n_transform_iter', required=True, type=int,
              help='Number of transformation iterations for Pytket.')
@click.option('--config', type=click.Path(exists=True), default=None,
              help='Path to the config file (YAML).')
def main(
        input_folder: str, number_of_rounds: int, n_transform_iter: int,
        config: Optional[str]) -> None:

    # by default run all platforms
    platforms_to_run = PLATFORMS.keys()

    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        input_folder = config_data.get('input_folder', input_folder)
        number_of_rounds = config_data.get(
            'number_of_rounds', number_of_rounds)
        n_transform_iter = config_data.get(
            'n_transform_iter', n_transform_iter)
        selected_platforms = config_data.get('platforms', [])
        platforms_to_run = [
            platform for platform in selected_platforms
            if platform in PLATFORMS.keys()
        ]

    apply_qite_algorithm(input_folder=input_folder,
                         number_of_rounds=number_of_rounds,
                         n_transform_iter=n_transform_iter,
                         platforms_to_run=platforms_to_run)


if __name__ == "__main__":
    main()
