import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from qiskit import QuantumCircuit
from rich.console import Console
import click
from qite.processors.platform_processor import PlatformProcessor
from qite.qite_loop import lazy_imports
import yaml
import random

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
        platform: str) -> str:
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
        raise_any_exception=False
    )
    return str(exported_path)


def process_files(
        input_folder: Path, platforms: List[str],
        program_id_range: Optional[List[int]]) -> None:
    """Process each Python file in the input folder."""
    files_to_process = [
        file_path for file_path in sorted(input_folder.glob("*.py"))
        if not program_id_range or (
            program_id_range[0] <= int(file_path.stem.split('_')[0]) <= program_id_range[1]
        )
    ]
    for file_path in files_to_process:
        try:
            qc = get_qc_qiskit_from_file(file_path=str(file_path))
            # pick random platorm
            platform = random.choice(platforms)
            print(f"Processing {file_path} for {platform}")
            export_path = convert_and_export_to_qasm(
                qiskit_circ=qc,
                output_dir=str(input_folder),
                circuit_input_file_name=file_path.name,
                circuit_file_name=file_path.stem + ".qasm",
                platform=platform)
            console.log(f"Exported {export_path}")
        except Exception as e:
            console.log(f"Error processing {file_path}: {e}")


@click.command()
@click.option(
    '--input_folder', required=True, type=click.Path(exists=True),
    help='Path to the folder containing Python files.')
@click.option('--config', type=click.Path(exists=True), default=None,
              help='Path to the config file (YAML).')
def main(input_folder: str, config: Optional[str]) -> None:
    """Main function to handle CLI arguments and initiate processing."""
    input_folder_path = Path(input_folder)
    program_id_range = None

    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        input_folder_path = Path(config_data.get('input_folder', input_folder))
        platform_list = config_data.get('platforms')
        program_id_range = config_data.get(
            'program_id_range', program_id_range)

    process_files(
        input_folder=input_folder_path, platforms=platform_list,
        program_id_range=program_id_range)


if __name__ == "__main__":
    main()
