import pytest
from pathlib import Path
from generators.strategies.fixed_files_generator import (
    TestSuiteOnlyGenerationStrategy
)


@pytest.fixture
def qasm_folder(tmp_path):
    """Fixture to create a temporary QASM folder with sample files."""
    qasm_folder = tmp_path / "seeds_qasm"
    qasm_folder.mkdir()
    for i in range(3):
        (qasm_folder / f"sample_{i}.qasm").write_text(f"// QASM content {i}")
    return qasm_folder


def test_generate_three_times(qasm_folder):
    """Test that the generation strategy can be called 3 times and then raises an exception."""
    strategy = TestSuiteOnlyGenerationStrategy(qasm_folder)

    # Generate three times successfully
    for _ in range(3):
        result = strategy.generate()
        print(result)
        assert "OPENQASM 2.0;" in result
        assert "<START_GATES>" in result
        assert "<END_GATES>" in result
        assert "TIMESTAMP" in result

    # Fourth call should raise an exception
    with pytest.raises(FileNotFoundError, match="No more unused QASM files available."):
        strategy.generate()


def test_generate_with_existing_files():
    """Test that the generation strategy works with existing QASM files in a specific folder."""
    qasm_folder = Path("tests/artifacts/qasm_quantum_circuits")
    strategy = TestSuiteOnlyGenerationStrategy(qasm_folder)

    # Assuming there are at least 3 files in the folder
    for _ in range(3):
        result = strategy.generate()
        assert "OPENQASM 2.0;" in result
        assert "<START_GATES>" in result
        assert "<END_GATES>" in result
        assert "TIMESTAMP" in result

        print(result)

    # Fourth call should raise an exception
    with pytest.raises(FileNotFoundError, match="No more unused QASM files available."):
        strategy.generate()
