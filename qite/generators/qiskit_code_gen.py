"""Script with a series of objects/dataclass, that represent the different gates in Qiskit.

The signature of the gates are:
    "barrier(*qargs, label=None)",
    "ccx(control_qubit1, control_qubit2, target_qubit, ctrl_state=None)",
    "ccz(control_qubit1, control_qubit2, target_qubit, label=None, ctrl_state=None)",
    "ch(control_qubit, target_qubit, label=None, ctrl_state=None)",
    "cp(theta, control_qubit, target_qubit, label=None, ctrl_state=None)",
    "crx(theta, control_qubit, target_qubit, label=None, ctrl_state=None)",
    "cry(theta, control_qubit, target_qubit, label=None, ctrl_state=None)",
    "crz(theta, control_qubit, target_qubit, label=None, ctrl_state=None)",
    "cs(control_qubit, target_qubit, label=None, ctrl_state=None)",
    "csdg(control_qubit, target_qubit, label=None, ctrl_state=None)",
    "cswap(control_qubit, target_qubit1, target_qubit2, label=None, ctrl_state=None)",
    "csx(control_qubit, target_qubit, label=None, ctrl_state=None)",
    "cu(theta, phi, lam, gamma, control_qubit, target_qubit, label=None, ctrl_state=None)",
    "cx(control_qubit, target_qubit, label=None, ctrl_state=None)",
    "cy(control_qubit, target_qubit, label=None, ctrl_state=None)",
    "cz(control_qubit, target_qubit, label=None, ctrl_state=None)",
    "dcx(qubit1, qubit2)",
    "delay(duration, qarg=None, unit='dt')",
    "ecr(qubit1, qubit2)",
    "h(qubit)",
    "id(qubit)",
    "initialize(params, qubits=None, normalize=False)",
    "iswap(qubit1, qubit2)",
    "mcp(lam, control_qubits, target_qubit, ctrl_state=None)",
    "mcrx(theta, q_controls, q_target, use_basis_gates=False)",
    "mcry(theta, q_controls, q_target, q_ancillae=None, mode=None, use_basis_gates=False)",
    "mcrz(lam, q_controls, q_target, use_basis_gates=False)",
    "mcx(control_qubits, target_qubit, ancilla_qubits=None, mode='noancilla', ctrl_state=None)",
    "measure(qubit, cbit)",
    "ms(theta, qubits)",
    "p(theta, qubit)",
    "pauli(pauli_string, qubits)",
    "prepare_state(state, qubits=None, label=None, normalize=False)",
    "r(theta, phi, qubit)",
    "rcccx(control_qubit1, control_qubit2, control_qubit3, target_qubit)",
    "rccx(control_qubit1, control_qubit2, target_qubit)",
    "reset(qubit)",
    "rv(vx, vy, vz, qubit)",
    "rx(theta, qubit, label=None)",
    "rxx(theta, qubit1, qubit2)",
    "ry(theta, qubit, label=None)",
    "ryy(theta, qubit1, qubit2)",
    "rz(phi, qubit)",
    "rzx(theta, qubit1, qubit2)",
    "rzz(theta, qubit1, qubit2)",
    "s(qubit)",
    "sdg(qubit)",
    "store(var, qubits, *, label=None)",
    "swap(qubit1, qubit2)",
    "sx(qubit)",
    "sxdg(qubit)",
    "t(qubit)",
    "tdg(qubit)",
    "u(theta, phi, lam, qubit)",
    "unitary(obj, qubits, label=None)",
    "x(qubit, label=None)",
    "y(qubit)",
    "z(qubit)"

Create an object hierarchy to track the position of the arguments that are qubits, classical bits, and parameters.
theta, phi, lam, gamma, vx, vy, vz are parameters ranging from 0 to 2*pi.

Create the object hierarchy of classes and dataclasses to represent the gates in Qiskit.
The use cases it to use these classes to generate strings that reprent valid Qiskit code statements that can be used to generate quantum circuits.

The creation of python statement takes:
- the name of the variable of the circuit object (e.g. qc)
- the name of the quantum register object (e.g. qr)
- the name of the classical register object (e.g. cr)
- the maximum number of qubits in the quantum register
- the maximum number of classical bits in the classical register
Then a set of gate objects is sampled and instantiated with random arguments,
thus each gate should know the position of the qubits, classical bits, and parameters in the call.

The main Gate class should have the method: .instantiate() that should return a string with the valid Qiskit code statement.
Each Gate is initialized with the same parameters:
- circuit_var: str
- quantum_reg_var: str
- classical_reg_var: str
- max_qubits: int
- max_bits: int

I want to be able to generate many valid statement by just sampling the gate objects and calling the .instantiate() method.

Examples of valid Qiskit code statements:
- qc.cx(qr[0], qr[1])
- qc.rz(1.234554, qr[0])
- qc.ccx(qr[0], qr[1], qr[2])
"""
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
from qite.qite_loop import lazy_imports

console = Console(color_system=None)


class DistinctSampler:
    def __init__(self, max_value: int):
        self.max_value = max_value
        self.available_values = set(range(max_value))
        self.sampled_values = set()

    def sample(self) -> int:
        if not self.available_values:
            raise ValueError("No more distinct values available to sample.")
        value = random.choice(list(self.available_values))
        self.available_values.remove(value)
        self.sampled_values.add(value)
        return value

    def reset(self):
        self.available_values = set(range(self.max_value))
        self.sampled_values = set()

    def get_remaining(self) -> List[int]:
        return list(self.available_values)


class Gate:
    def __init__(self, circuit_var: str, quantum_reg_var: str,
                 classical_reg_var: str, max_qubits: int, max_bits: int):
        self.circuit_var = circuit_var
        self.quantum_reg_var = quantum_reg_var
        self.classical_reg_var = classical_reg_var
        self.quantum_sampler = DistinctSampler(max_value=max_qubits)
        self.classical_sampler = DistinctSampler(max_value=max_bits)

    def instantiate(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")

# Helper function to generate random parameters


def random_param() -> float:
    return round(random.uniform(0, 2 * math.pi), 6)

# Gate classes


class Barrier(Gate):
    def instantiate(self) -> str:
        qubits = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(random.randint(1, 5))]
        return f"{self.circuit_var}.barrier({', '.join(qubits)})"


class Ccx(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.ccx({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Ccz(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.ccz({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Cp(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.cp({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Cx(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.cx({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Crx(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.crx({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Cry(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.cry({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Crz(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.crz({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Cs(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.cs({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Csdg(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.csdg({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Cswap(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.cswap({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Csx(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.csx({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Cu(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        phi = random_param()
        lam = random_param()
        gamma = random_param()
        return f"{self.circuit_var}.cu({theta}, {phi}, {lam}, {gamma}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Cy(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.cy({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Cz(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.cz({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Dcx(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.dcx({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Delay(Gate):
    def instantiate(self) -> str:
        duration = random.randint(1, 10)
        unit = 'dt'
        return f"{self.circuit_var}.delay({duration}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], unit='{unit}')"


class Ecr(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.ecr({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class H(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.h({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Id(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.id({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Initialize(Gate):
    def instantiate(self) -> str:
        params = [random_param() for _ in range(random.randint(1, 5))]
        return f"{self.circuit_var}.initialize({params}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Iswap(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.iswap({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Mcp(Gate):
    def instantiate(self) -> str:
        lam = random_param()
        controls = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(random.randint(1, 3))]
        return f"{self.circuit_var}.mcp({lam}, [{', '.join(controls)}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Mcrx(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        controls = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(random.randint(1, 3))]
        return f"{self.circuit_var}.mcrx({theta}, [{', '.join(controls)}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Mcry(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        controls = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(random.randint(1, 3))]
        return f"{self.circuit_var}.mcry({theta}, [{', '.join(controls)}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Mcrz(Gate):
    def instantiate(self) -> str:
        lam = random_param()
        controls = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(random.randint(1, 3))]
        return f"{self.circuit_var}.mcrz({lam}, [{', '.join(controls)}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Mcx(Gate):
    def instantiate(self) -> str:
        controls = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(random.randint(1, 3))]
        return f"{self.circuit_var}.mcx([{', '.join(controls)}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Measure(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.measure({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.classical_reg_var}[{self.classical_sampler.sample()}])"


class Ms(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        qubits = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(random.randint(1, 3))]
        return f"{self.circuit_var}.ms({theta}, [{', '.join(qubits)}])"


class P(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.p({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Pauli(Gate):
    def instantiate(self) -> str:
        pauli_string = ''.join(random.choice('XYZ')
                               for _ in range(random.randint(1, 3)))
        qubits = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(len(pauli_string))]
        return f"{self.circuit_var}.pauli('{pauli_string}', {', '.join(qubits)})"


class PrepareState(Gate):
    def instantiate(self) -> str:
        state = ''.join(random.choice('0X')
                        for _ in range(random.randint(1, 3)))
        return f"{self.circuit_var}.prepare_state('{state}', {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class R(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        phi = random_param()
        return f"{self.circuit_var}.r({theta}, {phi}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Rcccx(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.rcccx({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Rccx(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.rccx({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Reset(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.reset({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Rv(Gate):
    def instantiate(self) -> str:
        vx = random_param()
        vy = random_param()
        vz = random_param()
        return f"{self.circuit_var}.rv({vx}, {vy}, {vz}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Rx(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.rx({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Rxx(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.rxx({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Ry(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.ry({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Ryy(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.ryy({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Rz(Gate):
    def instantiate(self) -> str:
        phi = random_param()
        return f"{self.circuit_var}.rz({phi}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Rzx(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.rzx({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Rzz(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        return f"{self.circuit_var}.rzz({theta}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class S(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.s({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Sdg(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.sdg({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Store(Gate):
    def instantiate(self) -> str:
        var = f"var{random.randint(1, 10)}"
        qubits = [
            f"{self.quantum_reg_var}[{self.quantum_sampler.sample()}]"
            for _ in range(random.randint(1, 3))]
        return f"{self.circuit_var}.store('{var}', {', '.join(qubits)})"


class Swap(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.swap({self.quantum_reg_var}[{self.quantum_sampler.sample()}], {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Sx(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.sx({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Sxdg(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.sxdg({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class T(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.t({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Tdg(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.tdg({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class U(Gate):
    def instantiate(self) -> str:
        theta = random_param()
        phi = random_param()
        lam = random_param()
        return f"{self.circuit_var}.u({theta}, {phi}, {lam}, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Unit(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.unitary(obj, {self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class X(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.x({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Y(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.y({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


class Z(Gate):
    def instantiate(self) -> str:
        return f"{self.circuit_var}.z({self.quantum_reg_var}[{self.quantum_sampler.sample()}])"


# Example usage


GATE_MAP = {
    "barrier": Barrier, "ccx": Ccx, "ccz": Ccz, "cp": Cp,
    "cx": Cx,
    "crx": Crx, "cry": Cry, "crz": Crz, "cs": Cs, "csdg": Csdg, "cswap": Cswap, "csx": Csx, "cu": Cu,
    "cy": Cy, "cz": Cz,
    "dcx": Dcx,
    "ecr": Ecr, "h": H, "id": Id,
    "iswap": Iswap, "mcp": Mcp, "mcrx": Mcrx, "mcry": Mcry,
    "mcrz": Mcrz, "mcx": Mcx,
    "p": P,
    "r": R, "rcccx": Rcccx, "rccx": Rccx,
    "rv": Rv, "rx": Rx, "rxx": Rxx, "ry": Ry,
    "ryy": Ryy, "rz": Rz, "rzx": Rzx, "rzz": Rzz, "s": S, "sdg": Sdg,
    "swap": Swap, "sx": Sx, "sxdg": Sxdg, "t": T, "tdg": Tdg,
    "x": X, "y": Y, "z": Z}


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


def get_latest_py_index(output_dir: Path) -> int:
    py_files = list(output_dir.glob("*.py"))
    if not py_files:
        return 0
    return max(int(f.stem.split("_")[0]) for f in py_files)


def generate_qiskit_programs(
        num_qubits: int, num_gates: int, seed: int, final_measure: bool,
        num_programs: int, output_dir: str, only_qregs: bool,
        gate_set: Optional[List[str]] = None):
    """Generate a given number of random Qiskit programs.

    Each program is stored as .py and has the name
    {i}.zfill(7)_{uuid4()}.py.
    The files are stored in a sub-folder with the current name:
    2025_01_29__16_43__qiskit (date of the start of execution)
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

    starting_index = get_latest_py_index(
        generation_output_path) + 1

    for i in range(starting_index, num_programs + starting_index):
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
def main(
        num_qubits: int, num_gates: int, seed: int, final_measure: bool,
        num_programs: int, output_dir: str, config: Optional[str],
        only_qregs: bool):

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
        output_dir=output_dir, only_qregs=only_qregs, gate_set=gate_set)


if __name__ == "__main__":
    main()
