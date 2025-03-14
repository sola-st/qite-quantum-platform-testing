from qiskit.qasm2 import load, LEGACY_CUSTOM_INSTRUCTIONS
from qiskit.quantum_info import Operator
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import click
from rich.console import Console
from tqdm import tqdm

from qite.qite_replay import run_qite_chain
from qite.inspection.ddmin import DDMin
from mqt import qcec

import tempfile
import logging
import shutil

from qite.generate_equivalences_graph import generate_equivalence_graph


console = Console()


def load_json(file_path: Path) -> Dict[str, Any]:
    with file_path.open('r') as file:
        return json.load(file)


def find_common_ancestor(tree1: List[Dict[str, Any]],
                         tree2: List[Dict[str, Any]]) -> Dict[str, Any]:
    # case in which one of the two program was
    # generated and has no provenance tree
    if len(tree1) == 0:
        return tree2[0]
    if len(tree2) == 0:
        return tree1[0]
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


def compare_unitary_equivalence(qasm1_path: str, qasm2_path: str) -> None:
    """Compare the unitary equivalence of two QASM files."""
    try:
        qc1 = load(qasm1_path, custom_instructions=LEGACY_CUSTOM_INSTRUCTIONS)
        qc2 = load(qasm2_path, custom_instructions=LEGACY_CUSTOM_INSTRUCTIONS)

        op1 = Operator(qc1)
        op2 = Operator(qc2)

        # console.print("QASM 1 Unitary Matrix:")
        # console.print(op1.data)

        # console.print("QASM 2 Unitary Matrix:")
        # console.print(op2.data)

        unitary_equiv = op1.equiv(op2)
        print(f"Unitary Equivalence: {unitary_equiv}")
    except Exception as e:
        print(f"Error: {e}")
        return False
    return unitary_equiv


def delta_debugging_in_sandbox(
    qasm_content: str,
    original_qasm_filename: str,
    original_qcec_result: str,
    tree1: List[Dict[str, Any]],
    tree2: List[Dict[str, Any]],
) -> Tuple[str, Path]:
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
            # case that one tree is empty, means that this file was generated
            # and has no provenance tree. This can happen only for one of the
            # two trees, not both because we have only one root qasm per
            # equivalence class
            if len(tree1) == 0:
                last_qasm_1 = Path(tree2[0]["input_qasm"]).name
            else:
                last_qasm_1 = Path(tree1[-1]["output_qasm"]).name
            if len(tree2) == 0:
                last_qasm_2 = Path(tree1[0]["input_qasm"]).name
            else:
                last_qasm_2 = Path(tree2[-1]["output_qasm"]).name
            path_qasm_1 = tmpdir / last_qasm_1
            path_qasm_2 = tmpdir / last_qasm_2
            try:
                # print the qasm files content
                # with path_qasm_1.open('r') as file:
                #     console.print(file.read(), style="red")
                # with path_qasm_2.open('r') as file:
                #     console.print(file.read(), style="blue")
                result = qcec.verify(
                    str(path_qasm_1),
                    str(path_qasm_2),
                    transform_dynamic_circuit=True)
                equivalence = str(result.equivalence)
                # if compare_unitary_equivalence(
                #         str(path_qasm_1), str(path_qasm_2)):
                #     equivalence = "equivalent"
                # else:
                #     equivalence = "not_equivalent"
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

    return '\n'.join(minimized_qasm_lines), tmpdir


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

    minimize_file_content, tmpdir = delta_debugging_in_sandbox(
        qasm_content=comm_anc_content,
        original_qasm_filename=comm_anc_filename,
        original_qcec_result=data['equivalence'],
        tree1=nodes_from_ancestor1,
        tree2=nodes_from_ancestor2)

    output_folder.mkdir(parents=True, exist_ok=True)
    minimized_qasm_path = output_folder / comm_anc_filename
    with minimized_qasm_path.open('w') as file:
        file.write(minimize_file_content)

    # copy entire content of tmpdir to output_folder shutil
    extra_info_folder = \
        output_folder / f"{Path(common_ancestor['input_qasm']).stem}_debug"
    shutil.copytree(tmpdir, extra_info_folder, dirs_exist_ok=True)

    generate_equivalence_graph(
        input_folder=extra_info_folder, prefix=None)


if __name__ == '__main__':
    main()
