import pytest
import tempfile
import shutil
from pathlib import Path
from generators.morphq_like_w_oracles import (
    SequentialKnittingGenerationStrategy
)
from qiskit import QuantumCircuit
from qiskit.qasm2 import dumps
import pickle


@pytest.fixture
def temp_seed_folder():
    """Fixture to create a temporary seed folder with sample QASM and PKL files."""
    temp_dir = tempfile.mkdtemp()
    seed_folder = Path(temp_dir)

    # Create sample QASM file
    qasm_circuit = QuantumCircuit(2)
    qasm_circuit.cx(0, 1)
    qasm_file = seed_folder / "sample.qasm"
    with open(qasm_file, 'w') as f:
        f.write(dumps(qasm_circuit))

    # Create sample PKL file
    pkl_circuit = QuantumCircuit(2)
    pkl_circuit.h(0)
    pkl_file = seed_folder / "sample.pkl"
    with open(pkl_file, 'wb') as f:
        pickle.dump(pkl_circuit, f)

    yield seed_folder

    # Cleanup
    shutil.rmtree(temp_dir)


def test_generate_no_files():
    """Test SequentialKnittingGenerationStrategy.generate when no QASM or PKL files are present."""
    empty_folder = tempfile.mkdtemp()
    strategy = SequentialKnittingGenerationStrategy(
        seed_programs_folder=Path(empty_folder))

    with pytest.raises(FileNotFoundError, match="No QASM or PKL files found in the specified seed folder."):
        strategy.generate()

    shutil.rmtree(empty_folder)


def test_generate_with_files(temp_seed_folder):
    """Test SequentialKnittingGenerationStrategy.generate with QASM and PKL files present."""
    strategy = SequentialKnittingGenerationStrategy(
        seed_programs_folder=temp_seed_folder)
    result = strategy.generate()

    assert "combined_sample_sample.qasm" in result
    assert "OPENQASM" in result


def test_load_circuit_qasm(temp_seed_folder):
    """Test SequentialKnittingGenerationStrategy._load_circuit with a QASM file."""
    strategy = SequentialKnittingGenerationStrategy(
        seed_programs_folder=temp_seed_folder)
    qasm_file = temp_seed_folder / "sample.qasm"
    circuit = strategy._load_circuit(qasm_file)

    assert isinstance(circuit, QuantumCircuit)
    assert circuit.width() == 2


def test_load_circuit_pkl(temp_seed_folder):
    """Test SequentialKnittingGenerationStrategy._load_circuit with a PKL file."""
    strategy = SequentialKnittingGenerationStrategy(
        seed_programs_folder=temp_seed_folder)
    pkl_file = temp_seed_folder / "sample.pkl"
    circuit = strategy._load_circuit(pkl_file)

    assert isinstance(circuit, QuantumCircuit)
    assert circuit.width() == 2
