import pytest
from qiskit import QuantumCircuit
from validate.functions_qasm_export import export_to_qasm_with_pytket
from pathlib import Path


def test_export_to_qasm_with_pytket():
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


if __name__ == "__main__":
    pytest.main()
