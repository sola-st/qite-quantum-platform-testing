
from mqt import qcec

# Case 1 + 2: Make both circuits operate on two qubits and append measurements
result_two_qubits_with_measurements = qcec.verify(
    str('qasm_a_two_qubits_with_measurements.qasm'),
    str('qasm_b_two_qubits_with_measurements.qasm'),
    transform_dynamic_circuit=True)
equivalence_two_qubits_with_measurements = str(result_two_qubits_with_measurements.equivalence)
print(f"Equivalence for Two Qubits with Measurements: {equivalence_two_qubits_with_measurements}")
