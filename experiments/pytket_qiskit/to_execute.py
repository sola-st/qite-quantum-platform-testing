# Section: Prologue
from pytket.extensions.qiskit import qiskit_to_tk
from pytket.qasm import circuit_to_qasm_str
from qiskit import qasm2
import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Session, Sampler

# Section: Circuit
qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')

# Apply some gate operations
qc.h(qr[0])  # Apply Hadamard gate to qubit 0
qc.cx(qr[0], qr[1])  # Apply CNOT gate with control qubit 0 and target qubit 1
qc.x(qr[2])  # Apply X (NOT) gate to qubit 2
qc.cz(qr[1], qr[2])  # Apply CZ gate with control qubit 1 and target qubit 2
qc.y(qr[0])  # Apply Y gate to qubit 0

# Section: Measurement
qc.measure(qr, cr)

# Section: Execution
# Run the sampler job locally using AerSimulator.
# Session syntax is supported but ignored.
aer_sim = AerSimulator()

# The session is used but ignored in AerSimulator.
sampler = Sampler(mode=aer_sim)
result = sampler.run([qc]).result()[0]

# Section: Results
counts = result.data.cr.get_counts()
print(f"Measurement results: {counts}")


# get all the global variables which are QuantumCircuit objects
all_qiskit_circuits = [
    v for v in globals().values() if isinstance(v, QuantumCircuit)]


def save_file(qasm_str: str, file_path: str):
    """Save the qasm_str to a file."""
    with open(file_path, "w") as file:
        file.write(qasm_str)


# get the path of the folder where the current file is located
current_folder = os.path.dirname(os.path.abspath(__file__))
for i, qiskit_circ in enumerate(all_qiskit_circuits):
    # get the qasm from Pytket
    tket_circ = qiskit_to_tk(qiskit_circ)
    qasm_str = circuit_to_qasm_str(tket_circ, header="qelib1")
    file_path_pytket = os.path.join(current_folder, f"{i}_pytket.qasm")
    save_file(qasm_str, file_path_pytket)
    print(f"Saved the pytket circuit to {file_path_pytket}")
    # get the qasm from Qiskit
    file_path_qiskit = os.path.join(current_folder, f"{i}_qiskit.qasm")
    qasm2.dump(qiskit_circ, file_path_qiskit)
    print(f"Saved the qiskit circuit to {file_path_qiskit}")
