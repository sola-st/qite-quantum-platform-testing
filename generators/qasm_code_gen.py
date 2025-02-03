from dataclasses import dataclass
from typing import List, Optional
import random
import math

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


class H(Gate):
    def __init__(self):
        super().__init__("h", 1)


class CX(Gate):
    def __init__(self):
        super().__init__("cx", 2)


class RX(Gate):
    def __init__(self):
        super().__init__("rx", 1, 1)


class U3(Gate):
    def __init__(self):
        super().__init__("u3", 1, 3)


class QASMCodeGenerator:
    def __init__(self, num_qubits, seed: Optional[int] = None):
        self.num_qubits = num_qubits
        self.qasm_code = []
        self.gates = [H(), CX(), RX(), U3()]
        if seed is not None:
            random.seed(seed)

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
