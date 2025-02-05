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

# qasm_code_gen.py


@dataclass
class Gate:
    name: str
    num_qubits: int
    num_params: int = 0

    def to_qasm(self, qreg_name: str, circuit_size: int) -> str:
        qubits = random.sample(range(circuit_size), self.num_qubits)
        qubit_str = ",".join(f"{qreg_name}[{q}]" for q in qubits)
        if self.num_params > 0:
            params = [random.uniform(0, 2 * math.pi)
                      for _ in range(self.num_params)]
            param_str = ",".join(map(str, params))
            return f"{self.name}({param_str}) {qubit_str};"
        else:
            return f"{self.name} {qubit_str};"


class U3(Gate):
    def __init__(self):
        super().__init__("u3", 1, 3)


class U2(Gate):
    def __init__(self):
        super().__init__("u2", 1, 2)


class U1(Gate):
    def __init__(self):
        super().__init__("u1", 1, 1)


class CX(Gate):
    def __init__(self):
        super().__init__("cx", 2)


class ID(Gate):
    def __init__(self):
        super().__init__("id", 1)


class U0(Gate):
    def __init__(self):
        super().__init__("u0", 1, 1)


class U(Gate):
    def __init__(self):
        super().__init__("u", 1, 3)


class P(Gate):
    def __init__(self):
        super().__init__("p", 1, 1)


class X(Gate):
    def __init__(self):
        super().__init__("x", 1)


class Y(Gate):
    def __init__(self):
        super().__init__("y", 1)


class Z(Gate):
    def __init__(self):
        super().__init__("z", 1)


class H(Gate):
    def __init__(self):
        super().__init__("h", 1)


class S(Gate):
    def __init__(self):
        super().__init__("s", 1)


class SDG(Gate):
    def __init__(self):
        super().__init__("sdg", 1)


class T(Gate):
    def __init__(self):
        super().__init__("t", 1)


class TDG(Gate):
    def __init__(self):
        super().__init__("tdg", 1)


class RX(Gate):
    def __init__(self):
        super().__init__("rx", 1, 1)


class RY(Gate):
    def __init__(self):
        super().__init__("ry", 1, 1)


class RZ(Gate):
    def __init__(self):
        super().__init__("rz", 1, 1)


class SX(Gate):
    def __init__(self):
        super().__init__("sx", 1)


class SXDG(Gate):
    def __init__(self):
        super().__init__("sxdg", 1)


class CZ(Gate):
    def __init__(self):
        super().__init__("cz", 2)


class CY(Gate):
    def __init__(self):
        super().__init__("cy", 2)


class SWAP(Gate):
    def __init__(self):
        super().__init__("swap", 2)


class CH(Gate):
    def __init__(self):
        super().__init__("ch", 2)


class CCX(Gate):
    def __init__(self):
        super().__init__("ccx", 3)


class CSWAP(Gate):
    def __init__(self):
        super().__init__("cswap", 3)


class CRX(Gate):
    def __init__(self):
        super().__init__("crx", 2, 1)


class CRY(Gate):
    def __init__(self):
        super().__init__("cry", 2, 1)


class CRZ(Gate):
    def __init__(self):
        super().__init__("crz", 2, 1)


class CU1(Gate):
    def __init__(self):
        super().__init__("cu1", 2, 1)


class CP(Gate):
    def __init__(self):
        super().__init__("cp", 2, 1)


class CU3(Gate):
    def __init__(self):
        super().__init__("cu3", 2, 3)


class CSX(Gate):
    def __init__(self):
        super().__init__("csx", 2)


class CU(Gate):
    def __init__(self):
        super().__init__("cu", 2, 4)


class RXX(Gate):
    def __init__(self):
        super().__init__("rxx", 2, 1)


class RZZ(Gate):
    def __init__(self):
        super().__init__("rzz", 2, 1)


class RCCX(Gate):
    def __init__(self):
        super().__init__("rccx", 3)


class RC3X(Gate):
    def __init__(self):
        super().__init__("rc3x", 4)


class C3X(Gate):
    def __init__(self):
        super().__init__("c3x", 4)


class C3SQRTX(Gate):
    def __init__(self):
        super().__init__("c3sqrtx", 4)


class C4X(Gate):
    def __init__(self):
        super().__init__("c4x", 5)


class QASMCodeGenerator:
    def __init__(
            self, num_qubits: int, seed: Optional[int] = None,
            gate_set: Optional[List[str]] = None):
        self.num_qubits = num_qubits
        self.qasm_code = []
        self.available_gates = {
            "u3": U3(),
            "u2": U2(),
            "u1": U1(),
            "cx": CX(),
            "id": ID(),
            "u0": U0(),
            "u": U(),
            "p": P(),
            "x": X(),
            "y": Y(),
            "z": Z(),
            "h": H(),
            "s": S(),
            "sdg": SDG(),
            "t": T(),
            "tdg": TDG(),
            "rx": RX(),
            "ry": RY(),
            "rz": RZ(),
            "sx": SX(),
            "sxdg": SXDG(),
            "cz": CZ(),
            "cy": CY(),
            "swap": SWAP(),
            "ch": CH(),
            "ccx": CCX(),
            "cswap": CSWAP(),
            "crx": CRX(),
            "cry": CRY(),
            "crz": CRZ(),
            "cu1": CU1(),
            "cp": CP(),
            "cu3": CU3(),
            "csx": CSX(),
            "cu": CU(),
            "rxx": RXX(),
            "rzz": RZZ(),
            "rccx": RCCX(),
            "rc3x": RC3X(),
            "c3x": C3X(),
            "c3sqrtx": C3SQRTX(),
            "c4x": C4X()}
        self.gates = (
            [self.available_gates[gate] for gate in gate_set]
            if gate_set else list(self.available_gates.values())
        )

        if seed is not None:
            random.seed(seed)

        if seed is not None:
            random.seed(seed)

    def reset_memory(self):
        self.qasm_code = []

    def generate_header(self):
        self.qasm_code.append("OPENQASM 2.0;")
        self.qasm_code.append('include "qelib1.inc";')

    def generate_registers(self):
        self.qasm_code.append(f"qreg q[{self.num_qubits}];")
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
        if final_measure:
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


def get_latest_qasm_index(output_dir: Path) -> int:
    qasm_files = list(output_dir.glob("*.qasm"))
    if not qasm_files:
        return 0
    return max(int(f.stem.split("_")[0]) for f in qasm_files)


def generate_qasm_programs(
        num_qubits: int, num_gates: int, seed: int, final_measure: bool,
        num_programs: int, output_dir: str,
        gate_set: Optional[List[str]] = None):
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

    # date_str = datetime.now().strftime("%Y_%m_%d__%H_%M")
    # subfolder_name = f"{date_str}__qasm"
    # generation_output_path = output_path / subfolder_name
    # generation_output_path.mkdir(parents=True, exist_ok=True)

    if not seed:
        seed = random.randint(0, 1000)
    # store the seed in the output folder
    with (generation_output_path / "_seed.txt").open("w") as f:
        f.write(str(seed))
    generator = QASMCodeGenerator(
        num_qubits=num_qubits, seed=seed, gate_set=gate_set)

    starting_index = get_latest_qasm_index(
        generation_output_path) + 1

    for i in range(starting_index, num_programs + starting_index):
        generator.generate_random_qasm(
            num_gates=num_gates, final_measure=final_measure)
        qasm_code = generator.get_qasm_code()
        generator.reset_memory()
        random_chars = uuid4().hex[:6]
        file_path = generation_output_path / \
            f"{str(i).zfill(7)}_{random_chars}.qasm"
        with file_path.open("w") as f:
            f.write(qasm_code)
        console.log(f"Generated {file_path}")


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
def main(
        num_qubits: int, num_gates: int, seed: int, final_measure: bool,
        num_programs: int, output_dir: str, config: Optional[str]):

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

    generate_qasm_programs(
        num_qubits=num_qubits, num_gates=num_gates, seed=seed,
        final_measure=final_measure, num_programs=num_programs,
        output_dir=output_dir, gate_set=gate_set)


if __name__ == "__main__":
    main()
