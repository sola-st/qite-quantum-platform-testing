from pathlib import Path
from typing import List, Tuple
from qiskit import QuantumCircuit
from qiskit.qasm2 import load, dumps
from jinja2 import Environment, FileSystemLoader
import random
import pickle
from generators.strategies.base_generation import GenerationStrategy
from generators.knitting.unitary_knitter import UnitaryKnitter
from generators.knitting.parallel_knitter import ParallelKnitter
from generators.knitting.interleaved_knitter import InterleavedKnitter
from generators.knitting.sequential_knitter import SequentialKnitter

from generators.knitting.sanitizers import AssignRandomParamsSanitizer
from generators.combine_circuits import assign_random_params

from rich.console import Console

console = Console()


class SPIUKnittingGenerationStrategy(
        GenerationStrategy):
    """Combines circuits sequentially, in parallel, and interleaved with unitary operations.

    SPIU stands for Sequential, Parallel, Interleaved, and Unitary operations.
    This strategy combines quantum circuits using these four methods to create a
    more complex and potentially more powerful quantum circuit. The
    SPIUKnittingGenerationStrategy class implements this by loading quantum
    circuits from specified files, sampling them, and then combining them using
    one of the four knitting strategies: SequentialKnitter, ParallelKnitter,
    InterleavedKnitter, and UnitaryKnitter.

    """

    def __init__(
            self, seed_programs_folder: Path,
            program_extensions: List[str] = [".pkl", ".qasm"],
            *args, **kwargs):
        self.seed_programs_folder = seed_programs_folder
        self.program_extensions = program_extensions

    def _dummy_circuit(self) -> QuantumCircuit:
        toy_qc = QuantumCircuit(1, 1)
        toy_qc.h(0)
        toy_qc.measure(0, 0)
        return toy_qc

    def generate(self) -> str:
        """Generate a combined circuit using sequential, parallel, and interleaved unitary operations."""
        program_files = list(self.seed_programs_folder.glob('*'))
        if not program_files:
            raise FileNotFoundError(
                "No program files found in the specified seed folder.")

        selected_circuits = self._sample_group_until_success(program_files)
        sel_files, sel_circuits = zip(*selected_circuits)
        combined_circuit, provenance = self._combine_circuits(sel_circuits)

        try:
            qasm_combined = dumps(combined_circuit)
        except Exception as e:
            console.log(f"Error dumping QASM dumps of combined circuit: {e}")
            qasm_combined = dumps(self._dummy_circuit())

        env = Environment(loader=FileSystemLoader(
            Path(__file__).parent.parent))
        circuit_template = env.get_template('circuit_qasm_embedded.jinja')
        return circuit_template.render(
            QASM_STRING=qasm_combined,
            QASM_FILENAME=f"combined_{sel_files[0].stem}_{sel_files[1].stem}.qasm . strategy: {provenance}"
        )

    def _load_circuit(self, file_path: Path) -> QuantumCircuit:
        """Load a quantum circuit from a file."""
        if file_path.suffix == ".qasm":
            return load(file_path)
        elif file_path.suffix == ".pkl":
            return pickle.load(file_path.open("rb"))

    def _sample_group_until_success(
            self, program_files: List[Path],
            sample_size: int = 2) -> List[
            Tuple[Path, QuantumCircuit]]:
        """Sample two programs until both can be loaded successfully."""
        circuit_group = []
        while len(circuit_group) < sample_size:
            selected_file = random.sample(program_files, 1)
            try:
                qc_circuit = self._load_circuit(selected_file[0])
                circuit_group.append((selected_file[0], qc_circuit))
            except Exception:
                pass
        return circuit_group

    def _combine_circuits(
            self, circuits: List[QuantumCircuit]) -> Tuple[QuantumCircuit, str]:
        """Combine circuits using sequential, parallel, and interleaved unitary operations."""
        knitter_classes = [
            SequentialKnitter,
            ParallelKnitter,
            InterleavedKnitter,
            UnitaryKnitter]
        selected_knitter_class = random.choice(knitter_classes)
        console.log(f"Selected knitter class: {selected_knitter_class}")

        try:
            knitter = selected_knitter_class(circuits[0], circuits[1])
            combined_circuit = knitter.combine_circuits()

            sanitizer_unbound_parameters = AssignRandomParamsSanitizer()
            sanitized_qc = sanitizer_unbound_parameters.sanitize(
                combined_circuit)

            sanitized_qc = assign_random_params(sanitized_qc)
        except Exception as e:
            console.log(f"Error during combination: {e}")
            sanitized_qc = self._dummy_circuit()

        return sanitized_qc, str(selected_knitter_class)
