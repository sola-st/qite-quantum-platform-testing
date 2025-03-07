from dataclasses import dataclass
from typing import List, Optional
import random
import math
import click
from pathlib import Path
from rich.console import Console
from uuid import uuid4
from datetime import datetime
import yaml
import math
from typing import Callable
import json
import time

from qite.generators.qasm_gates import GATE_MAP, Gate

# qasm_code_gen.py


class QASMCodeGenerator:
    def __init__(
            self, num_qubits: int, seed: Optional[int] = None,
            gate_set: Optional[List[str]] = None, only_qregs: bool = False):
        self.num_qubits = num_qubits
        self.qasm_code = []
        self.only_qregs = only_qregs
        self.available_gates = GATE_MAP
        self.gates = (
            [self.available_gates[gate] for gate in gate_set]
            if gate_set else list(self.available_gates.values())
        )

        if seed is not None:
            random.seed(seed)

    def reset_memory(self):
        self.qasm_code = []

    def generate_header(self):
        self.qasm_code.append("OPENQASM 2.0;")
        self.qasm_code.append('include "qelib1.inc";')

    def generate_registers(self):
        self.qasm_code.append(f"qreg q[{self.num_qubits}];")
        if not self.only_qregs:
            self.qasm_code.append(f"creg c[{self.num_qubits}];")

    def add_gate(self, gate: Gate):
        self.qasm_code.append(gate.to_qasm("q", self.num_qubits))

    def add_random_gate(self):
        gate = random.choice(self.gates)
        self.add_gate(gate)

    def generate_random_qasm(self, num_gates, final_measure=True):
        self.generate_header()
        self.generate_registers()
        for _ in range(num_gates):
            self.add_random_gate()
        if final_measure and not self.only_qregs:
            self.qasm_code.append("measure q -> c;")

    def get_qasm_code(self):
        return "\n".join(self.qasm_code)


"""
Cmd line that generates a given number of random QASM program.

Arguments:
    --num_qubits: int - Number of qubits in the quantum circuit.
    --num_gates: int - Number of gates in the quantum circuit.
    --seed: int - Seed for the random number generator.
    --final_measure: bool - Include a final measurement in the circuit.
    --num_programs: int - Number of random programs to generate.
    --output_dir: str - Output directory for the generated programs.

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

console = Console()


def get_latest_index(output_dir: Path, extensions: List[str]) -> int:
    latest_index = 0
    for ext in extensions:
        files = list(output_dir.glob(f"*.{ext}"))
        if files:
            indices = [int(f.stem.split("_")[0]) for f in files]
            latest_index = max(latest_index, max(indices))
    return latest_index


def generate_qasm_programs(
        num_qubits: int, num_gates: int, seed: int, final_measure: bool,
        num_programs: int, output_dir: str, only_qregs: bool,
        gate_set: Optional[List[str]] = None, end_timestamp: int = -1):
    """Generate a given number of random QASM programs.

    Each program is stored as .qasm and has the name
    {i}.zfill(7)_{uuid4()}.qasm.
    The files are stored in a sub-folder with the current name:
    2025_01_29__16_43__qasm (date of the start of execution)
    fixed at the start.
    """
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
    generator = QASMCodeGenerator(
        num_qubits=num_qubits, seed=seed, gate_set=gate_set,
        only_qregs=only_qregs)

    starting_index = get_latest_index(
        generation_output_path, extensions=["py", "qasm"]) + 1

    for i in range(starting_index, num_programs + starting_index):
        if end_timestamp != -1 and time.time() > end_timestamp:
            console.print("Time limit exceeded. Exiting.")
            exit(0)

        start_time = time.time()
        generator.generate_random_qasm(
            num_gates=num_gates, final_measure=final_measure)
        qasm_code = generator.get_qasm_code()
        generator.reset_memory()
        end_time = time.time()
        generation_time = end_time - start_time

        random_chars = uuid4().hex[:6]
        file_prefix = f"{str(i).zfill(7)}_{random_chars}"
        qasm_file_path = generation_output_path / f"{file_prefix}.qasm"
        time_file_path = generation_time_path / f"{file_prefix}.json"

        with qasm_file_path.open("w") as f:
            f.write(qasm_code)

        with time_file_path.open("w") as f:
            json.dump({"generation_time": generation_time}, f)

        console.log(f"Generated {qasm_file_path} and {time_file_path}")


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
              help='Exit with code 1 if current timestamp exceeds this value.')
def main(
        num_qubits: int, num_gates: int, seed: int, final_measure: bool,
        num_programs: int, output_dir: str, config: Optional[str],
        only_qregs: bool, end_timestamp: int):

    if end_timestamp != -1 and time.time() > end_timestamp:
        console.print(
            "[red]Current time exceeds end timestamp, exiting.[/red]")
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

    generate_qasm_programs(
        num_qubits=num_qubits, num_gates=num_gates, seed=seed,
        final_measure=final_measure, num_programs=num_programs,
        output_dir=output_dir, only_qregs=only_qregs, gate_set=gate_set,
        end_timestamp=end_timestamp)


if __name__ == "__main__":
    main()
