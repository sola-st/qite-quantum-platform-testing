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
import click
from pathlib import Path
from datetime import datetime
from jinja2 import Template
from typing import List, Tuple, Dict, Any, Optional
from rich.console import Console
from generators.qiskit_gate_gen import generate_qiskit_code
from uuid import uuid4
import docker
from generators.source_code_manipulation import get_source_code_functions_w_prefix
from abc import ABC, abstractmethod
import validate.functions_qasm_export as export_functions
import validate.functions_qasm_import as import_functions
import validate.functions_qasm_compare as compare_functions

from generators.docker_tooling import (
    run_program_in_docker,
    run_program_in_docker_w_timeout
)

console = Console()


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


class GenerationStrategy(ABC):
    """Abstract base class for generation strategies."""

    @abstractmethod
    def generate(self) -> str:
        """Generates the circuit code."""
        pass


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
            GATE_OPS=source_code_gate_ops
        )


class CircuitFragmentsGenerationStrategy(GenerationStrategy):
    """It re-combines existing QASM files to generate Qiskit circuits."""

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
        current_file_folder = Path(__file__).parent
        circuit_template = current_file_folder / 'circuit_fragment_single.jinja'
        with open(circuit_template, 'r') as f:
            template_content = f.read()
        template = Template(template_content)
        return template.render(
            QASM_STRING=qasm_content,
            QASM_FILENAME=selected_qasm_file.name)


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
    if strategy_name == 'random':
        return RandomGenerationStrategy(
            max_n_qubits=kwargs['max_n_qubits'],
            max_n_gates=kwargs['max_n_gates']
        )
    elif strategy_name == 'circuit_fragments':
        return CircuitFragmentsGenerationStrategy(
            qasm_folder=kwargs['qasm_folder']
        )
    else:
        raise ValueError(f"Unknown generation strategy: {strategy_name}")


@click.command()
@click.option('--output_folder', default='program_bank', type=str,
              required=True, help="Folder to store the generated programs.")
@click.option('--prompt', default='generators/scaffold_oracles.jinja',
              type=Path, required=True, help="Path to the prompt template.")
@click.option('--circuit_generation_strategy', default='random', type=str,
              required=True, help="Strategy to generate the circuit.")
@click.option('--max_n_qubits', default=5, type=int, required=True,
              help="Maximum number of qubits in the circuit.")
@click.option('--max_n_gates', default=10, type=int, required=True,
              help="Maximum number of gates in the circuit.")
@click.option('--max_n_programs', default=10, type=int, required=True,
              help="Maximum number of programs to generate.")
@click.option('--perform_execution', is_flag=True, default=False,
              help="Flag to indicate whether to perform execution.")
@click.option('--seed', default=None, type=int,
              help="Seed for random reproducible generation (debug).")
@click.option('--seed_qasm_folder', default=None, type=Path,
              help="Optional folder containing QASM files for seeding.")
def main(
        output_folder: str, prompt: Path, circuit_generation_strategy: str,
        max_n_qubits: int, max_n_gates: int, max_n_programs: int,
        perform_execution: bool, seed: Optional[int],
        seed_qasm_folder: Optional[Path]):
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

    for i in range(max_n_programs):
        # Generate the circuit code
        generation_strategy = get_generation_strategy(
            strategy_name=circuit_generation_strategy,
            max_n_qubits=max_n_qubits,
            max_n_gates=max_n_gates,
            qasm_folder=seed_qasm_folder
        )
        qc_circuit_source = generation_strategy.generate()

        # get export functions
        export_functions_section = get_source_code_functions_w_prefix(
            prefix='export_to_qasm_with_', module=export_functions)

        # get import functions
        import_functions_section = get_source_code_functions_w_prefix(
            prefix='import_from_qasm_with_', module=import_functions)

        # get compare functions
        compare_functions_section = get_source_code_functions_w_prefix(
            prefix='compare_', module=compare_functions)

        # Render the program code using the template
        program_code = template.render(
            QC_CIRCUIT_CODE=qc_circuit_source,
            FUNCTIONS_EXPORT_TO_QASM=export_functions_section,
            FUNCTION_IMPORT_FROM_QASM=import_functions_section,
            FUNCTIONS_COMPARE=compare_functions_section,
            TARGET_QC='qc',
            PERFORM_EXECUTION=perform_execution
        )

        # Save the generated program to a file
        uuid_str = str(uuid4())[:6]
        save_program_to_file(
            output_path=output_path,
            program_code=program_code,
            file_name=f"qiskit_circuit_{max_n_qubits}q_{max_n_gates}g_{i+1}_{uuid_str}.py"
        )

        # Run the generated program in Docker
        file_name = f"qiskit_circuit_{max_n_qubits}q_{max_n_gates}g_{i+1}_{uuid_str}.py"
        run_program_in_docker_w_timeout(folder_with_file=output_path,
                                        file_name=file_name, console=console)

    console.log("Qiskit program generation completed.")


if __name__ == '__main__':
    main()
