
from mqt import qcec

# Case 2: Append measurements to the end of the circuit
result_with_measurements = qcec.verify(
    str('qasm_a_with_measurements.qasm'),
    str('qasm_b_with_measurements.qasm'),
    transform_dynamic_circuit=True)
equivalence_with_measurements = str(result_with_measurements.equivalence)
print(f"Equivalence with Measurements: {equivalence_with_measurements}")
