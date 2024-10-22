fromqiskitimportQuantumCircuit,Aer,transpile,assemble,execute

# Define the circuit
qc =QuantumCircuit(,)

# Execute the circuit
backend =Aer.get_backend(qasm_simulator)
shots =
job =execute(qc,backend,shots=shots)
result =job.result()
counts =result.get_counts(qc)
print(counts)
