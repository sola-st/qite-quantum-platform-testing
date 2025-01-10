import pytest
from aiexchange.knowledge_base.library import get_files_from_entity


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
