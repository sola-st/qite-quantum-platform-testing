# Section: Prologue
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
