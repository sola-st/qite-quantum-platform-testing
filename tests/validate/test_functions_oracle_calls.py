import pytest
import tempfile
from pathlib import Path
from validate.functions_oracle_calls import (
    oracle_exporter,
    get_copy_of_all_circuits_vars,
    get_functions
)
from qiskit import QuantumCircuit
from unittest.mock import patch, MagicMock
from validate.functions_qasm_export import (
    export_to_qasm_with_bqskit,
    export_to_qasm_with_pennylane,
    export_to_qasm_with_qiskit,
    export_to_qasm_with_pytket,
)


@pytest.fixture
def mock_qc():
    """Fixture to create a mock QuantumCircuit."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


@pytest.fixture
def mock_get_copy_of_all_circuits_vars(mock_qc):
    """Fixture to mock get_copy_of_all_circuits_vars function."""
    with patch('validate.functions_oracle_calls.get_copy_of_all_circuits_vars') as mock:
        mock.return_value = {'mock_qc': mock_qc}
        yield mock


@pytest.fixture
def mock_get_functions():
    """Fixture to mock get_functions function."""
    with patch('validate.functions_oracle_calls.get_functions') as mock:
        mock.return_value = {
            'qiskit': export_to_qasm_with_qiskit,
            'pennylane': export_to_qasm_with_pennylane,
            'pytket': export_to_qasm_with_pytket,
            'bqskit': export_to_qasm_with_bqskit,
        }
        yield mock


def test_oracle_exporter(
        mock_get_copy_of_all_circuits_vars, mock_get_functions):
    """Test oracle_exporter function when QASM export raises an exception."""

    with tempfile.TemporaryDirectory() as output_dir:
        oracle_exporter(output_dir)

        # check that there is a qasm file in the temp directory
        assert len(list(Path(output_dir).glob('*.qasm'))
                   ) > 0, "No QASM files exported."

        # print the qasm files
        for qasm_file in Path(output_dir).glob('*.qasm'):
            print("-" * 80)
            print(qasm_file)
            print("-" * 80)
            print(qasm_file.read_text())
            print("=" * 80)
