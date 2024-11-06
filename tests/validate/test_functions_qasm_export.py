import pytest
from qiskit import QuantumCircuit
from validate.functions_qasm_export import export_to_qasm_with_pytket
from validate.functions_qasm_export import export_to_qasm_with_qiskit
from pathlib import Path
import warnings


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


if __name__ == "__main__":
    pytest.main()
