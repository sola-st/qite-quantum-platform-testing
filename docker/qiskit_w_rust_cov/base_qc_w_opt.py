from qiskit import QuantumCircuit
from qiskit import transpile


def test_optimization():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.swap(0, 1)
    qc.measure_all()

    qc_transpiled = transpile(
        qc, basis_gates=['u1', 'u2', 'u3', 'cx'],
        optimization_level=3)
    print(qc_transpiled.draw())


if __name__ == "__main__":
    test_optimization()
