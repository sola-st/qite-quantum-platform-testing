from dataclasses import dataclass, field
from typing import List, Optional, Union
import random
import math
import random
from typing import List, Set
import click
from pathlib import Path
from rich.console import Console
import yaml
import json
import time
from uuid import uuid4
from qite.qite_loop import (
    lazy_imports
)
from qite.generators.qiskit_gates import (
    GATE_MAP,
    Gate
)

console = Console(color_system=None)


def create_random_gate(circuit_var: str, quantum_reg_var: str,
                       classical_reg_var: str, max_qubits: int, max_bits: int,
                       gate_set: Optional[List[str]] = None) -> Gate:
    gate_classes = [GATE_MAP[gate]
                    for gate in gate_set] if gate_set else list(GATE_MAP.values())
    gate_class = random.choice(gate_classes)
    return gate_class(
        circuit_var, quantum_reg_var, classical_reg_var, max_qubits, max_bits)


def generate_qiskit_code(
        circuit_var: str, quantum_reg_var: str, classical_reg_var: str,
        max_qubits: int, max_bits: int, num_statements: int,
        gate_set: Optional[List[str]] = None) -> List[str]:
    statements = []

    while len(statements) < num_statements:
        try:
            gate = create_random_gate(
                circuit_var, quantum_reg_var, classical_reg_var, max_qubits,
                max_bits, gate_set)
            statements.append(gate.instantiate())
        except ValueError:
            continue
    return statements


def get_latest_index(output_dir: Path, extensions: List[str]) -> int:
    latest_index = 0
    for ext in extensions:
        files = list(output_dir.glob(f"*.{ext}"))
        if files:
            indices = [int(f.stem.split("_")[0]) for f in files]
            latest_index = max(latest_index, max(indices))
    return latest_index


def generate_qiskit_programs(
        num_qubits: int, num_gates: int, seed: int, final_measure: bool,
        num_programs: int, output_dir: str, only_qregs: bool,
        gate_set: Optional[List[str]] = None, coverage_enabled: bool = False,
        template_coverage_file: Optional[str] = None, end_timestamp: int = -1):
    """Generate a given number of random Qiskit programs."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generation_output_path = output_path
    generation_time_path = output_path / "generation_time"
    generation_time_path.mkdir(parents=True, exist_ok=True)

    if not seed:
        seed = random.randint(0, 1000)
    # store the seed in the output folder
    with (generation_output_path / "_seed.txt").open("w") as f:
        f.write(str(seed))

    starting_index = get_latest_index(
        generation_output_path, extensions=["py", "qasm"]) + 1

    for i in range(starting_index, num_programs + starting_index):
        if end_timestamp != -1 and time.time() > end_timestamp:
            console.print("Time limit exceeded. Exiting.")
            exit(0)

        start_time = time.time()
        statements = generate_qiskit_code(
            circuit_var="qc", quantum_reg_var="qr", classical_reg_var="cr",
            max_qubits=num_qubits, max_bits=num_qubits,
            num_statements=num_gates, gate_set=gate_set)
        end_time = time.time()
        generation_time = end_time - start_time

        random_chars = uuid4().hex[:6]
        file_prefix = f"{str(i).zfill(7)}_{random_chars}"
        py_file_path = generation_output_path / f"{file_prefix}.py"
        time_file_path = generation_time_path / f"{file_prefix}.json"

        with py_file_path.open("w") as f:
            f.write(
                "from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit\n")
            f.write(f"qr = QuantumRegister({num_qubits}, 'qr')\n")
            if not only_qregs:
                f.write(f"cr = ClassicalRegister({num_qubits}, 'cr')\n")
                f.write(f"qc = QuantumCircuit(qr, cr)\n")
            else:
                f.write(f"qc = QuantumCircuit(qr)\n")
            f.write("\n".join(statements))
            if final_measure and not only_qregs:
                f.write("\nqc.measure(qr, cr)\n")

        with time_file_path.open("w") as f:
            json.dump({"generation_time": generation_time}, f)

        console.log(f"Generated {py_file_path} and {time_file_path}")


@click.command()
@click.option('--num_qubits', required=True, type=int,
              help='Number of qubits in the quantum circuit.')
@click.option('--num_gates', required=True, type=int,
              help='Number of gates in the quantum circuit.')
@click.option('--seed', type=int, default=None,
              help='Seed for the random number generator.')
@click.option('--final_measure', is_flag=True, default=False,
              help='Include a final measurement in the circuit.')
@click.option('--num_programs', required=True, type=int,
              help='Number of random programs to generate.')
@click.option('--output_dir', required=True, type=str,
              help='Output directory for the generated programs.')
@click.option('--config', type=click.Path(exists=True), default=None,
              help='Path to the config file (YAML).')
@click.option('--only_qregs', is_flag=True, default=False,
              help='Generate only quantum registers without classical registers.')
@click.option('--end_timestamp', type=int, default=-1,
              help='Exit with code 1 if current time exceeds this timestamp.')
def main(
        num_qubits: int, num_gates: int, seed: int, final_measure: bool,
        num_programs: int, output_dir: str, config: Optional[str],
        only_qregs: bool, end_timestamp: int):

    if end_timestamp != -1 and time.time() > end_timestamp:
        console.print("Time limit exceeded. Exiting.")
        exit(0)

    gate_set = None

    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        num_qubits = config_data.get('num_qubits', num_qubits)
        num_gates = config_data.get('num_gates', num_gates)
        seed = config_data.get('seed', seed)
        final_measure = config_data.get('final_measure', final_measure)
        num_programs = config_data.get('num_programs', num_programs)
        output_dir = config_data.get('output_dir', output_dir)
        gate_set = config_data.get('gate_set', gate_set)
        only_qregs = config_data.get('only_qregs', only_qregs)

    generate_qiskit_programs(
        num_qubits=num_qubits, num_gates=num_gates, seed=seed,
        final_measure=final_measure, num_programs=num_programs,
        output_dir=output_dir, only_qregs=only_qregs, gate_set=gate_set,
        end_timestamp=end_timestamp)


if __name__ == "__main__":
    main()
