import os
import json
from pathlib import Path
from typing import List, Dict, Any
import click
from rich.console import Console
from tqdm import tqdm

from qite.qite_replay import run_qite_chain
from analysis_and_reporting.ddmin import DDMin
from mqt import qcec

import tempfile
import logging


"""
Task Description: Delta Debugging CLI Tool

**Objective:**
Develop a command-line interface (CLI) tool that minimizes the input program to trigger the same inequivalence by identifying the common ancestor in the transformation tree and providing detailed metadata for the derivation paths.

**Input:**
- A JSON file specified by the `--comparison_metadata` option. This JSON file contains information about the comparison of two nodes in a transformation tree.
- An output folder specified by the `--output_folder` option where the common ancestor file will be stored.

**Output:**
- Print the content of the "input_qasm" file of the common ancestor to the console.
- Print the pretty-printed "platform" fields for the derivation paths from the common ancestor to the two compared nodes.
- Save the content of the common ancestor's "input_qasm" file to the specified output folder.

**Requirements:**
1. **Command-Line Arguments:**
   - `--comparison_metadata <path>`: Path to the input JSON file containing comparison metadata.
   - `--output_folder <path>`: Path to the folder where the common ancestor file will be stored.

2. **Transformation Tree:**
   - The JSON file contains a "qasms" field with two elements, each having a "provenance_tree" field.
   - Each "provenance_tree" is a list of dictionaries (INFO) with "input_qasm" and "output_qasm" fields.

3. **Processing Logic:**
   - Identify the common ancestor of the two provenance trees using an efficient algorithm.
   - Extract the content of the "input_qasm" file of the common ancestor.
   - Collect and pretty-print the "platform" field for each INFO dictionary from the common ancestor to the two compared nodes.

4. **Output:**
   - Print the content of the "input_qasm" file of the common ancestor to the console.
   - Print the pretty-printed "platform" fields for the derivation paths.
   - Save the content of the common ancestor's "input_qasm" file to the specified output folder.

5. **Error Handling:**
   - Assume the metadata has all the fields needed, no error handling required.

6. **Testing and Validation:**
   - Validate the tool with various input JSON files to ensure correctness.
   - Provide test cases and scenarios for validation.

**Example JSON Structure:**
```json
{
    "qasms": [
        {
            "filename": "0000009_qite_88e429.qasm",
            "provenance": "pennylane",
            "provenance_tree": [
                {
                    "input_qasm": "program_bank/v024/2025_02_06__17_14/0000009_qite_b6cb8e.qasm",
                    "platform": "pennylane",
                    "importer_function": "pennylane_import",
                    "transformer_functions": [
                        "pennylane_optimizer_commute_controlled",
                        "pennylane_optimizer_single_qubit_fusion",
                        "pennylane_optimizer_combine_global_phases"
                    ],
                    "exporter_function": "pennylane_export",
                    "output_qasm": "program_bank/v024/2025_02_06__17_14/0000009_qite_88e429.qasm"
                },
                {
                    "input_qasm": "program_bank/v024/2025_02_06__17_14/0000009_qite_ad3590.qasm",
                    "platform": "pytket",
                    "importer_function": "pytket_import",
                    "transformer_functions": [
                        "pytket_optimizer_pauli_simp",
                        "pytket_optimizer_optimise_phase_gadgets",
                        "pytket_optimizer_flatten_registers"
                    ],
                    "exporter_function": "pytket_export",
                    "output_qasm": "program_bank/v024/2025_02_06__17_14/0000009_qite_b6cb8e.qasm"
                },
                {
                    "input_qasm": "program_bank/v024/2025_02_06__17_14/0000009_c6d763.qasm",
                    "platform": "qiskit",
                    "importer_function": "qiskit_import",
                    "transformer_functions": [
                        "qiskit_optimizer_level_3",
                        "qiskit_change_gateset_u3_cx",
                        "qiskit_change_gateset_rx_ry_rz_cz"
                    ],
                    "exporter_function": "qiskit_export",
                    "output_qasm": "program_bank/v024/2025_02_06__17_14/0000009_qite_ad3590.qasm"
                }
            ]
        },
        {
            "filename": "0000009_qite_b6cb8e.qasm",
            "provenance": "pytket",
            "provenance_tree": [
                {
                    "input_qasm": "program_bank/v024/2025_02_06__17_14/0000009_qite_ad3590.qasm",
                    "platform": "pytket",
                    "importer_function": "pytket_import",
                    "transformer_functions": [
                        "pytket_optimizer_pauli_simp",
                        "pytket_optimizer_optimise_phase_gadgets",
                        "pytket_optimizer_flatten_registers"
                    ],
                    "exporter_function": "pytket_export",
                    "output_qasm": "program_bank/v024/2025_02_06__17_14/0000009_qite_b6cb8e.qasm"
                },
                {
                    "input_qasm": "program_bank/v024/2025_02_06__17_14/0000009_c6d763.qasm",
                    "platform": "qiskit",
                    "importer_function": "qiskit_import",
                    "transformer_functions": [
                        "qiskit_optimizer_level_3",
                        "qiskit_change_gateset_u3_cx",
                        "qiskit_change_gateset_rx_ry_rz_cz"
                    ],
                    "exporter_function": "qiskit_export",
                    "output_qasm": "program_bank/v024/2025_02_06__17_14/0000009_qite_ad3590.qasm"
                }
            ]
        }
    ],
    "equivalence": "not_equivalent"
}
```

# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- avoid function with a single line which is a function call
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib every time that paths are checked, created or composed.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate
- make sure that any output folder exists before storing file in it, otherwise create it.

Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports
Make sure to add a function and call that function only in the main cli command.
The goal is to be able to import that function also from other files.



"""
console = Console()


def load_json(file_path: Path) -> Dict[str, Any]:
    with file_path.open('r') as file:
        return json.load(file)


def find_common_ancestor(tree1: List[Dict[str, Any]],
                         tree2: List[Dict[str, Any]]) -> Dict[str, Any]:
    set1 = {node['output_qasm'] for node in tree1}
    for node in tree2:
        if node['output_qasm'] in set1:
            return node
    return {}


def pretty_print_platforms(
        tree: List[Dict[str, Any]],
        ancestor: Dict[str, Any]) -> None:
    start_printing = False
    for node in tree:
        if node['input_qasm'] == ancestor['input_qasm']:
            start_printing = True
        if start_printing:
            console.print(f"- [bold]{node['platform']}[/bold]")


def get_nodes_from_ancestor(
        tree: List[Dict[str, Any]],
        ancestor: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes = []
    start_collecting = False
    for node in tree:
        if node['input_qasm'] == ancestor['input_qasm']:
            start_collecting = True
        if start_collecting:
            nodes.append(node)
    return nodes


def save_common_ancestor(input_qasm: str, output_folder: Path) -> None:
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / Path(input_qasm).name
    with open(input_qasm, 'r') as src_file, output_path.open('w') as dst_file:
        dst_file.write(src_file.read())


def write_tree_to_disk(
        tree: List[Dict[str, Any]],
        output_folder: Path, tree_name: str) -> List[str]:
    filenames = []
    for idx, node in enumerate(tree):
        output_path = output_folder / f"{tree_name}_node{idx + 1}.json"
        with output_path.open('w') as file:
            json.dump(node, file, indent=4)
        filenames.append(str(output_path))
    return filenames


def delta_debugging_in_sandbox(
    qasm_content: str,
    original_qasm_filename: str,
    original_qcec_result: str,
    tree1: List[Dict[str, Any]],
    tree2: List[Dict[str, Any]],
) -> str:
    """Run delta debugging process on the input QASM content.

    It returns the minimized QASM content that triggers the same inequivalence.
    """
    tmpdir = Path(tempfile.mkdtemp())
    console.print(f"Temporary directory created at: {tmpdir}")

    qasm_path = tmpdir / original_qasm_filename
    with qasm_path.open('w') as file:
        file.write(qasm_content)

    filenames_tree1 = write_tree_to_disk(
        tree=tree1, output_folder=tmpdir, tree_name="tree1")
    filenames_tree2 = write_tree_to_disk(
        tree=tree2, output_folder=tmpdir, tree_name="tree2")
    for path in os.listdir(tmpdir):
        print(path)

        logger = logging.getLogger(__name__)

        def repro_func(qasm_lines: List[str]) -> bool:
            """Return False if the same error is reproduced."""
            qasm_path = tmpdir / original_qasm_filename
            with qasm_path.open('w') as file:
                file.write('\n'.join(qasm_lines))

            for i, filenames_tree in enumerate(
                    [filenames_tree1, filenames_tree2]):
                logger.info(f"Running QITE chain on tree: {i + 1}")
                try:
                    run_qite_chain(
                        metadata_paths=filenames_tree,
                        input_folder=str(tmpdir),
                        output_debug_folder=str(tmpdir),
                        print_intermediate_qasm=False)
                except Exception as e:
                    return True
            last_qasm_1 = Path(tree1[-1]["output_qasm"]).name
            last_qasm_2 = Path(tree2[-1]["output_qasm"]).name
            path_qasm_1 = tmpdir / last_qasm_1
            path_qasm_2 = tmpdir / last_qasm_2
            try:
                result = qcec.verify(
                    str(path_qasm_1),
                    str(path_qasm_2),
                    transform_dynamic_circuit=True)
                equivalence = str(result.equivalence)
            except Exception as e:
                equivalence = f"error: {e}"
            logger.info("Equivalence Check")
            logger.info(f"Equivalence: {equivalence}")
            logger.info(f"Original QCEC Result: {original_qcec_result}")
            if equivalence == original_qcec_result:
                return False
            return True

    original_qasm_lines = qasm_content.split('\n')

    # get stats on reproducibility
    n_repro_runs = 10
    n_succ_repros = sum(tqdm([int(repro_func(original_qasm_lines) == False)
                              for _ in range(n_repro_runs)]))
    repro_stats = n_succ_repros / n_repro_runs
    console.print(
        f"Reproducibility Stats: {repro_stats:.2f} ({n_succ_repros}/{n_repro_runs})")

    assert repro_stats == 1.0, (
        "Reproducibility check failed (the same error in the original program "
        "must be reproduced consistently in the original program before "
        "running the delta debugging process. Unfortunately, the error is not "
        "reproduced consistently, the same error is reproduced only "
        f"{repro_stats:.2f}% of the time ({n_succ_repros}/{n_repro_runs} runs)."
    )
    console.rule("Running Delta Debugging Process")
    debugger = DDMin(original_qasm_lines, repro_func)
    minimized_qasm_lines = debugger.execute()

    # reproduce with the minimized lines
    # so that the intermediate files of this file are in the tmpdir
    repro_func(minimized_qasm_lines)

    return '\n'.join(minimized_qasm_lines)


@click.command()
@click.option('--comparison_metadata', type=click.Path(exists=True, path_type=Path), required=True)
@click.option('--output_folder', type=click.Path(path_type=Path),
              required=True)
@click.option('--input_folder', type=click.Path(exists=True, path_type=Path), required=True)
def main(comparison_metadata: Path, output_folder: Path, input_folder: Path) -> None:
    data = load_json(file_path=comparison_metadata)
    qasms = data['qasms']
    tree1 = qasms[0]['provenance_tree'][::-1]
    tree2 = qasms[1]['provenance_tree'][::-1]

    common_ancestor = find_common_ancestor(tree1=tree1, tree2=tree2)
    assert common_ancestor, "No common ancestor found"

    comm_anc_filename = Path(common_ancestor['input_qasm']).name
    input_qasm_path = input_folder / comm_anc_filename
    with input_qasm_path.open('r') as file:
        comm_anc_content = file.read()
    console.print(comm_anc_content)

    for i, tree in enumerate([tree1, tree2], start=1):
        console.rule(f"Platform Provenance Tree {i}")
        pretty_print_platforms(tree=tree, ancestor=common_ancestor)

    nodes_from_ancestor1 = get_nodes_from_ancestor(
        tree=tree1, ancestor=common_ancestor)
    nodes_from_ancestor2 = get_nodes_from_ancestor(
        tree=tree2, ancestor=common_ancestor)

    minimize_file_content = delta_debugging_in_sandbox(
        qasm_content=comm_anc_content,
        original_qasm_filename=comm_anc_filename,
        original_qcec_result=data['equivalence'],
        tree1=nodes_from_ancestor1,
        tree2=nodes_from_ancestor2)

    minimized_qasm_path = output_folder / comm_anc_filename
    with minimized_qasm_path.open('w') as file:
        file.write(minimize_file_content)


if __name__ == '__main__':
    main()
