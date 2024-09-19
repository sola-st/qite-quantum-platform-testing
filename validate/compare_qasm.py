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
from typing import List, Tuple
from rich.console import Console
from mqt import qcec

console = Console()


def get_qasm_files(input_folder: Path) -> List[Path]:
    """Returns all QASM files in the input folder, sorted by filename."""
    qasm_files = sorted(input_folder.glob("*.qasm"))
    return qasm_files


def pair_qasm_files(qasm_files: List[Path]) -> List[Tuple[Path, Path]]:
    """Pairs QASM files by matching the common prefix before _pytket and _qiskit."""
    pairs = []
    for qiskit_file in qasm_files:
        if "_qiskit.qasm" in qiskit_file.name:
            prefix = qiskit_file.stem.replace("_qiskit", "")
            pytket_file = qiskit_file.with_name(f"{prefix}_pytket.qasm")
            if pytket_file.exists():
                pairs.append((pytket_file, qiskit_file))
    return pairs


def compare_circuits(pair: Tuple[Path, Path]) -> None:
    """Compares two QASM files using QCEC and logs the result."""
    pytket_file, qiskit_file = pair
    result = qcec.verify(str(pytket_file), str(qiskit_file))
    equivalence = str(result.equivalence)
    if equivalence == 'equivalent':
        console.log(f"[green]The circuits {pytket_file.name} "
                    f"and {qiskit_file.name} are equivalent.")
    else:
        console.log(f"[red]The circuits {pytket_file.name} "
                    f"and {qiskit_file.name} are not equivalent.")


def process_qasm_files(input_folder: Path) -> None:
    """Processes the QASM files in pairs and compares them."""
    qasm_files = get_qasm_files(input_folder=input_folder)
    qasm_pairs = pair_qasm_files(qasm_files=qasm_files)

    for pair in qasm_pairs:
        console.log("Comparing circuits:")
        console.log(f"  {pair[0].name}")
        console.log(f"  {pair[1].name}")
        compare_circuits(pair=pair)


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
