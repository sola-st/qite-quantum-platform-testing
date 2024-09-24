"""Compare all the qasm files in the folder with QCEC.

The script scans the folder content, keeps only the qasm files, sorts them, and
then compares the circuits in pairs. it first creates all the pairs of circuits
each pair contain the two files ending with _pytket.qasm and _qiskit.qasm and
the same prefix before.
Each pair is the compared with QCEC and the result is printed.

An example of how to use the QCEC library to compare two qasm files.
```python
import os
from mqt import qcec

# get path of the current file
current_folder = os.path.dirname(os.path.abspath(__file__))

# path to the qasm files
qasm_file_pytket = os.path.join(current_folder, "0_pytket.qasm")
qasm_file_qiskit = os.path.join(current_folder, "0_qiskit.qasm")

# verify the equivalence of two circuits provided as qasm files
result = qcec.verify(qasm_file_pytket, qasm_file_qiskit)

# print the result
assert str(result.equivalence) == 'equivalent', "The circuits are not equivalent"
```

Arguments:
--input_folder: str: The folder containing the qasm files to compare.


Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports


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


"""

import click
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from rich.console import Console
from mqt import qcec
from itertools import combinations
import traceback
import json
import re

console = Console()


def get_qasm_files(input_folder: Path) -> List[Path]:
    """Returns all QASM files in the input folder, sorted by filename."""
    qasm_files = sorted(input_folder.glob("*.qasm"))
    return qasm_files


def group_qasm_files(qasm_files: List[Path]) -> Dict[str, List[Path]]:
    """Group QASM files by prefixes.

    A file might end with _qiskit.qasm or _pytket.qasm or _pennylane.qasm.
    There might be one or more files with the same prefix.
    The routine
    """
    prefixes = set()
    for qasm_file in qasm_files:
        for suffix in ["_qiskit.qasm", "_pytket.qasm", "_pennylane.qasm"]:
            if suffix in qasm_file.name:
                prefix = qasm_file.name.replace(suffix, "")
                prefixes.add(prefix)
    groups = {}
    for prefix in prefixes:
        group = [
            qasm_file for qasm_file in qasm_files
            if qasm_file.stem.startswith(prefix)]
        groups[prefix] = group
    return groups


def get_common_prefix_and_circ_name(file_a: Path, file_b: Path) -> Tuple[str, str]:
    """Returns the common prefix of two QASM files.

    Scan the filenames from the start until the first difference is found.
    """
    prefix = ""
    for a, b in zip(file_a.stem, file_b.stem):
        if a == b:
            prefix += a
        else:
            break
    if prefix.endswith("isa_qc"):
        file_name = prefix.replace("isa_qc", "")
        var_qc = "isa_qc"
    else:
        file_name = prefix.replace("_qc", "")
        var_qc = "qc"
    return file_name, var_qc


def compare_circuits(pair: Tuple[Path, Path]) -> Optional[Dict[str, str]]:
    """Compares two QASM files using QCEC and logs the result."""
    a_file, b_file = pair
    error_msg = None
    stack_trace = None
    try:
        result = qcec.verify(str(a_file), str(b_file))
        equivalence = str(result.equivalence)
        if equivalence == 'equivalent':
            console.log(f"[green]The circuits are equivalent:\n- {a_file.name}"
                        f"\n- {b_file.name}")
            return None
        else:
            console.log(
                f"[red]The circuits are not equivalent:\n- {a_file.name}"
                f"\n- {b_file.name}")
            error_msg = f"The circuits are not equivalent"
    except Exception as e:
        console.log(f"[red]Error comparing the circuits: {e}[/red]")
        error_msg = f"Error comparing the circuits: {e}"
        stack_trace = traceback.format_exc()
    platform_a = a_file.name.split("_")[-1].replace(".qasm", "")
    platform_b = b_file.name.split("_")[-1].replace(".qasm", "")
    file_name, var_qc = get_common_prefix_and_circ_name(
        file_a=a_file, file_b=b_file)
    return {
        "error": error_msg,
        "file_a": a_file.name,
        "file_b": b_file.name,
        "file_name": file_name,
        "var_qc": var_qc,
        "file_a_content": a_file.read_text(),
        "file_b_content": b_file.read_text(),
        "stack_trace": stack_trace,
        "testing_phase": "qasm_comparison",
        "platform_a": platform_a,
        "platform_b": platform_b,
    }


def process_qasm_files(input_folder: Path) -> None:
    """Processes the QASM files in pairs and compares them."""
    qasm_files = get_qasm_files(input_folder=input_folder)
    qasm_group = group_qasm_files(qasm_files=qasm_files)

    for group_key, group in qasm_group.items():
        console.log("Circuits in group:")
        errors = []
        for el in group:
            console.log(f"  {el.name}")
        for pair in combinations(group, 2):
            console.log(f"Comparing...")
            console.log(f"A.  {pair[0].name}")
            console.log(f"B.  {pair[1].name}")

            error = compare_circuits(pair=pair)
            if error:
                errors.append(error)
            file_path_output = input_folder / \
                f"{group_key}_comparison_errors.json"
            with open(file_path_output, "w") as f:
                json.dump(errors, f, indent=4)


@click.command()
@click.option('--input_folder', required=True, type=click.Path(
    exists=True, file_okay=False),
    help="Folder containing the QASM files to compare.")
def main(input_folder: str) -> None:
    """Main function to scan, pair, and compare QASM files in the given folder."""
    input_folder_path = Path(input_folder)
    process_qasm_files(input_folder=input_folder_path)


if __name__ == '__main__':
    main()
