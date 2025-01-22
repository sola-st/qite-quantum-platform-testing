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
from typing import List, Dict, Any, Tuple
import json
from aiexchange.tools.docker_tools import run_qiskit_code_in_docker
from aiexchange.feedback.log_understanding import is_code_fixed
import aiexchange.tools.base_model_setup


# lm = dspy.LM('groq/gemma-7b-it')
# lm = dspy.LM('groq/llama-3.3-70b-versatile')
# lm = dspy.LM('groq/llama-3.1-70b-versatile')


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


class GenerateProgramFromAPI(dspy.Signature):
    """Generate a program inspired by this specific existing Qiskit API.

    It must:
    - only use Qiskit library and standard Python libraries
    - the given API must be imported and used (it is defined already, no need to define it)
    - be self-contained, without any external dependencies
    - include at least one QuantumCircuit object
    - import all the necessary modules / functions before using them
    - return only Python code (no backticks, no comments, no markdown) in the
      field: generated_python_program
    """
    api_description: str = dspy.InputField(
        desc="The description of the API to inspire the program generation")
    api_signature: str = dspy.InputField(
        desc="The signature of the API to inspire the program generation")
    full_api_name: str = dspy.InputField(
        desc="The full name of the API to inspire the program generation")
    api_file_path: str = dspy.InputField(
        desc="The file path of the API to inspire the program generation")
    generated_python_program: str = dspy.OutputField(
        desc="The generated ptyhon program, which includes at least one QuantumCircuit object")
    variable_name_of_circuit: str = dspy.OutputField(
        desc="The variable name of the QuantumCircuit object")


class GenerateProgramFromAPIModule(dspy.Module):
    def __init__(self):
        self.prog = dspy.ChainOfThought(
            GenerateProgramFromAPI, temperature=1)

    def forward(self, api_description: str, api_signature: str,
                full_api_name: str, api_file_path: str) -> Dict[str, Any]:
        results = self.prog(api_description=api_description,
                            api_signature=api_signature,
                            full_api_name=full_api_name,
                            api_file_path=api_file_path)
        return results


class LLMAPIBasedGenerationStrategy(GenerationStrategy):
    """It generates a program inspired by a specific API using the LLM model."""

    def __init__(self, api_file: Path, *args, **kwargs):
        self.api_file = api_file
        if str(api_file).lower() in ["", "none", "null", "empty"]:
            self.api_file = None
        if self.api_file is not None:
            self.api_data = self._load_api_data()
        self.generator = GenerateProgramFromAPIModule()

    def _load_api_data(self) -> List[Dict[str, Any]]:
        """Load the API data from the JSON file."""
        with open(self.api_file, 'r') as f:
            return json.load(f)

    def _remove_backticks(self, python_code: str) -> str:
        """Removes the backticks from the Python code."""
        python_code = python_code.strip()
        if python_code.startswith("```"):
            # remove the first line
            python_code = python_code[python_code.find("\n") + 1:]
        if python_code.endswith("```"):
            # remove it from the end
            python_code = python_code[:-3]
        return python_code

    def generate(self) -> Tuple[str, Dict[str, Any]]:
        """Generates a program inspired by a specific API."""
        if not self.api_file:
            api_info: Dict[str, Any] = {
                "api_description": "No description available",
                "api_signature": "No signature available",
                "full_api_name": "No name available",
                "file_path": "No file path available"
            }
        else:
            api_info = random.choice(self.api_data)
        metadata = {}
        metadata["api_info"] = api_info
        try:
            res = self.generator(
                api_description=api_info["api_description"],
                api_signature=api_info["api_signature"],
                full_api_name=api_info["full_api_name"],
                api_file_path=api_info["file_path"])
            metadata["dspy_store"] = res._store
            lm = dspy.settings["lm"]
            last_interaction = lm.history[-1]
            metadata["llm_usage"] = last_interaction["usage"]
            metadata["llm_timestamp"] = last_interaction["timestamp"]
            metadata["llm_model"] = last_interaction["model"]
        except Exception as e:
            print(f"Error: {e}")
            print("Waiting for 60 seconds before retrying ...")
            time.sleep(60)
            return self.generate()
        return self._remove_backticks(
            res["generated_python_program"]), metadata


class MigrateProgram(dspy.Signature):
    """Migrate an existing program to the latest version of Qiskit.

    It must:
    - still use the same API as the existing code
    - use the provided migration context to guide the migration
    - only use Qiskit library and standard Python libraries
    - be self-contained, without any external dependencies
    - include at least one QuantumCircuit object
    - import all the necessary modules / functions before using them
    - return only Python code (no backticks, no comments, no markdown) in the
        field: migrated_python_program
    """
    api_description: str = dspy.InputField(
        desc="The description of the API to inspire the program migration")
    api_signature: str = dspy.InputField(
        desc="The signature of the API to inspire the program migration")
    full_api_name: str = dspy.InputField(
        desc="The full name of the API to inspire the program migration")
    api_file_path: str = dspy.InputField(
        desc="The file path of the API to inspire the program migration")
    migration_context: str = dspy.InputField(
        desc="The context to guide the migration")
    existing_code: str = dspy.InputField(
        desc="The existing code to be migrated")
    runtime_error: str = dspy.InputField(
        desc="The runtime error generated by the existing code")
    migrated_python_program: str = dspy.OutputField(
        desc="The migrated python program, which includes at least one QuantumCircuit object")
    variable_name_of_circuit: str = dspy.OutputField(
        desc="The variable name of the QuantumCircuit object")


class MigrateProgramModule(dspy.Module):
    def __init__(self):
        self.prog = dspy.ChainOfThought(
            MigrateProgram, temperature=1)

    def forward(self, api_description: str, api_signature: str,
                full_api_name: str, api_file_path: str,
                migration_context: str, existing_code: str,
                runtime_error: str) -> Dict[str, Any]:
        results = self.prog(api_description=api_description,
                            api_signature=api_signature,
                            full_api_name=full_api_name,
                            api_file_path=api_file_path,
                            migration_context=migration_context,
                            existing_code=existing_code,
                            runtime_error=runtime_error)
        return results


class LLMAPIwithMigrationGenerationStrategy(LLMAPIBasedGenerationStrategy):
    """It generates a program inspired by a specific API using the LLM model.

    It also migrates the program to the latest version of Qiskit.
    """

    def __init__(self, api_file: Path, migration_dir: Path, *args, **kwargs):
        super().__init__(api_file, *args, **kwargs)
        self.migration_dir = migration_dir
        self.image_starting_version = "qiskit_image_0.45.0"
        self.image_target_version = "qiskit_image_1.2.0"
        self.migration_context = self._load_migration_files()

    def _load_migration_files(self) -> str:
        """Load the migration files from the directory."""
        migration_context = ""
        file_header_template = ""
        file_header_template += "=" * 80 + "\n"
        file_header_template += "Migration File: {}\n"
        file_header_template += "=" * 80 + "\n"
        for file in self.migration_dir.glob("*.md"):
            with open(file, 'r') as f:
                file_content = f.read()
            file_header = file_header_template.format(file.name)
            migration_context += file_header + file_content + "\n"
        return migration_context

    def _migrate_program(
            self, python_code: str, api_info: Dict[str, Any], runtime_error: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Migrates the program to the latest version of Qiskit."""
        try:
            migrator = MigrateProgramModule()
            res = migrator(
                api_description=api_info["api_description"],
                api_signature=api_info["api_signature"],
                full_api_name=api_info["full_api_name"],
                api_file_path=api_info["file_path"],
                runtime_error=runtime_error,
                migration_context=self.migration_context,
                existing_code=python_code)
            migration_metadata = {}
            migration_metadata["dspy_store"] = res._store
            lm = dspy.settings["lm"]
            last_interaction = lm.history[-1]
            migration_metadata["llm_usage"] = last_interaction["usage"]
            migration_metadata["llm_timestamp"] = last_interaction["timestamp"]
            migration_metadata["llm_model"] = last_interaction["model"]
        except Exception as e:
            print(f"Error: {e}")
            print("Waiting for 60 seconds before retrying ...")
            time.sleep(60)
            return self._migrate_program(python_code, api_info)
        return self._remove_backticks(
            res["migrated_python_program"]), migration_metadata

    def generate(self) -> Tuple[str, Dict[str, Any]]:
        """Generates a program inspired by a specific API and migrates it to the latest version of Qiskit."""
        python_code, metadata = super().generate()
        log_first_generation = run_qiskit_code_in_docker(
            code=python_code,
            image_name=self.image_target_version
        )
        metadata["execution_feedback"] = [{
            "id": 1,
            "image": self.image_target_version,
            "log": log_first_generation,
            "fixed": is_code_fixed(log_first_generation)
        }]
        # BEST CASE: the code works on the target version
        if is_code_fixed(log_first_generation):
            return python_code, metadata
        log_first_generation_old = run_qiskit_code_in_docker(
            code=python_code,
            image_name=self.image_starting_version
        )
        metadata["execution_feedback"].append({
            "id": 2,
            "image": self.image_starting_version,
            "log": log_first_generation_old,
            "fixed": is_code_fixed(log_first_generation_old)
        })
        # MEDIUM CASE: the code works on the starting version, let's migrate it
        if is_code_fixed(log_first_generation_old):
            api_info = metadata["api_info"]
            migrated_python_code, migration_metadata = self._migrate_program(
                python_code, api_info=api_info,
                runtime_error=log_first_generation)
            metadata["migration_metadata"] = migration_metadata
            log_second_generation = run_qiskit_code_in_docker(
                code=migrated_python_code,
                image_name=self.image_target_version
            )
            metadata["execution_feedback"].append({
                "id": 3,
                "image": self.image_target_version,
                "log": log_second_generation,
                "fixed": is_code_fixed(log_second_generation)
            })
            return migrated_python_code, metadata

        # WORST CASE: the code does not work on both versions, we give up
        return python_code, metadata
