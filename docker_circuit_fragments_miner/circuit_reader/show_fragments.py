import click
from pathlib import Path
from typing import List, Optional
import pickle
from qiskit import QuantumCircuit
from rich.console import Console
from qiskit.qasm2 import dump

"""Script that reads all the pkl quantum circuits in the `circuit_fragment` folder and shows them.

They are qiskit cicuits.

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
# python /home/paltenmo/projects/crossplatform/data/show_fragments.py --dir_with_circuits_pkl /path/to/circuit_fragment

"""

console = Console()


def load_circuit(file_path: Path) -> QuantumCircuit:
    """Load a quantum circuit from a pickle file."""
    with file_path.open('rb') as file:
        return pickle.load(file)


def show_circuit(circuit: QuantumCircuit) -> None:
    """Display a quantum circuit using Qiskit visualization."""
    console.print(circuit.draw(output='text'))


def get_circuit_files(directory: Path) -> List[Path]:
    """Get all pickle files in the specified directory."""
    return list(directory.glob('*.pkl'))


def ensure_directory_exists(directory: Path) -> None:
    """Ensure that the specified directory exists."""
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)


@click.command()
@click.option('--dir_with_circuits_pkl', required=True, type=click.Path(
    exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help='Directory containing circuit fragments')
@click.option('--export_to_qasm', is_flag=True,
              help='Flag to export circuits to QASM')
@click.option('--dir_with_exported_qasm', type=click.Path(
    file_okay=False, dir_okay=True, path_type=Path),
    help='Directory to export QASM files (optional)')
def main(
        dir_with_circuits_pkl: Path, dir_with_exported_qasm: Optional[Path],
        export_to_qasm: bool) -> None:
    """Main function to load and show quantum circuits from pickle files."""
    ensure_directory_exists(dir_with_circuits_pkl)

    if export_to_qasm:
        if dir_with_exported_qasm is None:
            dir_with_exported_qasm = dir_with_circuits_pkl.parent / \
                f"{dir_with_circuits_pkl.name}_qasm"
        ensure_directory_exists(dir_with_exported_qasm)

    circuit_files = get_circuit_files(dir_with_circuits_pkl)
    if not circuit_files:
        console.print(
            f"No pickle files found in directory: {dir_with_circuits_pkl}",
            style="bold red")
        return

    for file_path in circuit_files:
        try:
            circuit = load_circuit(file_path)
            show_circuit(circuit)
            if export_to_qasm:
                qasm_path = dir_with_exported_qasm / f"{file_path.stem}.qasm"
                export_circuit_to_qasm(circuit, qasm_path)
        except (pickle.UnpicklingError, EOFError) as e:
            console.print(
                f"Error loading circuit from {file_path}: {e}",
                style="bold red")
        except Exception as e:
            console.print(
                f"Unexpected error with file {file_path}: {e}",
                style="bold red")
        finally:
            if export_to_qasm:
                # check if empty qasm_path and remove
                if qasm_path.exists() and qasm_path.stat().st_size == 0:
                    qasm_path.unlink()


def export_circuit_to_qasm(circuit: QuantumCircuit, qasm_path: Path) -> None:
    """Export a quantum circuit to a QASM file."""
    path = str(qasm_path)
    dump(circuit, path)


if __name__ == '__main__':
    main()
