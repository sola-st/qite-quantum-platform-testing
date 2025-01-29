import pytest
from qiskit import QuantumCircuit
from validate.functions_qasm_export import export_to_qasm_with_pytket
from validate.functions_qasm_export import export_to_qasm_with_qiskit
from pathlib import Path
import warnings
from validate.functions_qasm_export import export_to_qasm_from_proprietary_ir_pennylane
import pennylane as qml


def test_export_to_qasm_with_pytket():
    # Suppress warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # Create a simple Qiskit circuit
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        # Call the function
        var_name = "test"
        qasm_file_path = export_to_qasm_with_pytket(qc, var_name)

        # Check if the file was created
        assert Path(qasm_file_path).exists()

        # Cleanup
        Path(qasm_file_path).unlink()


def test_export_to_qasm_with_qiskit():
    # Create a simple Qiskit circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    # Call the function
    var_name = "test"
    qasm_file_path = export_to_qasm_with_qiskit(qc, var_name)

    # Check if the file was created
    assert Path(qasm_file_path).exists()

    # Cleanup
    Path(qasm_file_path).unlink()


def test_export_to_qasm_from_proprietary_ir_pennylane():
    """Test exporting a PennyLane circuit to a QASM file."""
    qasm_content = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
creg c[1];
id q[0];
x q[0];
measure q[0] -> c[0];
"""
    circuit = qml.from_qasm(qasm_content)
    var_name = "test_pennylane"
    qasm_file_path = export_to_qasm_from_proprietary_ir_pennylane(
        circuit, var_name)

    # Check if the file was created
    assert Path(qasm_file_path).exists()

    created_qasm_content = Path(qasm_file_path).read_text()
    assert created_qasm_content == qasm_content

    # Cleanup
    Path(qasm_file_path).unlink()


if __name__ == "__main__":
    pytest.main()
