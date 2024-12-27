"""Generator that uses a large language model to generate fuzzing programs.

It uses the Fuzz4All framework to generate fuzzing programs.

It has two stages:
1. Gather relevant information for fuzzing, usually from a specific website or
github repository.
2. Auto-prompting: find the best prompt to generate valid programs to feed to the
platform.
3. Fuzzing: generate programs using the best prompt found. Occasionally, using
the mutation strategies
    - generate a new program from scratch
    - mutate an existing program (usually the last one generated)
    - generate a semantically equivalent program (usually the last one generated)


Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports
Make sure to add a function and call that function only in the main cli command.
The goal is to be able to import that function also from other files.


"""


import dspy
import os
import ast
import time
import random
from pathlib import Path
from generators.strategies.base_generation import GenerationStrategy
from groq import GroqError
from typing import List, Dict, Any


# check if the GROQ_API_KEY is set
if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = Path("groq_token.txt").read_text().strip()

# lm = dspy.LM('groq/gemma-7b-it')
# lm = dspy.LM('groq/llama-3.3-70b-versatile')
lm = dspy.LM('groq/llama-3.1-70b-versatile')


class GenerateQuantumCircuit(dspy.Signature):
    """Generate a quantum circuit in Qiskit for the purpose of fuzzing."""
    random_seed: int = dspy.InputField(
        desc="The random seed to use for generating the quantum circuit")
    documentation: str = dspy.InputField(
        desc="An extract of the documentation of Qiskit")
    python_code: str = dspy.OutputField()


class LLMGenerationStrategy(GenerationStrategy):
    """It generates Qiskit circuits using the LLM model."""

    def __init__(self, path_to_documentation: Path, *args, **kwargs):
        self.path_to_documentation = path_to_documentation
        self.documentation_content = self._load_documentation()
        dspy.configure(lm=lm)
        self.generator = dspy.ChainOfThought(
            GenerateQuantumCircuit, temperature=1.5)
        self.retries = 0

    def _load_documentation(self) -> str:
        """Load the documentation content to generate prompts."""
        with open(self.path_to_documentation, 'r') as f:
            return f.read()

    def _clean_tags(self, text: str) -> str:
        """Removes the tags from the text."""
        text = text.strip()
        if text.startswith("```"):
            # remove the first line
            text = text[text.find("\n") + 1:]
        if text.endswith("```"):
            # remove the last line
            text = text[:text.rfind("\n")]
        return text

    def _surround_imports_with_try_except(self, python_code: str) -> str:
        """Surrounds the imports with a try-except block.

        This uses the AST module to parse the Python code and then
        surround the imports with a try-except block.
        """
        try:
            root = ast.parse(python_code)
        except SyntaxError:
            return python_code  # Return the original code if it is not parsable

        for node in root.body:
            if isinstance(
                    node, ast.Import) or isinstance(
                    node, ast.ImportFrom):
                # surround the import with a try-except block
                try_except = ast.Try(
                    body=[node],
                    handlers=[
                        ast.ExceptHandler(
                            type=ast.Name(id='Exception', ctx=ast.Load()),
                            name='e',
                            body=[
                                ast.Expr(
                                    value=ast.Call(
                                        func=ast.Name(id='print', ctx=ast.Load()),
                                        args=[ast.Name(id='e', ctx=ast.Load())],
                                        keywords=[]
                                    )
                                )
                            ]
                        )
                    ],
                    orelse=[],
                    finalbody=[]
                )
                root.body[root.body.index(node)] = try_except

        try:
            return ast.unparse(root)
        except Exception:
            return python_code  # Return the original code if unparse fails

    def generate(self) -> str:
        """Generates a Qiskit circuit using the LLM model."""
        try:
            res = self.generator(
                random_seed=random.randint(0, 1000),
                documentation=self.documentation_content)
            self.retries = 0
        except Exception as e:
            print(f"Error: {e}")
            print("Waiting for 60 seconds before retrying ...")
            time.sleep(60)
            self.retries += 1
            if self.retries >= 10:
                raise e
            return self.generate()
        python_code = res.python_code
        python_code = self._clean_tags(python_code)
        python_code = self._surround_imports_with_try_except(python_code)
        return python_code


class GenerateMultipleCircuit(dspy.Signature):
    """Generate multiple quantum circuits in Qiskit.

    Each circuit:
    - has enough classical bits to measure all qubits
    - has unusual gates
    - registers are referenced with the number only
    - includes intermediate measurements
    - is valid Qiskit python code (statements end with a newline)

    The circuits must have only circuit objects and no execution or transpilation."""
    n_circuits: int = dspy.InputField(
        desc="The number of circuits to generate")
    max_qubits: int = dspy.InputField(
        desc="The maximum number of qubits to use in each circuit")
    n_ops_per_circuit: int = dspy.InputField(
        desc="The number of operations to include in each circuit")
    circuits: List[str] = dspy.OutputField()


class GenerateMultipleCircuits(dspy.Module):
    def __init__(self):
        self.prog = dspy.ChainOfThought(
            GenerateMultipleCircuit, temperature=1)

    def forward(self, n_circuits: int, max_qubits: int, n_ops_per_circuit: int) -> Dict[str, Any]:
        results = self.prog(n_circuits=n_circuits,
                            max_qubits=max_qubits,
                            n_ops_per_circuit=n_ops_per_circuit)
        return results


class LLMMultiCircuitsGenerationStrategy(GenerationStrategy):
    """It generates multiple Qiskit circuits using the LLM model."""

    def __init__(self, *args, **kwargs):
        dspy.configure(lm=lm)
        self.generator = GenerateMultipleCircuits()
        self.precomputed_circuits = []

    def generate(self) -> List[str]:
        """Generates multiple Qiskit circuits using the LLM model."""
        if not self.precomputed_circuits:
            try:
                self.precomputed_circuits = self.generator(
                    n_circuits=random.randint(3, 10),
                    max_qubits=random.randint(3, 7),
                    n_ops_per_circuit=random.randint(20, 40))["circuits"]
            except Exception as e:
                print(f"Error: {e}")
                print("Waiting for 60 seconds before retrying ...")
                time.sleep(60)
                return self.generate()
        return self.precomputed_circuits.pop(0)
