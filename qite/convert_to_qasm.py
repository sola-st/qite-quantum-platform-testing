import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from qiskit import QuantumCircuit
from rich.console import Console
import click
from qite.processors.platform_processor import PlatformProcessor
from qite.qite_loop import lazy_imports, prepare_coverage_file
import yaml
import random
import time
import json

"""
# Example usage:
# python -m qite.convert_to_qasm --input_folder /path/to/input/folder --platforms qiskit,pennylane,pytket
"""
console = Console(color_system=None)


def get_qc_qiskit_from_file(
        file_path: str, var_name: str = "qc") -> QuantumCircuit:
    """Execute the code in the file and return the QuantumCircuit object."""
    namespace = {}
    with open(file_path, "r") as f:
        exec(f.read(), namespace)
    return namespace[var_name]


def convert_and_export_to_qasm(
        qiskit_circ: QuantumCircuit,
        output_dir: str,
        circuit_input_file_name: str,
        circuit_file_name: str,
        platform: str,
        raise_any_exception: bool = False
) -> str:
    """Convert a Qiskit circuit to QASM using different platforms and export it."""
    output_path = Path(output_dir)
    converter_error_path = output_path / "converter_error"
    converter_error_path.mkdir(parents=True, exist_ok=True)

    output_metadata_path = output_path / "converter_metadata"
    output_metadata_path.mkdir(parents=True, exist_ok=True)

    platforms = lazy_imports()
    platform_class = platforms[platform]["processor_class"]
    platform_processor = platform_class(
        metadata_folder=str(output_metadata_path),
        error_folder=str(converter_error_path),
        output_folder=str(output_path))
    platform_processor.set_round(0)
    exported_path = platform_processor.execute_conversion_loop(
        circuit_file_name=circuit_input_file_name,
        qiskit_circ=qiskit_circ,
        predefined_output_filename=circuit_file_name,
        raise_any_exception=raise_any_exception
    )

    return str(exported_path)


def override_last_line(file_path: Path, new_last_line: str) -> None:
    """Override the last line of the file with the new_last_line."""
    lines = file_path.read_text().splitlines()
    if lines:
        lines[-1] = new_last_line
    else:
        lines.append(new_last_line)
    file_path.write_text("\n".join(lines) + "\n")


def process_files(
        input_folder: Path, platforms: List[str],
        program_id_range: Optional[List[int]], coverage_enabled: bool,
        template_coverage_file: Optional[str],
        end_timestamp: int = -1
) -> None:
    """Process each Python file in the input folder."""
    files_to_process = [
        file_path for file_path in sorted(input_folder.glob("*.py"))
        if not program_id_range or (
            program_id_range[0] <= int(file_path.stem.split('_')[0]) <= program_id_range[1]
        )
    ]

    if coverage_enabled and template_coverage_file:
        output_path = Path(input_folder)
        cov = prepare_coverage_file(
            template_coverage_file=template_coverage_file,
            output_folder=output_path,
            platforms=platforms
        )
        cov.start()

    generated_qasm_files = []
    for file_path in files_to_process:
        try:
            if end_timestamp != -1 and time.time() > end_timestamp:
                console.print("Time limit exceeded. Exiting.")
                break
            qc = get_qc_qiskit_from_file(file_path=str(file_path))
            # pick random platform
            platform = random.choice(platforms)
            print(f"Processing {file_path} for {platform}")
            export_path = convert_and_export_to_qasm(
                qiskit_circ=qc,
                output_dir=str(input_folder),
                circuit_input_file_name=file_path.name,
                circuit_file_name=file_path.stem + ".qasm",
                platform=platform)
            console.log(f"Exported {export_path}")
            if export_path:
                generated_qasm_files.append(Path(export_path).name)
        except Exception as e:
            console.log(f"Error processing {file_path}: {e}")

    stats_file = input_folder / "_qite_stats.jsonl"
    # read last line
    if stats_file.exists():
        last_line = stats_file.read_text().splitlines()[-1]
        print(last_line)
        last_run = json.loads(last_line)
        if last_run.get("round") == 0:
            last_run["generated_qasm_files"] = last_run["generated_qasm_files"] + generated_qasm_files
            last_run["n_program"] = len(last_run["generated_qasm_files"])
        # overwrite the last line
        override_last_line(stats_file, json.dumps(last_run))

    if coverage_enabled and template_coverage_file:
        output_path = Path(input_folder)
        cov.stop()
        cov.save()
        cov.xml_report(
            outfile=str(output_path / 'converter_coverage.xml'),
            ignore_errors=True
        )


@click.command()
@click.option(
    '--input_folder', required=True, type=click.Path(exists=True),
    help='Path to the folder containing Python files.')
@click.option('--config', type=click.Path(exists=True), default=None,
              help='Path to the config file (YAML).')
@click.option('--end_timestamp', type=int, default=-1,
              help='Exit if current time exceeds this timestamp.')
def main(input_folder: str, config: Optional[str], end_timestamp: int) -> None:
    """Main function to handle CLI arguments and initiate processing."""
    if end_timestamp != -1 and time.time() > end_timestamp:
        console.print("Time limit exceeded. Exiting.")
        exit(0)

    input_folder_path = Path(input_folder)
    program_id_range = None
    coverage_enabled = False
    template_coverage_file = None

    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        input_folder_path = Path(config_data.get('input_folder', input_folder))
        platform_list = config_data.get('platforms')
        program_id_range = config_data.get(
            'program_id_range', program_id_range)
        coverage_enabled = config_data.get('coverage', coverage_enabled)
        template_coverage_file = config_data.get(
            'template_coverage_file', template_coverage_file)

    process_files(
        input_folder=input_folder_path, platforms=platform_list,
        program_id_range=program_id_range, coverage_enabled=coverage_enabled,
        template_coverage_file=template_coverage_file,
        end_timestamp=end_timestamp)


if __name__ == "__main__":
    main()
