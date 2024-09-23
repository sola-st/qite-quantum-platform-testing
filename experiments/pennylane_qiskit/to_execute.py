
from pennylane.tape import QuantumTape
from pennylane.measurements import CountsMP
import pennylane as qml
from qiskit import QuantumCircuit
from pathlib import Path

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.h(0)
qc.cx(0, 1)
qc.measure_all(add_bits=False)

# create a QNode from the Qiskit circuit
n_qubits = qc.num_qubits
measurements = [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
circuit_fn = qml.from_qiskit(qc, measurements=measurements)
dev = qml.device('default.qubit', wires=n_qubits)
qml_circuit = qml.QNode(circuit_fn, dev)
# extract the QASM from the QNode
with QuantumTape(shots=10) as tape:
    qml_circuit.construct([], {})
    t = qml_circuit.tape.to_openqasm()
    print(t)
    # get folder of current file
    current_folder = Path(__file__).parent
    # save the string to file
    with open(current_folder / "0_pennylane.qasm", "w") as f:
        f.write(t)
