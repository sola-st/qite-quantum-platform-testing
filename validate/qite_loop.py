import click
import random
from pathlib import Path
from typing import List
from rich.console import Console
from validate.qiskit_processor import (
    QiskitProcessor,
    QiskitChangeGateSetU3CX, QiskitOptimizerLevel2
)
from qite.transforms.pytket_transforms import list_pytket_transformers
from validate.pytket_processor import PytketProcessor
from validate.pennylane_processor import (
    PennyLaneProcessor,
    PennyLaneOptimizer
)
from validate.bqskit_processor import (
    BQSKitProcessor,
    BQSKitOptimizer
)

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


def apply_qite_algorithm(input_folder: str, number_of_rounds: int,
                         n_transform_iter: int) -> None:
    input_path = Path(input_folder)
    qasm_files = list(input_path.glob("*.qasm"))

    for round_num in range(number_of_rounds):
        console.log(f"Round {round_num + 1}/{number_of_rounds}")
        for qasm_file in qasm_files:
            process_qasm_file(qasm_file=qasm_file,
                              n_transform_iter=n_transform_iter)


def process_qasm_file(qasm_file: Path, n_transform_iter: int) -> None:
    console.log(f"QITE ({n_transform_iter}) -> {qasm_file}")
    metadata_folder = qasm_file.parent / "metadata"
    error_folder = qasm_file.parent / "error"
    metadata_folder.mkdir(exist_ok=True)
    error_folder.mkdir(exist_ok=True)

    processors = []

    # PLATFORM: QISKIT
    processor = QiskitProcessor(
        metadata_folder=metadata_folder,
        error_folder=error_folder,
        output_folder=qasm_file.parent
    )
    processor.add_transformer(QiskitChangeGateSetU3CX())
    processor.add_transformer(QiskitOptimizerLevel2())
    processors.append(processor)

    # PLATFORM: PYTKET
    processor = PytketProcessor(
        metadata_folder=metadata_folder,
        error_folder=error_folder,
        output_folder=qasm_file.parent
    )
    selected_transformers = (
        random.sample(list_pytket_transformers, n_transform_iter)
        if n_transform_iter < len(list_pytket_transformers)
        else list_pytket_transformers
    )
    for transformer in selected_transformers:
        processor.add_transformer(transformer)
    processors.append(processor)

    # # PLATFORM: PENNYLANE
    # processor = PennyLaneProcessor(
    #     metadata_folder=metadata_folder,
    #     error_folder=error_folder,
    #     output_folder=qasm_file.parent
    # )
    # processor.add_transformer(PennyLaneOptimizer())
    # processors.append(processor)

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
        final_path = processor.execute_qite_loop(str(qasm_file))
        # console.log(
        #     f"Processed {qasm_file} successfully. Output: {final_path}")
    except Exception as e:
        console.log(f"Error processing {qasm_file}: {e}")


@click.command()
@click.option('--input_folder', required=True, type=str,
              help='Folder containing the QASM programs.')
@click.option('--number_of_rounds', required=True, type=int,
              help='Number of rounds of the QITE algorithm.')
@click.option('--n_transform_iter', required=True, type=int,
              help='Number of transformation iterations for Pytket.')
def main(input_folder: str, number_of_rounds: int, n_transform_iter: int) -> None:
    apply_qite_algorithm(input_folder=input_folder,
                         number_of_rounds=number_of_rounds,
                         n_transform_iter=n_transform_iter)


if __name__ == "__main__":
    main()
