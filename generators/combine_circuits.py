import click
from pathlib import Path
import pickle
from qiskit import QuantumCircuit
from rich.console import Console
from typing import List
import random
from qiskit.qasm2 import dump

"""Script to combine quantum circuits using a generator.

This script reads quantum circuits from pickled files in the input folder,
combines them into a single quantum circuit, and saves the result to an output file.

Arguments:
- --input_folder (str): Path to the folder containing the pickled quantum circuits.
- --output_folder (str): Path to the output file where the combined quantum circuit will be saved.
- --seed (int): Seed for the random selection of circuits to combine.

Implementation Steps:
1. Read the pkl files from the input folder.
    When more than one is found, sample two of them.
2. Read the files and load the circuits.
2. Print their register name, size, and circuit name (if any).
3. Sequentially stitch the two circuits together.
4. Export the circuit to QASM2 format, in the output folder.
    (The name of the output file is the concatenation of the input files
    with the extension .qasm)

# Example usage:
# python -m generators.combine_circuits --input_folder tests/artifacts/pickled_quantum_circuits --output_folder program_bank/circuit_stitching --seed 42

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

"""


def read_circuit_files(input_folder: Path) -> List[Path]:
    """Read all pkl files from the input folder."""
    return list(input_folder.glob("*.pkl"))


def load_circuit(file_path: Path) -> QuantumCircuit:
    """Load a quantum circuit from a pkl file."""
    with file_path.open("rb") as f:
        return pickle.load(f)


def print_circuit_info(circuit: QuantumCircuit) -> None:
    """Print the register name, size, and circuit name.

    Consider both classical and quantum registers.
    """
    console = Console()
    for register in circuit.qregs + circuit.cregs:
        console.print(f"Register: {register.name}, Size: {register.size}")
    console.print(f"Circuit name: {circuit.name if circuit.name else 'N/A'}")


def combine_circuits(
        circuit1: QuantumCircuit, circuit2: QuantumCircuit) -> QuantumCircuit:
    """
    Combine two quantum circuits sequentially into a single circuit.

    This function takes two quantum circuits and combines them into a new circuit.
    If the circuits have different register sizes, the combined circuit will have
    the maximum size of quantum and classical registers from the two input circuits.
    The input circuits are appended sequentially to the combined circuit.

    Args:
        circuit1 (QuantumCircuit): The first quantum circuit to combine.
        circuit2 (QuantumCircuit): The second quantum circuit to combine.

    Returns:
        QuantumCircuit: A new quantum circuit that combines the input circuits.
    """
    combined_qc = QuantumCircuit(
        max(circuit1.num_qubits, circuit2.num_qubits),
        max(circuit1.num_clbits, circuit2.num_clbits)
    )
    circuit1 = assign_random_params(circuit1)
    circuit2 = assign_random_params(circuit2)
    combined_qc.compose(
        circuit1,
        range(circuit1.num_qubits),
        range(circuit1.num_clbits),
        inplace=True)
    combined_qc.compose(
        circuit2,
        range(circuit2.num_qubits),
        range(circuit2.num_clbits),
        inplace=True
    )
    return combined_qc


def assign_random_params(circuit: QuantumCircuit) -> QuantumCircuit:
    """Assign random values to all unbound parameters in the circuit."""
    unbound_params = get_all_unbound_params(circuit)
    for param in unbound_params:
        circuit = circuit.assign_parameters(
            {param: random.uniform(0, 2 * 3.14159)})
    return circuit


def get_all_unbound_params(circuit: QuantumCircuit) -> List[str]:
    """Get all unbound parameters in the circuit."""
    try:
        return list(circuit.parameters)
    except Exception:
        pass
    return list(circuit.decompose().parameters)


def save_circuit(circuit: QuantumCircuit, output_path: Path) -> None:
    """Save the combined circuit to a QASM2 file."""
    print(f"Saving combined circuit to {output_path}")
    print(circuit.draw())
    dump(circuit, str(output_path))


@click.command()
@click.option("--input_folder", required=True, type=click.Path(
    exists=True, file_okay=False, path_type=Path))
@click.option("--output_folder", required=True, type=click.Path(file_okay=False, path_type=Path))
@click.option("--seed", required=True, type=int)
def main(input_folder: Path, output_folder: Path, seed: int) -> None:
    """Main function to combine quantum circuits."""
    random.seed(seed)
    console = Console()

    input_files = read_circuit_files(input_folder)
    if len(input_files) < 2:
        console.print("Not enough circuits to combine.")
        return

    selected_files = random.sample(input_files, 2)
    circuits = [load_circuit(file) for file in selected_files]

    for circuit in circuits:
        print_circuit_info(circuit)

    combined_circuit = combine_circuits(circuits[0], circuits[1])

    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / \
        f"{selected_files[0].stem}_{selected_files[1].stem}.qasm"
    save_circuit(combined_circuit, output_file)

    console.print(f"Combined circuit saved to {output_file}")


if __name__ == "__main__":
    main()
