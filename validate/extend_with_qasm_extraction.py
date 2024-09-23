
from qiskit import QuantumCircuit
from pytket.extensions.qiskit import qiskit_to_tk
from pytket.qasm import circuit_to_qasm_str
from qiskit import qasm2
import os
import uuid
import traceback
from pennylane.tape import QuantumTape
from pennylane.measurements import CountsMP
import pennylane as qml


# get all the global variables which are QuantumCircuit objects
all_qiskit_circuits = [
    {"var_name": name, "circuit": v}
    for name, v in globals().items() if isinstance(v, QuantumCircuit)]


def save_file(qasm_str: str, file_path: str):
    """Save the qasm_str to a file."""
    with open(file_path, "w") as file:
        file.write(qasm_str)


def create_error(
        e: Exception, platform_name: str, file_name: str, var_name: str):
    """Create an error dictionary."""
    return {
        "platform_exporter": platform_name,
        "file_name": file_name,
        "var_name": var_name,
        "error_message": str(e),
        "file_content": open(file_name, "r").read(),
        "stack_trace": traceback.format_exc(),
        "testing_phase": "qasm_exporter"
    }


# get the path of the folder where the current file is located
current_folder = os.path.dirname(os.path.abspath(__file__))
file_name = os.path.basename(__file__)

json_file_path = os.path.join(
    current_folder, f"{file_name}_exporter_errors.json")
errors = []

for i, circuit_info in enumerate(all_qiskit_circuits):
    qiskit_circ = circuit_info["circuit"]
    var_name = circuit_info["var_name"]
    # get uuid
    uuid_str = str(uuid.uuid4())[:6]
    try:
        # get the qasm from Pytket
        tket_circ = qiskit_to_tk(qiskit_circ.decompose().decompose())
        qasm_str_tket = circuit_to_qasm_str(tket_circ, header="qelib1")
        file_path_pytket = os.path.join(
            current_folder, f"{file_name}_{var_name}_pytket.qasm")
        save_file(qasm_str_tket, file_path_pytket)
        print(f"Saved the pytket circuit to {file_path_pytket}")
    except Exception as e:
        print(f"Error in Pytket: {e}")
        errors.append(
            create_error(
                e=e,
                platform_name="pytket",
                file_name=file_name,
                var_name=var_name)
        )

    try:
        # get the qasm from Qiskit
        file_path_qiskit = os.path.join(
            current_folder, f"{file_name}_{var_name}_qiskit.qasm")
        qasm2.dump(qiskit_circ, file_path_qiskit)
        print(f"Saved the qiskit circuit to {file_path_qiskit}")
    except Exception as e:
        print(f"Error in Qiskit: {e}")
        errors.append(
            create_error(
                e=e,
                platform_name="qiskit",
                file_name=file_name,
                var_name=var_name)
        )
    # get the qasm from PennyLane
    try:
        # get the qasm from PennyLane
        file_path_pennylane = os.path.join(
            current_folder, f"{file_name}_{var_name}_pennylane.qasm")
        # create a QNode from the Qiskit circuit
        simplified_qiskit_circ = qiskit_circ.decompose().decompose()
        n_qubits = simplified_qiskit_circ.num_qubits
        measurements = [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
        circuit_fn = qml.from_qiskit(
            simplified_qiskit_circ, measurements=measurements)
        dev = qml.device('default.qubit', wires=n_qubits)
        qml_circuit = qml.QNode(circuit_fn, dev)
        # extract the QASM from the QNode
        with QuantumTape(shots=10) as tape:
            qml_circuit.construct([], {})
            qasm_str_pennylane = qml_circuit.tape.to_openqasm()
            # save the string to file
            save_file(qasm_str_pennylane, file_path_pennylane)
            print(f"Saved the pennylane circuit to {file_path_pennylane}")
    except Exception as e:
        print(f"Error in PennyLane: {e}")
        errors.append(
            create_error(
                e=e,
                platform_name="pennylane",
                file_name=file_name,
                var_name=var_name)
        )

# save the errors to a json file
if errors:
    import json
    with open(json_file_path, "w") as json_file:
        json.dump(errors, json_file, indent=4)
    print(f"Errors saved to {json_file_path}")
