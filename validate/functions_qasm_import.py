def import_from_qasm_with_qiskit(file_path: str):
    """Import a QASM file using Qiskit."""
    from qiskit import qasm2
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = qasm2.loads(
        qasm_content, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
    print(f"Circuit (Qiskit) imported correctly: {file_path}")
    return circuit


def import_from_qasm_with_pytket(file_path: str):
    """Import a QASM file using Pytket."""
    from pytket.qasm import circuit_from_qasm_str
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = circuit_from_qasm_str(qasm_content, maxwidth=200)
    print(f"Circuit (Pytket) imported correctly: {file_path}")
    return circuit


def import_from_qasm_with_pennylane(file_path: str):
    """Import a QASM file using PennyLane."""
    import pennylane as qml
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = qml.from_qasm(qasm_content)
    print(f"Circuit (PennyLane) imported correctly: {file_path}")
    return circuit


def import_from_qasm_with_bqskit(file_path: str):
    """Import a QASM file using bqskit."""
    from bqskit import Circuit
    bqskit_circuit = Circuit.from_file(file_path)
    print(f"Circuit (bqskit) imported correctly: {file_path}")
    return bqskit_circuit
