
from qiskit import QuantumCircuit
from pytket.extensions.qiskit import qiskit_to_tk
from pytket.qasm import circuit_to_qasm_str
from qiskit import qasm2
import os
import uuid


# get all the global variables which are QuantumCircuit objects
all_qiskit_circuits = [
    {"var_name": name, "circuit": v}
    for name, v in globals() if isinstance(v, QuantumCircuit)]


def save_file(qasm_str: str, file_path: str):
    """Save the qasm_str to a file."""
    with open(file_path, "w") as file:
        file.write(qasm_str)


# get the path of the folder where the current file is located
current_folder = os.path.dirname(os.path.abspath(__file__))
file_name = os.path.basename(__file__)
for i, circuit_info in enumerate(all_qiskit_circuits):
    qiskit_circ = circuit_info["circuit"]
    var_name = circuit_info["var_name"]
    # get uuid
    uuid_str = str(uuid.uuid4())[:6]
    # get the qasm from Pytket
    tket_circ = qiskit_to_tk(qiskit_circ.decompose())
    qasm_str = circuit_to_qasm_str(tket_circ, header="qelib1")
    file_path_pytket = os.path.join(
        current_folder, f"{file_name}_{var_name}_pytket.qasm")
    save_file(qasm_str, file_path_pytket)
    print(f"Saved the pytket circuit to {file_path_pytket}")
    # get the qasm from Qiskit
    file_path_qiskit = os.path.join(
        current_folder, f"{file_name}_{var_name}_qiskit.qasm")
    qasm2.dump(qiskit_circ, file_path_qiskit)
    print(f"Saved the qiskit circuit to {file_path_qiskit}")
