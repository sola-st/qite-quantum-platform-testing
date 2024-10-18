from qiskit import QuantumCircuit
import os
from pathlib import Path
from typing import Optional


def export_to_qasm_with_pytket(
        qiskit_circ: QuantumCircuit, var_name: str) -> Optional[str]:
    """Export a Qiskit circuit to a Pytket QASM file."""
    from pytket.extensions.qiskit import qiskit_to_tk
    from pytket.qasm import circuit_to_qasm_str

    # Convert Qiskit circuit to Pytket format and save as QASM
    tket_circ = qiskit_to_tk(qiskit_circ.decompose().decompose())
    qasm_str_tket = circuit_to_qasm_str(
        tket_circ, header="qelib1", maxwidth=200)

    # Determine file path
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_pytket = current_file.with_name(
        f"{file_stem}_{var_name}_pytket.qasm")

    with open(file_path_pytket, 'w') as f:
        f.write(qasm_str_tket)

    print(f"Saved the Pytket circuit to {file_path_pytket}")
    return file_path_pytket.as_posix()


def export_to_qasm_with_qiskit(
        qiskit_circ: QuantumCircuit, var_name: str) -> Optional[str]:
    """Export a Qiskit circuit to a Qiskit QASM file."""
    from qiskit import qasm2

    # Determine file path
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_qiskit = current_file.with_name(
        f"{file_stem}_{var_name}_qiskit.qasm")

    # Save Qiskit circuit directly to QASM
    qasm2.dump(qiskit_circ, file_path_qiskit)

    print(f"Saved the Qiskit circuit to {file_path_qiskit}")
    return file_path_qiskit.as_posix()


def export_to_qasm_with_pennylane(
        qiskit_circ: QuantumCircuit, var_name: str) -> Optional[str]:
    """Export a Qiskit circuit to a PennyLane QASM file."""
    import pennylane as qml
    from pennylane.tape import QuantumTape

    # Convert Qiskit circuit to a simplified form
    simplified_qiskit_circ = qiskit_circ.decompose().decompose()
    n_qubits = simplified_qiskit_circ.num_qubits

    # Define measurement and PennyLane device
    measurements = [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    circuit_fn = qml.from_qiskit(
        simplified_qiskit_circ, measurements=measurements)
    dev = qml.device('default.qubit', wires=n_qubits)
    qml_circuit = qml.QNode(circuit_fn, dev)

    # Extract the QASM from the PennyLane QNode
    with QuantumTape(shots=10) as tape:
        qml_circuit.construct([], {})
        qasm_str_pennylane = qml_circuit.tape.to_openqasm()

    # Determine file path
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_pennylane = current_file.with_name(
        f"{file_stem}_{var_name}_pennylane.qasm")

    # Save PennyLane QASM string to file
    with open(file_path_pennylane, 'w') as f:
        f.write(qasm_str_pennylane)

    print(f"Saved the PennyLane circuit to {file_path_pennylane}")
    return file_path_pennylane.as_posix()
