from abc import ABC, abstractmethod
from pathlib import Path
import pickle
from qiskit import QuantumCircuit
from qiskit.qasm2 import load
import qiskit.qasm2 as qasm2


class GenerationStrategy(ABC):
    """Abstract base class for generation strategies."""

    @abstractmethod
    def generate(self) -> str:
        """Generates the circuit code."""
        pass

    def load_circuit(self, path: str) -> QuantumCircuit:
        """Load a quantum circuit from a file."""
        file_path = Path(path)
        if file_path.suffix == ".qasm":
            return load(
                file_path, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
        elif file_path.suffix == ".pkl":
            return pickle.load(file_path.open("rb"))
        else:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")
