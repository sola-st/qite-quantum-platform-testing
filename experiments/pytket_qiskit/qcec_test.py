import os
from mqt import qcec

# get path of the current file
current_folder = os.path.dirname(os.path.abspath(__file__))

# path to the qasm files
qasm_file_pytket = os.path.join(current_folder, "0_pytket.qasm")
qasm_file_qiskit = os.path.join(current_folder, "0_qiskit.qasm")

# verify the equivalence of two circuits provided as qasm files
result = qcec.verify(qasm_file_pytket, qasm_file_qiskit)

# print the result
assert str(result.equivalence) == 'equivalent', "The circuits are not equivalent"
