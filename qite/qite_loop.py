import click
import random
import yaml

from pathlib import Path
from typing import Optional, List
from rich.console import Console


from qite.base.primitives import Transformer

import signal
import coverage
import multiprocessing
import time

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


def lazy_imports():
    # Imports are here so that they are counted in the round coverage
    from qite.processors.qiskit_processor import QiskitProcessor
    from qite.processors.pytket_processor import PytketProcessor
    from qite.processors.pennylane_processor import PennyLaneProcessor
    from qite.processors.bqskit_processor import BQSKitProcessor
    from qite.transforms.pytket_transforms import list_pytket_transformers
    from qite.transforms.pennylane_transforms import list_pennylane_transformers
    from qite.transforms.qiskit_transforms import list_qiskit_transformers
    from qite.transforms.bqskit_transforms import list_bqskit_transformers

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
        },
        "bqskit": {
            "processor_class": BQSKitProcessor,
            "transformers": list_bqskit_transformers
        }
    }
    return PLATFORMS


def apply_qite_algorithm(
        input_folder: str, number_of_rounds: int, n_transform_iter: int,
        platforms_to_run: List[str], template_coverage_file: str,
        program_id_range: Optional[List[int]], coverage_enabled: bool,
        coverage_every_round: bool,
        end_timestamp: int = -1) -> None:
    """Apply the QITE algorithm to the QASM programs."""
    input_path = Path(input_folder)
    qasm_files = sorted(list(input_path.glob("*.qasm")))

    if program_id_range:
        qasm_files = [qasm_file for qasm_file in qasm_files
                      if program_id_range[0] <=
                      int(qasm_file.stem.split('_')[0]) <=
                      program_id_range[1]]

    qasm_to_process_this_round = qasm_files
    cov = prepare_coverage_file(
        template_coverage_file=template_coverage_file,
        output_folder=Path(input_folder),
        platforms=platforms_to_run
    )
    cov.start()
    stats_file = input_path / "_qite_stats.txt"
    for round_num in range(number_of_rounds):
        # if coverage_enabled:
        #     output_folder_coverage_round = input_path / \
        #         f"cov_round_{round_num + 1}"
        #     cov = prepare_coverage_file(
        #         template_coverage_file=template_coverage_file,
        #         output_folder=output_folder_coverage_round,
        #         platforms=platforms_to_run
        #     )
        #     cov.start()
        console.log(f"Round {round_num + 1}/{number_of_rounds}")
        qasm_generated_this_round = []

        save_coverage_every_n_files = 50

        for i, qasm_file in enumerate(qasm_to_process_this_round):
            if end_timestamp != -1 and time.time() > end_timestamp:
                console.print("End timestamp reached, exiting")
                exit(0)
            new_qasm = process_qasm_file(
                qasm_file=qasm_file,
                n_transform_iter=n_transform_iter,
                platforms_to_run=platforms_to_run,
                round_number=round_num + 1)
            if new_qasm:
                qasm_generated_this_round.append(new_qasm)
            if coverage_enabled and i % save_coverage_every_n_files == 0:
                cov.save()
        qasm_to_process_this_round = sorted(qasm_generated_this_round)
        n_generated = len(qasm_to_process_this_round)
        console.log(f"Generated {n_generated} new QASM programs.")
        if coverage_enabled:
            #     cov.stop()
            cov.save()
        #     if coverage_every_round:
        #         cov.xml_report(
        #             outfile=str(output_folder_coverage_round / 'coverage.xml'),
        #             ignore_errors=True
        #         )

        with stats_file.open("a") as f:
            f.write(f'{{"round": {round_num + 1}, "n_program": {n_generated}}}\n')

    cov.stop()
    cov.save()


def process_qasm_file(
        qasm_file: Path, n_transform_iter: int,
        platforms_to_run: List[str], round_number: int) -> Optional[Path]:
    PLATFORMS = lazy_imports()
    console.log(
        f"QITE (R{str(round_number).zfill(3)}-T{str(n_transform_iter).zfill(3)}) -> {qasm_file}")
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
        processor.set_round(round_number)
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

    def process_with_timeout(qasm_file, processor, timeout):
        """Run processor.execute_qite_loop with a timeout."""
        result_queue = multiprocessing.Queue()

        def worker():
            try:
                final_path = processor.execute_qite_loop(str(qasm_file))
                result_queue.put(final_path)
            except Exception as e:
                result_queue.put(e)  # Put the exception in the queue

        process = multiprocessing.Process(target=worker)
        process.start()
        process.join(timeout)

        if process.is_alive():
            process.terminate()
            process.join()  # Ensure the process is cleaned up
            return TimeoutError("Processing timed out")

        result = result_queue.get()
        if isinstance(result, Exception):
            raise result  # Re-raise the exception
        return result

    try:
        timeout = 10  # seconds
        final_path = process_with_timeout(qasm_file, processor, timeout)
        if final_path:
            return Path(final_path)

    except TimeoutError as e:
        console.log(f"Error processing {qasm_file}: {e}")
    except Exception as e:
        console.log(f"Error processing {qasm_file}: {e}")
        # console.print_exception()
        # raise e

    return None


def prepare_coverage_file(
        template_coverage_file: str, output_folder: Path, platforms: List
        [str]) -> coverage.Coverage:
    """Prepare the coverage file for the QITE algorithm.

    It copies the template coverage file to the output folder and replaces
    the placeholders:
    - {{FOLDER_WITH_DATA_FILE}} with the output folder.
    - {{PLATFORMS_PACKAGES}} with the path to the platforms to cover.
    """
    with open(template_coverage_file, 'r') as file:
        content = file.read()

    content = content.replace('{{FOLDER_WITH_DATA_FILE}}', str(output_folder))
    platforms_packages = ','.join(platforms)
    content = content.replace('{{PLATFORMS_PACKAGES}}', platforms_packages)

    output_folder.mkdir(parents=True, exist_ok=True)
    coverage_file_path = output_folder / 'coverage.rc'
    with coverage_file_path.open('w') as file:
        file.write(content)

    # Initialize a Coverage object with the newly created .coveragerc configuration
    cov = coverage.Coverage(config_file=str(coverage_file_path))
    return cov


def post_process_coverage(
        input_folder: str, number_of_rounds: int,
        template_coverage_file: str, platforms_to_run: List[str]) -> None:
    """Create overall coverage report."""
    cumulative_coverage_folder = Path(input_folder) / 'cumulative_coverage'
    cumulative_coverage_folder.mkdir(parents=True, exist_ok=True)
    console.log("Processing coverage...")
    for i in range(1, number_of_rounds + 1):
        console.log(f"Processing round {i}")
        cov = prepare_coverage_file(
            template_coverage_file=template_coverage_file,
            output_folder=Path(input_folder),
            platforms=platforms_to_run
        )
        cov.combine(
            data_paths=[
                str(Path(input_folder) / f'cov_round_{j}')
                for j in range(1, i + 1)],
            keep=True)
        cov.xml_report(
            outfile=str(
                cumulative_coverage_folder /
                f'coverage_up_to_{i}.xml'),
            ignore_errors=True)

    # Create the final overall coverage report
    cov = prepare_coverage_file(
        template_coverage_file=template_coverage_file,
        output_folder=Path(input_folder),
        platforms=platforms_to_run
    )
    cov.combine(
        data_paths=[
            str(Path(input_folder) / f'cov_round_{i}')
            for i in range(1, number_of_rounds + 1)],
        keep=True)
    cov.xml_report(
        outfile=str(Path(input_folder) / 'coverage.xml'),
        ignore_errors=True
    )


@click.command()
@click.option('--input_folder', required=True, type=str,
              help='Folder containing the QASM programs.')
@click.option('--number_of_rounds', required=True, type=int,
              help='Number of rounds of the QITE algorithm.')
@click.option('--n_transform_iter', required=True, type=int,
              help='Number of transformation iterations for Pytket.')
@click.option('--config', type=click.Path(exists=True), default=None,
              help='Path to the config file (YAML).')
@click.option('--end_timestamp', type=int, default=-1,
              help='If set, exit when current time exceeds this timestamp.')
def main(
        input_folder: str, number_of_rounds: int, n_transform_iter: int,
        config: Optional[str], end_timestamp: int) -> None:

    if end_timestamp != -1 and time.time() > end_timestamp:
        console.print("End timestamp reached, exiting")
        exit(0)

    # by default run all platforms
    PLATFORMS = lazy_imports()
    platforms_to_run = PLATFORMS.keys()
    coverage_enabled = False

    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        input_folder = config_data.get('input_folder', input_folder)
        number_of_rounds = config_data.get(
            'number_of_rounds', number_of_rounds)
        n_transform_iter = config_data.get(
            'n_transform_iter', n_transform_iter)
        selected_platforms = config_data.get('platforms', [])
        program_id_range = config_data.get('program_id_range')
        platforms_to_run = [
            platform for platform in selected_platforms
            if platform in PLATFORMS.keys()
        ]
        template_coverage_file = config_data.get('template_coverage_file')
        coverage_enabled = config_data.get('coverage', False)
        coverage_every_round = config_data.get('coverage_every_round', False)
        end_timestamp = config_data.get('end_timestamp', end_timestamp)

        apply_qite_algorithm(input_folder=input_folder,
                             number_of_rounds=number_of_rounds,
                             n_transform_iter=n_transform_iter,
                             platforms_to_run=platforms_to_run,
                             template_coverage_file=template_coverage_file,
                             program_id_range=program_id_range,
                             coverage_enabled=coverage_enabled,
                             coverage_every_round=coverage_every_round,
                             end_timestamp=end_timestamp)

        # if coverage_enabled:
        #     post_process_coverage(
        #         input_folder=input_folder,
        #         number_of_rounds=number_of_rounds,
        #         template_coverage_file=template_coverage_file,
        #         platforms_to_run=platforms_to_run
        #     )

    else:
        print('No config file provided')


if __name__ == "__main__":
    main()
