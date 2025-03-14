import os
import click
from mqt import qcec
import json
import random
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import time
import signal
import threading
import multiprocessing
import yaml

logging.basicConfig(level=logging.INFO)


class ComparatorPicker:
    def pick(self, group: List[str],
             n_comparison: int = 5) -> List[Tuple[str, str]]:
        raise NotImplementedError


class MostDifferentQASMsComparatorPicker(ComparatorPicker):
    def pick(self, group: List[str],
             n_comparison: int = 5) -> List[Tuple[str, str]]:
        group.sort(
            key=lambda x: len(Path(x).read_text().splitlines()),
            reverse=True)
        return [(group[i], group[j]) for i in range(len(group))
                for j in range(i+1, len(group))][:n_comparison]


class RandomComparatorPicker(ComparatorPicker):
    def pick(self, group: List[str],
             n_comparison: int = 5) -> List[Tuple[str, str]]:
        return random.sample([(group[i], group[j])
                              for i in range(len(group))
                              for j in range(i + 1, len(group))],
                             n_comparison)


def get_metadata(file_path: str, metadata_folder: str) -> List[dict]:
    metadata_list = []
    for _ in range(10):
        if "_qite_" not in file_path:
            break
        metadata_path = Path(
            metadata_folder) / Path(file_path).with_suffix('.json').name
        if not metadata_path.exists():
            break
        with metadata_path.open('r') as f:
            metadata = json.load(f)
            metadata_list.append(metadata)
            file_path = metadata.get("input_qasm", "")
    return metadata_list


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException


signal.signal(signal.SIGALRM, timeout_handler)


def run_verification(path_qasm_a: str, path_qasm_b: str,
                     result_queue: multiprocessing.Queue):
    try:
        result = qcec.verify(
            str(path_qasm_a),
            str(path_qasm_b),
            transform_dynamic_circuit=True)
        result_queue.put({"equivalence": str(result.equivalence)})
    except Exception as e:
        result_queue.put({"equivalence": f"error: {e}"})


def process_files(input_folder: str, comparison_folder: str,
                  metadata_folder: str,
                  program_id_range: Optional[List[int]] = None,
                  end_timestamp: int = -1):
    input_path = Path(input_folder)
    comparison_path = Path(comparison_folder)
    metadata_path = Path(metadata_folder)

    if not comparison_path.exists():
        logging.info(f"Creating comparison folder at {comparison_path}")
        comparison_path.mkdir(parents=True)

    logging.info(f"Reading QASM files from {input_path}")
    qasm_files = [
        f for f in input_path.iterdir()
        if f.suffix == '.qasm' and f.is_file()]

    if program_id_range:
        qasm_files = [f for f in qasm_files if program_id_range[0]
                      <= int(f.stem[:7]) <= program_id_range[1]]

    groups = {}
    for file in qasm_files:
        prefix = file.stem[:7]
        if not prefix.isdigit():
            logging.warning(
                f"File {file} does not match the naming pattern and will be "
                "ignored.")
            continue
        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(str(file))

    for prefix, group in sorted(groups.items()):
        if end_timestamp != -1 and time.time() > end_timestamp:
            logging.info("Time limit exceeded. Exiting.")
            exit(0)

        logging.info(f"Processing group with prefix {prefix}")
        group.sort(key=lambda x: int(Path(x).stem[:7]))
        comparator = MostDifferentQASMsComparatorPicker()
        pairs = comparator.pick(group)

        for path_qasm_a, path_qasm_b in pairs:
            logging.info(f"Comparing {path_qasm_a} and {path_qasm_b}")
            start_time = time.time()
            result_queue = multiprocessing.Queue()
            verification_process = multiprocessing.Process(
                target=run_verification,
                args=(path_qasm_a, path_qasm_b, result_queue))
            verification_process.start()
            verification_process.join(timeout=5)  # Wait for 5 seconds

            if verification_process.is_alive():
                logging.error(
                    f"Comparison between {path_qasm_a} and {path_qasm_b} timed out.")
                verification_process.terminate()
                verification_process.join()
                result_dict = {"equivalence": "timeout"}
            else:
                result_dict = result_queue.get()

            end_time = time.time()
            comparator_time = end_time - start_time

            metadata_a = get_metadata(path_qasm_a, metadata_folder)
            metadata_b = get_metadata(path_qasm_b, metadata_folder)

            log_entry = {
                "qasms": [
                    {"filename": Path(path_qasm_a).name,
                     "provenance": metadata_a[0].get(
                        "platform", "generator")
                     if metadata_a else "generator",
                     "provenance_tree": metadata_a},
                    {"filename": Path(path_qasm_b).name,
                     "provenance": metadata_b[0].get(
                        "platform", "generator")
                     if metadata_b else "generator",
                     "provenance_tree": metadata_b}],
                "equivalence": result_dict['equivalence'],
                "comparator_time": comparator_time}

            output_path = comparison_path / \
                f"{Path(path_qasm_a).stem}_vs_{Path(path_qasm_b).stem}.json"
            logging.info(f"Writing comparison result to {output_path}")
            with output_path.open('w') as f:
                json.dump(log_entry, f, indent=4)


@click.command()
@click.option('--input_folder', required=True, type=click.Path(
    exists=True, file_okay=False, dir_okay=True))
@click.option('--comparison_folder', required=True, type=click.Path(
    file_okay=False, dir_okay=True))
@click.option('--metadata_folder', required=True, type=click.Path(
    exists=True, file_okay=False, dir_okay=True))
@click.option('--config', type=click.Path(exists=True), default=None,
              help='Path to the config file (YAML).')
@click.option('--program_id_range', type=(int, int), default=None,
              help='Range of program IDs to process (start, end).')
@click.option('--end_timestamp', type=int, default=-1,
              help='Exit if current time exceeds this timestamp.')
def main(
        input_folder: str, comparison_folder: str, metadata_folder: str,
        config: Optional[str], program_id_range: Optional[Tuple[int, int]],
        end_timestamp: int):
    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        input_folder = config_data.get('input_folder', input_folder)
        comparison_folder = config_data.get(
            'comparison_folder', comparison_folder)
        metadata_folder = config_data.get('metadata_folder', metadata_folder)
        program_id_range = config_data.get(
            'program_id_range', program_id_range)
        end_timestamp = config_data.get('end_timestamp', end_timestamp)

    if end_timestamp != -1 and time.time() > end_timestamp:
        logging.info("Time limit exceeded. Exiting.")
        exit(0)

    logging.info("Starting the process")
    process_files(input_folder, comparison_folder,
                  metadata_folder, program_id_range,
                  end_timestamp=end_timestamp)
    logging.info("Process completed")


if __name__ == '__main__':
    main()

# Example usage:
# python -m spot_divergences --input_folder /path/to/input_folder --comparison_folder /path/to/comparison_folder --metadata_folder /path/to/metadata_folder
