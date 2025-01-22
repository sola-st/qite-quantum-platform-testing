import pytest
import os
import tempfile
from pathlib import Path
from validate.functions_oracle_calls import (
    oracle_exporter,
    oracle_optimizer,
    oracle_importer,
    oracle_comparator,
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

from validate.functions_optimize import (
    optimize_with_pytket,
    optimize_with_pennylane,
    optimize_with_qiskit
)

from validate.functions_qasm_import import (
    import_from_qasm_with_bqskit,
    import_from_qasm_with_pennylane,
    import_from_qasm_with_qiskit,
    import_from_qasm_with_pytket,
)

from validate.functions_qasm_compare import (
    compare_qasm_via_qcec,
)


from typing import Dict, Callable


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

        def side_effect(prefix: str) -> Dict[str, Callable]:
            if prefix == "export_to_qasm_with_":
                return {
                    'qiskit': export_to_qasm_with_qiskit,
                    'pennylane': export_to_qasm_with_pennylane,
                    'pytket': export_to_qasm_with_pytket,
                    'bqskit': export_to_qasm_with_bqskit,
                }
            elif prefix == "optimize_with_":
                return {
                    'qiskit': optimize_with_qiskit,
                    'pennylane': optimize_with_pennylane,
                    'pytket': optimize_with_pytket,
                }
            elif prefix == "import_from_qasm_with_":
                return {
                    'qiskit': import_from_qasm_with_qiskit,
                    'pennylane': import_from_qasm_with_pennylane,
                    'pytket': import_from_qasm_with_pytket,
                    'bqskit': import_from_qasm_with_bqskit,
                }
            elif prefix == "compare_qasm_via_":
                return {
                    'qcec': compare_qasm_via_qcec,
                }
            else:
                return {}

        mock.side_effect = side_effect
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


def test_oracle_optimizer(
        mock_get_copy_of_all_circuits_vars, mock_get_functions):
    """Test oracle_optimizer function when optimization raises an exception."""

    # output_dir = "/tmp/optimizer_test/"
    # os.makedirs(output_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as output_dir:
        print(f"\nOutput directory: {output_dir}")

        oracle_optimizer(output_dir)

        # check that there is an optimized file in the temp directory
        assert len(list(Path(output_dir).glob('*.qasm'))
                   ) > 0, "No optimized files exported."

        # print the optimized files
        for optimized_file in Path(output_dir).glob('*.qasm'):
            print("-" * 80)
            print(optimized_file)
            print("-" * 80)
            print(optimized_file.read_text())
            print("=" * 80)


def test_oracle_importer(
        mock_get_copy_of_all_circuits_vars, mock_get_functions):
    """Test oracle_importer function when QASM import raises an exception."""

    # output_dir = "/tmp/optimizer_test/"
    # os.makedirs(output_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as output_dir:
        oracle_exporter(output_dir)
        oracle_importer(output_dir)

        # check that there is an imported file in the temp directory
        assert len(list(Path(output_dir).glob('*.qasm'))
                   ) > 0, "No imported files exported."

        # print the imported files
        for imported_file in Path(output_dir).glob('*.qasm'):
            print("-" * 80)
            print(imported_file)
            print("-" * 80)
            print(imported_file.read_text())
            print("=" * 80)


def test_oracle_comparator(
        mock_get_copy_of_all_circuits_vars, mock_get_functions):
    """Test oracle_comparator function when comparison raises an exception."""

    output_dir = "/tmp/optimizer_test/"
    os.makedirs(output_dir, exist_ok=True)
    # with tempfile.TemporaryDirectory() as output_dir:
    oracle_exporter(output_dir)
    oracle_optimizer(output_dir)
    oracle_comparator(output_dir)

    # check that there is a comparison file in the temp directory
    assert len(list(Path(output_dir).glob('*.json'))
               ) > 0, "No comparison files exported."

    # print the comparison files
    for comparison_file in Path(output_dir).glob('*'):
        print("-" * 80)
        print(comparison_file)
        print("-" * 80)
        print(comparison_file.read_text())
        print("=" * 80)
