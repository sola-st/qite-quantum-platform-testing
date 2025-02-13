
from mqt import qcec

# Case 1: Make both circuits operate on two qubits
result_two_qubits = qcec.verify(
    str('qasm_a_two_qubits.qasm'),
    str('qasm_b_two_qubits.qasm'),
    transform_dynamic_circuit=True)
equivalence_two_qubits = str(result_two_qubits.equivalence)
print(f"Equivalence for Two Qubits: {equivalence_two_qubits}")
