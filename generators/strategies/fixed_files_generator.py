import random
import time
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from generators.strategies.base_generation import GenerationStrategy
from qiskit.qasm2 import dumps
from qiskit import QuantumCircuit


class TestSuiteOnlyGenerationStrategy(GenerationStrategy):
    """It iterates over a list of circuit files to generate Qiskit circuits."""

    def __init__(self, seed_programs_folder: Path, *args, **kwargs):
        self.seed_programs_folder = seed_programs_folder
        self._used_files = set()

    def generate(self) -> str:
        """Generates gate operations by sampling a circuit file from the folder."""
        qasm_files = list(self.seed_programs_folder.glob('*.qasm'))
        pkl_files = list(self.seed_programs_folder.glob('*.pkl'))
        if not qasm_files and not pkl_files:
            raise FileNotFoundError(
                "No QASM or PKL files found in the specified seed folder.")
        sampleable_files = qasm_files + pkl_files

        available_files = [f for f in sampleable_files
                           if f not in self._used_files]
        if not available_files:
            raise FileNotFoundError("No more unused QASM files available.")

        selected_qasm_file = random.choice(available_files)
        self._used_files.add(selected_qasm_file)

        with open(selected_qasm_file, 'r') as f:
            qc: QuantumCircuit = self.load_circuit(selected_qasm_file)
            try:
                qasm_content = dumps(qc)
            except Exception as e:
                print(
                    f"Error while processing {selected_qasm_file}: {e}. "
                    "Trying again with a different file.")
                return self.generate()
        env = Environment(loader=FileSystemLoader(
            Path(__file__).parent.parent))
        circuit_template = env.get_template('circuit_qasm_embedded.jinja')
        return circuit_template.render(
            QASM_STRING=qasm_content,
            QASM_FILENAME=selected_qasm_file.name,
            TIMESTAMP=str(time.time()))
