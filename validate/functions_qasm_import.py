def import_from_qasm_with_qiskit(file_path: str):
    """Import a QASM file using Qiskit."""
    from qiskit import qasm2
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = qasm2.loads(qasm_content)
    print(f"Circuit (Qiskit) imported correctly: {file_path}")
    return circuit


def import_from_qasm_with_pytket(file_path: str):
    """Import a QASM file using Pytket."""
    from pytket.qasm import circuit_from_qasm_str
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = circuit_from_qasm_str(qasm_content)
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
