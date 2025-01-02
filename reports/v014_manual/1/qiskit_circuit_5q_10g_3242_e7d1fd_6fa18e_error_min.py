"""This is the content of the error message:
{
    "exception_message": "Invalid register name '4'. QASM register names must begin with a lowercase letter and may only contain lowercase and uppercase letters, numbers, and underscores. Try renaming the register with `rename_units` first.",
    "stack_trace": "Traceback (most recent call last):\n  File \"/workspace/qiskit_circuit_5q_10g_3242_e7d1fd.py\", line 277, in <module>\n    qasm_file = export_call(\n  File \"/workspace/qiskit_circuit_5q_10g_3242_e7d1fd.py\", line 168, in export_to_qasm_with_pytket\n    qasm_str_tket = circuit_to_qasm_str(\n  File \"/usr/local/lib/python3.10/site-packages/pytket/qasm/qasm.py\", line 1115, in circuit_to_qasm_str\n    qasm_writer = QasmWriter(\n  File \"/usr/local/lib/python3.10/site-packages/pytket/qasm/qasm.py\", line 1380, in __init__\n    raise QASMUnsupportedError(\npytket.qasm.qasm.QASMUnsupportedError: Invalid register name '4'. QASM register names must begin with a lowercase letter and may only contain lowercase and uppercase letters, numbers, and underscores. Try renaming the register with `rename_units` first.\n",
    "current_file": "qiskit_circuit_5q_10g_3242_e7d1fd.py",
    "involved_functions": [
        "export_to_qasm_with_pytket"
    ],
    "timestamp": 1735409740.94003
}
"""
# Section: Prologue
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Session, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Section: Circuit
# <START_GATES>

qr = QuantumRegister(3, '4')
cr = ClassicalRegister(3, 'c4')
circuit = QuantumCircuit(qr, cr)

import os
import traceback
import json
import uuid
import sys
import time
import inspect
from pathlib import Path
from typing import List, Dict, Any, Callable, Tuple, Optional


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
        'involved_functions': involved_functions, 'timestamp': time.time()}
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


from copy import deepcopy
all_circuits_vars = {var_name: deepcopy(var_value) for var_name, var_value in
    globals().items() if isinstance(var_value, QuantumCircuit)}
for key, value in all_circuits_vars.items():
    target_qc = deepcopy(value)
    var_name = key
    export_calls = get_functions(prefix='export_to_qasm')
    qasm_files_with_provenance = []
    for export_call in export_calls:
        try:
            qasm_file = export_call(qiskit_circ=target_qc, var_name=var_name)
            qasm_files_with_provenance.append((qasm_file, export_call.__name__)
                )
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
    from itertools import combinations
    compare_calls = get_functions(prefix='compare_qasm_')
    for pair in combinations(qasm_files_with_provenance, 2):
        a_file, a_exporter = pair[0]
        b_file, b_exporter = pair[1]
        for compare_call in compare_calls:
            try:
                compare_call(a_file, b_file)
            except Exception as e:
                stack_trace = traceback.format_exc()
                involved_functions = [compare_call.__name__, a_exporter,
                    b_exporter]
                log_exception_to_json(e, stack_trace, involved_functions)
