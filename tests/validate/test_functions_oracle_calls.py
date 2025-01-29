import pytest
import os
import json
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
    # export_to_qasm_with_bqskit,
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
from validate.functions_oracle_calls import (
    get_all_string_values_from_dict,
    get_all_qasm_files,
    get_reliable_qasm_files
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

        def side_effect(prefix: str) -> Dict[str, Callable]:
            if prefix == "export_to_qasm_with_":
                return {
                    'qiskit': export_to_qasm_with_qiskit,
                    'pennylane': export_to_qasm_with_pennylane,
                    'pytket': export_to_qasm_with_pytket,
                    # 'bqskit': export_to_qasm_with_bqskit,
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

    # output_dir = "/tmp/optimizer_test/"
    # os.makedirs(output_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as output_dir:
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


def test_get_all_string_values_from_dict():
    """Test get_all_string_values_from_dict function to ensure it extracts all string values from a nested dictionary."""

    # Test case 1: Simple dictionary with string values
    simple_dict = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }
    assert get_all_string_values_from_dict(
        simple_dict) == ["value1", "value2", "value3"]

    # Test case 2: Nested dictionary with string values
    nested_dict = {
        "key1": {
            "subkey1": "value1",
            "subkey2": "value2"
        },
        "key2": "value3",
        "key3": {
            "subkey3": {
                "subsubkey1": "value4"
            }
        }
    }
    assert get_all_string_values_from_dict(nested_dict) == [
        "value1", "value2", "value3", "value4"]

    # Test case 3: Dictionary with non-string values
    mixed_dict = {
        "key1": "value1",
        "key2": 123,
        "key3": {
            "subkey1": "value2",
            "subkey2": [1, 2, 3]
        },
        "key4": {
            "subkey3": {
                "subsubkey1": "value3",
                "subsubkey2": None
            }
        }
    }
    assert get_all_string_values_from_dict(
        mixed_dict) == ["value1", "value2", "value3"]

    # Test case 4: Empty dictionary
    empty_dict = {}
    assert get_all_string_values_from_dict(empty_dict) == []

    # Test case 5: Dictionary with no string values
    no_string_dict = {
        "key1": 123,
        "key2": [1, 2, 3],
        "key3": {
            "subkey1": 456,
            "subkey2": None
        }
    }
    assert get_all_string_values_from_dict(no_string_dict) == []


def test_get_all_qasm_files():
    """Test get_all_qasm_files function to ensure it extracts all QASM file paths from a metadata dictionary."""
    # Test case 3: Dictionary with non-QASM file paths
    mixed_dict = {
        "key1": "file1.qasm",
        "key2": "file2.txt",
        "key3": {
            "subkey1": "file3.qasm",
            "subkey2": "file4.doc"
        },
        "key4": {
            "subkey3": {
                "subsubkey1": "file5.qasm",
                "subsubkey2": "file6.pdf"
            }
        }
    }
    assert get_all_qasm_files(mixed_dict) == [
        "file1.qasm", "file3.qasm", "file5.qasm"]


def test_get_reliable_qasm_files(tmp_path):
    """Test get_reliable_QASM_files function to ensure it filters QASM files with less than max_exceptions."""

    # Create temporary error metadata files
    error_metadata_1 = {
        "exception_message": "Error 1",
        "stack_trace": "Traceback 1",
        "current_file": "test_file.py",
        "involved_functions": ["function_1"],
        "extra_info": {"input_qasm_file": "file1.qasm"}
    }
    error_metadata_2 = {
        "exception_message": "Error 2",
        "stack_trace": "Traceback 2",
        "current_file": "test_file.py",
        "involved_functions": ["function_2"],
        "extra_info": {"input_qasm_file": "file2.qasm"}
    }
    error_metadata_3 = {
        "exception_message": "Error 3",
        "stack_trace": "Traceback 3",
        "current_file": "test_file.py",
        "involved_functions": ["function_3"],
        "extra_info": {"input_qasm_file": "file1.qasm"}
    }

    error_file_1 = tmp_path / "1_error.json"
    error_file_2 = tmp_path / "2_error.json"
    error_file_3 = tmp_path / "ac_error.json"

    error_file_1.write_text(json.dumps(error_metadata_1))
    error_file_2.write_text(json.dumps(error_metadata_2))
    error_file_3.write_text(json.dumps(error_metadata_3))

    # Create temporary QASM files
    qasm_file_1 = tmp_path / "file1.qasm"
    qasm_file_2 = tmp_path / "file2.qasm"
    qasm_file_3 = tmp_path / "file3.qasm"

    qasm_file_1.write_text("OPENQASM 2.0;")
    qasm_file_2.write_text("OPENQASM 2.0;")
    qasm_file_3.write_text("OPENQASM 2.0;")

    # Test get_reliable_QASM_files function
    reliable_qasm_files = get_reliable_qasm_files(
        input_dir=tmp_path, max_errors_allowed=1)

    # Check that only file2.qasm and file3.qasm are considered reliable
    assert set(reliable_qasm_files) == {str(qasm_file_2), str(qasm_file_3)}
