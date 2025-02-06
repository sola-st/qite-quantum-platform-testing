from qiskit import transpile
from qiskit.transpiler import PassManager
from qite.base.primitives import Transformer


class QiskitOptimizer(Transformer):
    def __init__(self, optimization_level):
        super().__init__(f"qiskit_optimizer_level_{optimization_level}")
        self.optimization_level = optimization_level

    def transform(self, qiskit_circuit):
        optimized_circuit = transpile(
            qiskit_circuit, optimization_level=self.optimization_level)
        return optimized_circuit


class QiskitChangeGateSet(Transformer):
    def __init__(self, basis_gates):
        gate_names = "_".join(basis_gates)
        super().__init__(f"qiskit_change_gateset_{gate_names}")
        self.basis_gates = basis_gates

    def transform(self, qiskit_circuit):
        optimized_circuit = transpile(
            qiskit_circuit, basis_gates=self.basis_gates)
        return optimized_circuit


list_qiskit_transformers = [
    QiskitOptimizer(0),
    QiskitOptimizer(1),
    QiskitOptimizer(2),
    QiskitOptimizer(3),
    QiskitChangeGateSet(basis_gates=['u1', 'u2', 'u3', 'cx']),
    QiskitChangeGateSet(basis_gates=['u3', 'cx']),
    QiskitChangeGateSet(basis_gates=['rz', 'sx', 'x', 'cx']),
    QiskitChangeGateSet(basis_gates=['rx', 'ry', 'rz', 'cz']),
]
