1. Intall grammarinator
```shell
pip install grammarinator
```

2. Generate the grammar with ChatGPT
```plaintext
create a grammar for antlr for generating qiskit programs
...
refine the grammar such that this example is gneerated:

from qiskit import QuantumCircuit, Aer, transpile, assemble, execute

# Define the circuit
qc = QuantumCircuit(3, 3)

# Apply gates
qc.h(0)         # Hadamard on qubit 0
qc.cx(0, 1)     # CNOT on qubits 0 and 1
qc.x(2)         # Pauli-X on qubit 2

# Measure
qc.measure(0, 0)
qc.measure(1, 1)
qc.measure(2, 2)

# Execute the circuit
backend = Aer.get_backend('qasm_simulator')
shots = 1024
job = execute(qc, backend, shots=shots)
result = job.result()
counts = result.get_counts(qc)
print(counts)

give me the new antlr
```


3. Generate the `unparser` from the grammar.
```shell
mkdir output
grammarinator-process qiskit.g4 -o output/ --no-actions
```

4. Fuzz programs
```shell
cd output
grammarinator-generate QiskitGenerator.QiskitGenerator -r program -d 2 -o output_testcases.py -n 3 --sys-path .
```
