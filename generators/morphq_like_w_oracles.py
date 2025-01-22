"""Script to generate simple Qiskit program following the MorphQ template.

It generates program in the format given below and stores it in a file.

--output_folder: str path to where to store the generated py programs. (default: program_bank)
    the new programs will be stored in a subfolder with the name the data and time
    e.g. 2024_09_30__22:50__qiskit (note the end with the title of the platform)
--prompt: str. path to the prompt template (default: generators/morphq.jinja)
--max_n_qubits: int. maximum number of qubits in the circuit (default: 5)
--max_n_gates: int. maximum number of gates in the circuit (default: 10)

This is the content of the jinja template to use to generate circuits
```jinja
# Section: Prologue
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Session, Sampler

# Section: Circuit
qr = QuantumRegister({{N_QUBITS}}, name='qr')
cr = ClassicalRegister({{N_QUBITS}}, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')

# Apply gate operations
{{GATE_OPS}}

# Section: Measurement
qc.measure(qr, cr)

# Section: Execution
# Run the sampler job locally using AerSimulator.
# Session syntax is supported but ignored.
aer_sim = AerSimulator()

# The session is used but ignored in AerSimulator.
sampler = Sampler(session=aer_sim)
result = sampler.run([qc]).result()

# Section: Results
counts = result.get_counts(qc)
print(f"Measurement results: {counts}")

```

N_QUBITS: int. Number of qubits in the circuit
GATE_OPS: str. python statements to add gates to the circuit
These are sampled randomly from the possible values:
- N_QUBITS: 1 to max_n_qubits
- GATE_OPS: random sequence of gates generated with
```python
def generate_qiskit_code(
        circuit_var: str, quantum_reg_var: str, classical_reg_var: str,
        max_qubits: int, max_bits: int, num_statements: int) -> List[str]
# from generators.qiskit_gate_gen import generate_qiskit_code
```



# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib every time that paths are checked, created or composed.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate

Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports

"""

import os
import random
import json
import click
from pathlib import Path
from datetime import datetime
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
from typing import List, Tuple, Dict, Any, Optional
from rich.console import Console
from generators.qiskit_gate_gen import generate_qiskit_code
from uuid import uuid4
import docker
from qiskit import QuantumCircuit
from qiskit.qasm2 import load, dumps
import pickle
import time
from generators.strategies.base_generation import GenerationStrategy
from generators.strategies.iteration_v001 import SPIUKnittingGenerationStrategy
from generators.strategies.llm_generator import (
    LLMGenerationStrategy,
    LLMMultiCircuitsGenerationStrategy,
    LLMAPIBasedGenerationStrategy,
    LLMAPIwithMigrationGenerationStrategy
)
from generators.strategies.fixed_files_generator import (
    TestSuiteOnlyGenerationStrategy
)
from generators.source_code_manipulation import (
    get_source_code_functions_w_prefix,
    get_entire_source_code_module
)
from abc import ABC, abstractmethod
import validate.functions_qasm_export as export_functions
import validate.functions_qasm_import as import_functions
import validate.functions_qasm_compare as compare_functions
import validate.functions_optimize as optimize_functions
import validate.functions_oracle_calls as oracle_functions

from generators.combine_circuits import combine_circuits

from generators.docker_tooling import (
    run_program_in_docker_pypi
)

console = Console(color_system=None)


def generate_output_folder(base_folder: Path, platform: str) -> Path:
    """Generates an output folder path with the current date and time."""
    timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M')
    output_path = base_folder / f"{timestamp}__{platform}"
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def load_jinja_template(template_path: Path) -> Template:
    """Loads a Jinja template from the specified file."""
    with open(template_path, 'r') as f:
        template_content = f.read()
    return Template(template_content)


class RandomGenerationStrategy(GenerationStrategy):
    """Random generation strategy for Qiskit circuits."""

    def __init__(self, max_n_qubits: int, max_n_gates: int, *args, **kwargs):
        self.max_n_qubits = max_n_qubits
        self.max_n_gates = max_n_gates

    def generate(self) -> str:
        """Generates gate operations using Qiskit gate generator."""
        gate_ops = generate_qiskit_code(
            circuit_var='qc',
            quantum_reg_var='qr',
            classical_reg_var='cr',
            max_qubits=self.max_n_qubits,
            max_bits=self.max_n_qubits,
            num_statements=self.max_n_gates
        )
        current_file_folder = Path(__file__).parent
        circuit_template = current_file_folder / 'circuit_random_ops.jinja'
        with open(circuit_template, 'r') as f:
            template_content = f.read()
        template = Template(template_content)
        source_code_gate_ops = "\n".join(gate_ops)
        return template.render(
            N_QUBITS=self.max_n_qubits,
            GATE_OPS=source_code_gate_ops,
            TIMESTAMP=str(time.time())
        )


class CircuitFragmentsGenerationStrategy(GenerationStrategy):
    """It  samples existing QASM files to generate Qiskit circuits."""

    def __init__(self, qasm_folder: Path, *args, **kwargs):
        self.qasm_folder = qasm_folder

    def generate(self) -> str:
        """Generates gate operations by sampling a QASM file from the folder."""
        qasm_files = list(self.qasm_folder.glob('*.qasm'))
        if not qasm_files:
            raise FileNotFoundError(
                "No QASM files found in the specified seed folder.")
        selected_qasm_file = random.choice(qasm_files)
        with open(selected_qasm_file, 'r') as f:
            qasm_content = f.read()
        env = Environment(loader=FileSystemLoader(Path(__file__).parent))
        circuit_template = env.get_template('circuit_qasm_embedded.jinja')
        return circuit_template.render(
            QASM_STRING=qasm_content,
            QASM_FILENAME=selected_qasm_file.name,
            TIMESTAMP=str(time.time()))


class SequentialKnittingGenerationStrategy(GenerationStrategy):
    """It combines two circuits sequentially to generate Qiskit circuits."""

    def __init__(
            self, seed_programs_folder: Path,
            program_extensions: List[str] = [".pkl", ".qasm"],
            *args, **kwargs):
        self.seed_programs_folder = seed_programs_folder
        self.program_extensions = program_extensions

    def generate(self) -> str:
        """Combine two circuits sequentially.

        It could work with both QASM and PKL files.
        """
        qasm_files = list(self.seed_programs_folder.glob('*.qasm'))
        pkl_files = list(self.seed_programs_folder.glob('*.pkl'))
        if not qasm_files and not pkl_files:
            raise FileNotFoundError(
                "No QASM or PKL files found in the specified seed folder.")
        selected_circuits = self._sample_group_until_success(
            qasm_files + pkl_files)
        sel_files, sel_circuits = zip(*selected_circuits)
        combined_circuit = combine_circuits(*sel_circuits)
        env = Environment(loader=FileSystemLoader(Path(__file__).parent))
        circuit_template = env.get_template('circuit_qasm_embedded.jinja')
        return circuit_template.render(
            QASM_STRING=dumps(combined_circuit),
            QASM_FILENAME=f"combined_{sel_files[0].stem}_{sel_files[1].stem}.qasm",
            TIMESTAMP=str(time.time()))

    def _load_circuit(self, file_path: Path) -> QuantumCircuit:
        """Load a quantum circuit from a file."""
        if file_path.suffix == ".qasm":
            return load(file_path)
        elif file_path.suffix == ".pkl":
            return pickle.load(file_path.open("rb"))

    def _sample_group_until_success(
            self, program_files: List[Path], sample_size: int = 2) -> List[Tuple[Path, QuantumCircuit]]:
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


def save_program_to_file(
        output_path: Path, program_code: str, file_name: str) -> None:
    """Saves the generated Qiskit program to a file."""
    file_path = output_path / file_name
    with open(file_path, 'w') as f:
        f.write(program_code)
    console.log(f"Program saved to: {file_path}")


def get_generation_strategy(
        strategy_name: str, **kwargs) -> GenerationStrategy:
    """Returns the appropriate generation strategy object based on the strategy name."""
    if strategy_name == 'test_suite_only':
        return TestSuiteOnlyGenerationStrategy(
            seed_programs_folder=kwargs['seed_program_folder']
        )
    elif strategy_name == 'random':
        return RandomGenerationStrategy(
            max_n_qubits=kwargs['max_n_qubits'],
            max_n_gates=kwargs['max_n_gates']
        )
    elif strategy_name == 'circuit_fragments':
        return CircuitFragmentsGenerationStrategy(
            qasm_folder=kwargs['seed_program_folder']
        )
    elif strategy_name == 'sequential_knitting':
        return SequentialKnittingGenerationStrategy(
            seed_programs_folder=kwargs['seed_program_folder'],
            program_extensions=kwargs.get(
                'program_extensions', [".qasm", ".pkl"]))
    elif strategy_name == 'spiu_knitting':
        return SPIUKnittingGenerationStrategy(
            seed_programs_folder=kwargs['seed_program_folder'],
            program_extensions=kwargs.get(
                'program_extensions', [".qasm", ".pkl"]))
    elif strategy_name == 'llm_generation':
        return LLMGenerationStrategy(
            path_to_documentation=kwargs['path_to_documentation'],
        )
    elif strategy_name == 'llm_multi_circuits_generation':
        return LLMMultiCircuitsGenerationStrategy()
    elif strategy_name == 'llm_api_based_generation':
        return LLMAPIBasedGenerationStrategy(
            api_file=kwargs['api_file']
        )
    elif strategy_name == 'llm_api_with_migration':
        return LLMAPIwithMigrationGenerationStrategy(
            api_file=kwargs['api_file'],
            migration_dir=kwargs['migration_dir']
        )
    else:
        raise ValueError(f"Unknown generation strategy: {strategy_name}")


@ click.command()
@ click.option('--output_folder', default='program_bank', type=str,
               required=True, help="Folder to store the generated programs.")
@ click.option('--prompt', default='generators/scaffold_oracles.jinja',
               type=Path, required=True, help="Path to the prompt template.")
@ click.option('--circuit_generation_strategy', default='random', type=str,
               required=True, help="Strategy to generate the circuit.")
@ click.option('--max_n_qubits', default=5, type=int, required=True,
               help="Maximum number of qubits in the circuit.")
@ click.option('--max_n_gates', default=10, type=int, required=True,
               help="Maximum number of gates in the circuit.")
@ click.option('--max_n_programs', default=10, type=int, required=True,
               help="Maximum number of programs to generate.")
@ click.option('--perform_execution', is_flag=True, default=False,
               help="Flag to indicate whether to perform execution.")
@ click.option('--seed', default=None, type=int,
               help="Seed for random reproducible generation (debug).")
@ click.option('--seed_program_folder', default=None, type=Path,
               help="Optional folder containing QASM/pkl files for seeding.")
@ click.option('--path_to_documentation', default=None, type=Path,
               help="Path to the documentation file for LLM generation.")
@ click.option('--api_file', default=None, type=Path,
               help="Path to the API file for API-based generation.")
@ click.option('--migration_dir', default=None, type=Path,
               help="Path to the migration directory.")
@ click.option('--model_dspy_name_id', default='qiskit',
               help="Name of the model in dspy.")
@ click.option('--active_oracles', multiple=True,
               help="List of active oracles to use in the generated programs.")
def main(
        output_folder: str, prompt: Path, circuit_generation_strategy: str,
        max_n_qubits: int, max_n_gates: int, max_n_programs: int,
        perform_execution: bool, seed: Optional[int],
        seed_program_folder: Optional[Path],
        path_to_documentation: Optional[Path],
        api_file: Optional[Path],
        migration_dir: Optional[Path],
        model_dspy_name_id: str,
        active_oracles: List[str]
):
    """
    CLI to generate Qiskit programs based on a MorphQ template and save them to files.
    """
    console.log("Starting Qiskit program generation...")

    # Set the random seed if provided
    if seed is not None:
        random.seed(seed)
    console.log(f"Random seed set to: {seed}")

    # Generate the output folder based on the current date and time
    output_path = generate_output_folder(
        base_folder=Path(output_folder),
        platform='qiskit'
    )

    # Load the Jinja template
    template = load_jinja_template(template_path=prompt)

    import dspy
    lm = dspy.LM(model_dspy_name_id, cache=False)
    dspy.configure(lm=lm)

    # Generate the circuit code
    generation_strategy = get_generation_strategy(
        strategy_name=circuit_generation_strategy,
        max_n_qubits=max_n_qubits,
        max_n_gates=max_n_gates,
        seed_program_folder=seed_program_folder,
        path_to_documentation=path_to_documentation,
        api_file=api_file,
        migration_dir=migration_dir
    )
    for i in range(max_n_programs):
        qc_circuit_source = generation_strategy.generate()

        # Check if the generation strategy returns a tuple/list with program and metadata
        metadata = dict({})
        if isinstance(qc_circuit_source, (tuple, list)) and len(
                qc_circuit_source) == 2:
            qc_circuit_source, metadata = qc_circuit_source

        # get export functions
        export_functions_section = get_source_code_functions_w_prefix(
            prefix='export_to_qasm_with_', module=export_functions)

        # get import functions
        import_functions_section = get_source_code_functions_w_prefix(
            prefix='import_from_qasm_with_', module=import_functions)

        # get optimize functions
        optimize_functions_section = get_source_code_functions_w_prefix(
            prefix='optimize_with_', module=optimize_functions)

        # get compare functions
        compare_functions_section = get_source_code_functions_w_prefix(
            prefix='compare_', module=compare_functions)

        # get oracle functions
        oracle_functions_section = get_entire_source_code_module(
            module=oracle_functions
        )

        # oracles to use
        active_oracles_call_statements = "\n".join([
            f"{oracle}()" for oracle in active_oracles
        ])

        # Render the program code using the template
        program_code = template.render(
            QC_CIRCUIT_CODE=qc_circuit_source,
            FUNCTIONS_EXPORT_TO_QASM=export_functions_section,
            FUNCTION_IMPORT_FROM_QASM=import_functions_section,
            FUNCTIONS_OPTIMIZE=optimize_functions_section,
            FUNCTIONS_COMPARE=compare_functions_section,
            TARGET_QC='qc',
            PERFORM_EXECUTION=perform_execution,
            FUNCTIONS_ORACLE=oracle_functions_section,
            ORACLE_TO_USE=active_oracles_call_statements,
        )
        # Get unique ID
        uuid_str = str(uuid4())[:6]
        # Generate a zero-padded incremental ID
        incremental_id = str(i + 1).zfill(7)

        # Save the generated program to a file
        save_program_to_file(
            output_path=output_path,
            program_code=program_code,
            file_name=f"{incremental_id}_{uuid_str}.py"
        )

        # Save only the circuit code to a file
        save_program_to_file(
            output_path=output_path,
            program_code=qc_circuit_source,
            file_name=f"{incremental_id}_{uuid_str}_circuit.py"
        )

        # Save metadata to a file
        metadata_file_name = f"{incremental_id}_{uuid_str}_metadata.json"
        metadata_path = output_path / metadata_file_name
        with open(metadata_path, 'w') as metadata_file:
            json.dump(metadata, metadata_file)
        console.log(f"Metadata saved to: {metadata_path}")

        # Run the generated program in Docker
        file_name = f"{incremental_id}_{uuid_str}.py"
        run_program_in_docker_pypi(folder_with_file=output_path,
                                   file_name=file_name,
                                   timeout=30,
                                   console=console)

    console.log("Qiskit program generation completed.")


if __name__ == '__main__':
    main()
