from pennylane.tape import QuantumTape
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=3)


@qml.qnode(dev)
def circuit():
    qml.SX(wires=1)
    return [
        qml.expval(qml.PauliZ(0)),
        qml.expval(qml.PauliZ(1)),
        qml.expval(qml.PauliZ(2)),
    ]


np.random.seed(1)
qml.drawer.use_style("black_white")
print("--------------------")
print("Circuit:")
print(qml.draw(circuit, level="device")())


with QuantumTape(shots=10) as tape:
    circuit.construct([], {})
    qasm_str_pennylane = circuit.tape.to_openqasm()
print("--------------------")
print("QASM string from PennyLane:")
print(qasm_str_pennylane)
