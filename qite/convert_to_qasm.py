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
Here is a revised task description based on your additional requirements:

---

### Task Description: Implement a Command Line Interface for QASM File Processing

**Objective:**
Develop a command line interface (CLI) script that scans a given input folder for Python files, executes the code to capture the value of specific variables, converts the QASM code to specified platforms (default: Qiskit, Pennylane, Pytket), and exports the converted code to new QASM files in the same folder with updated extensions.

**Requirements:**

1. **Input Handling:**
    - The script should accept an `--input_folder` argument specifying the folder containing Python files.
    - The script should focus only on the first-level Python files in the input folder and ignore subfolders.
    - The Python files should be sorted alphabetically before processing.

2. **Execution:**
    - The script should execute the Python files using `exec` to capture the value of specific variables (e.g., `qc`).
    - Ensure the execution environment is properly set up for running the Python code.

3. **Conversion:**
    - The script should convert the captured QASM code to specified platforms (default: Qiskit, Pennylane, Pytket).
    - Use appropriate libraries or tools for the conversion process.
    - Ensure the converted code adheres to the standards and formats required by the target platforms.

4. **Output Handling:**
    - The script should export the converted code to new QASM files in the same folder as the input files.
    - The output QASM files should have the same name as the input files but with updated extensions to reflect the target platform.

5. **Error Handling and Logging:**
    - Implement error handling to manage issues during execution and conversion.
    - Provide logging to capture the process details, including any errors or warnings.

6. **Command Line Interface:**
    - The script should support the following command line arguments:
      - `--input_folder`: Path to the folder containing Python files.
      - `--platforms`: List of target platforms for conversion (default: `qiskit`, `pennylane`, `pytket`).
    - Provide default values for optional arguments.
    - Display progress updates and feedback to the user during execution.


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
