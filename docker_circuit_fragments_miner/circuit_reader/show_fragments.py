import click
from pathlib import Path
from typing import List
import pickle
from qiskit import QuantumCircuit
from rich.console import Console

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
def main(dir_with_circuits_pkl: Path) -> None:
    """Main function to load and show quantum circuits from pickle files."""
    ensure_directory_exists(dir_with_circuits_pkl)
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
        except (pickle.UnpicklingError, EOFError) as e:
            console.print(
                f"Error loading circuit from {file_path}: {e}",
                style="bold red")
        except Exception as e:
            console.print(
                f"Unexpected error with file {file_path}: {e}",
                style="bold red")


if __name__ == '__main__':
    main()
