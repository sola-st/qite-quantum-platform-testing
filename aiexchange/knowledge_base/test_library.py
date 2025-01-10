import pytest
from aiexchange.knowledge_base.library import get_files_from_entity
from aiexchange.knowledge_base.library import preprocess_extract_entities
import tempfile
import shutil
import os


def test_get_file_from_entity_success():
    """
    Test that get_file_from_entity returns the correct file contents when the entity is found.
    """
    result = get_files_from_entity(
        entity_name="QuantumCircuit",
        version_number="0.45.0",
    )
    assert result == [
        "/usr/local/lib/python3.10/site-packages/qiskit/circuit/quantumcircuit.py"
    ]


def test_preprocess_extract_entities_success():
    """
    Test that preprocess_extract_entities runs the script in Docker and returns the expected output.
    """
    with tempfile.TemporaryDirectory() as temp_output_dir:
        result = preprocess_extract_entities(
            image_name="qiskit_image_0.45.0",
            directory_to_scan="/usr/local/lib/python3.10/site-packages/qiskit",
            output_dir=temp_output_dir,
        )
        lines = result.splitlines()
        not_empty_lines = [line for line in lines if line.strip()]
        last_line = not_empty_lines[-1]
        assert last_line == "API extraction completed."
        # check that the entities.json file is created
        assert "entities.json" in os.listdir(temp_output_dir)
