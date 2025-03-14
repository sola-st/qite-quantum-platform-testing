"""This is the content of the error message:
{
    "exception_message": "map::at",
    "stack_trace": "Traceback (most recent call last):\n  File \"/workspace/qiskit_circuit_5q_10g_3_8ce198.py\", line 313, in <module>\n    compare_call(a_file, b_file)\n  File \"/workspace/qiskit_circuit_5q_10g_3_8ce198.py\", line 250, in compare_qasm_via_qcec\n    result = qcec.verify(\n  File \"/usr/local/lib/python3.10/site-packages/mqt/qcec/verify.py\", line 59, in verify\n    ecm.run()\nIndexError: map::at\n",
    "current_file": "qiskit_circuit_5q_10g_3_8ce198.py",
    "involved_functions": [
        "compare_qasm_via_qcec",
        "export_to_qasm_with_pytket",
        "export_to_qasm_with_qiskit"
    ]
}
"""
# Section: Prologue
from itertools import combinations
from typing import List, Dict, Any, Callable, Tuple, Optional
from pathlib import Path
import inspect
import sys
import uuid
import json
import traceback
import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Session, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Section: Circuit
from qiskit import qasm2
# Original qasm name: 0e80535550b21de755cfc1f74077debc.qasm
# <START_GATES>

qc = qasm2.loads(
    """
include "qelib1.inc";
qreg q[4];
creg c[4];
swap q[0],q[1];
measure q[1] -> c[0];
swap q[1],q[3];
swap q[0],q[1];
cx q[3],q[1];
measure q[3] -> c[0];
""", custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)

def get_functions(prefix: str) ->List[Callable]:
    """
    Finds all functions in the current module that start with the given prefix
    and returns a list of these functions without executing them.

    Args:
        prefix (str): The prefix to filter functions by.

    Returns:
        List[Callable]: A list of functions that start with the given prefix.
    """
    current_module = sys.modules[__name__]
    functions = inspect.getmembers(current_module, inspect.isfunction)
    filtered_functions = [func for name, func in functions if name.
        startswith(prefix)]
    return filtered_functions


def log_exception_to_json(exception: Exception, stack_trace: str,
    involved_functions: List[str]) ->None:
    """
    Logs the stack trace, current file, exception message, and involved functions to a JSON file.

    Args:
        exception (Exception): The exception to log.
        stack_trace (str): The full stack trace of the exception.
        involved_functions (List[str]): List of function names involved in the current context.
    """
    current_file = Path(__file__)
    uuid_suffix = str(uuid.uuid4())[:6]
    log_file_name = f'{current_file.stem}_{uuid_suffix}_error.json'
    log_file_path = current_file.with_name(log_file_name)
    log_details: Dict[str, Any] = {'exception_message': str(exception),
        'stack_trace': stack_trace, 'current_file': current_file.name,
        'involved_functions': involved_functions}
    with log_file_path.open('w') as json_file:
        json.dump(log_details, json_file, indent=4)
    print(f'Log has been saved to {log_file_path}')


def export_to_qasm_with_pytket(qiskit_circ: QuantumCircuit, var_name: str
    ) ->Optional[str]:
    """Export a Qiskit circuit to a Pytket QASM file."""
    from pytket.extensions.qiskit import qiskit_to_tk
    from pytket.qasm import circuit_to_qasm_str
    tket_circ = qiskit_to_tk(qiskit_circ.decompose().decompose())
    qasm_str_tket = circuit_to_qasm_str(tket_circ, header='qelib1',
        maxwidth=200)
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_pytket = current_file.with_name(
        f'{file_stem}_{var_name}_pytket.qasm')
    with open(file_path_pytket, 'w') as f:
        f.write(qasm_str_tket)
    print(f'Saved the Pytket circuit to {file_path_pytket}')
    return file_path_pytket.as_posix()


def export_to_qasm_with_qiskit(qiskit_circ: QuantumCircuit, var_name: str
    ) ->Optional[str]:
    """Export a Qiskit circuit to a Qiskit QASM file."""
    from qiskit import qasm2
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_qiskit = current_file.with_name(
        f'{file_stem}_{var_name}_qiskit.qasm')
    qasm2.dump(qiskit_circ, file_path_qiskit)
    print(f'Saved the Qiskit circuit to {file_path_qiskit}')
    return file_path_qiskit.as_posix()


def compare_qasm_via_qcec(path_qasm_a: str, path_qasm_b: str) ->None:
    """Compare two QASM files using QCEC."""
    from mqt import qcec
    result = qcec.verify(str(path_qasm_a), str(path_qasm_b),
        transform_dynamic_circuit=True)
    equivalence = str(result.equivalence)
    if (equivalence == 'equivalent' or equivalence ==
        'equivalent_up_to_global_phase'):
        print(f'The circuits are equivalent: {path_qasm_a}, {path_qasm_b}')
        return
    raise ValueError(
        f'The circuits are not equivalent: {path_qasm_a}, {path_qasm_b}')


target_qc = qc
export_calls = get_functions(prefix='export_to_qasm')
qasm_files_with_provenance = []
for export_call in export_calls:
    try:
        qasm_file = export_call(qiskit_circ=target_qc, var_name='qc')
        qasm_files_with_provenance.append((qasm_file, export_call.__name__))
    except Exception as e:
        stack_trace = traceback.format_exc()
        involved_functions = [export_call.__name__]
        log_exception_to_json(e, stack_trace, involved_functions)
if len(qasm_files_with_provenance) > 0:
    print(f'Exported QASM files: {qasm_files_with_provenance}')
else:
    print('No QASM files exported.')
    exit(0)
parser_calls = get_functions(prefix='import_from_qasm')
for parser_call in parser_calls:
    for qasm_file, export_call_name in qasm_files_with_provenance:
        try:
            parser_call(qasm_file)
        except Exception as e:
            stack_trace = traceback.format_exc()
            involved_functions = [parser_call.__name__, export_call_name]
            log_exception_to_json(e, stack_trace, involved_functions)
compare_calls = get_functions(prefix='compare_qasm_')
for pair in combinations(qasm_files_with_provenance, 2):
    a_file, a_exporter = pair[0]
    b_file, b_exporter = pair[1]
    for compare_call in compare_calls:
        try:
            compare_call(a_file, b_file)
        except Exception as e:
            stack_trace = traceback.format_exc()
            involved_functions = [compare_call.__name__, a_exporter, b_exporter
                ]
            log_exception_to_json(e, stack_trace, involved_functions)
