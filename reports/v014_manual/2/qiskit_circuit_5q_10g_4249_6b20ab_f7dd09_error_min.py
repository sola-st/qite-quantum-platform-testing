"""This is the content of the error message:
{
    "exception_message": "Unrecognized gate: delay.",
    "stack_trace": "Traceback (most recent call last):\n  File \"/workspace/qiskit_circuit_5q_10g_4249_6b20ab.py\", line 297, in <module>\n    parser_call(qasm_file)\n  File \"/workspace/qiskit_circuit_5q_10g_4249_6b20ab.py\", line 201, in import_from_qasm_with_bqskit\n    bqskit_circuit = Circuit.from_file(file_path)\n  File \"/usr/local/lib/python3.10/site-packages/bqskit/ir/circuit.py\", line 3258, in from_file\n    return language.decode(f.read())\n  File \"/usr/local/lib/python3.10/site-packages/bqskit/ir/lang/qasm2/qasm2.py\", line 37, in decode\n    visitor.visit_topdown(tree)\n  File \"/usr/local/lib/python3.10/site-packages/lark/visitors.py\", line 371, in visit_topdown\n    self._call_userfunc(subtree)\n  File \"/usr/local/lib/python3.10/site-packages/lark/visitors.py\", line 343, in _call_userfunc\n    return getattr(self, tree.data, self.__default__)(tree)\n  File \"/usr/local/lib/python3.10/site-packages/bqskit/ir/lang/qasm2/visitor.py\", line 303, in gate\n    raise LangException('Unrecognized gate: %s.' % gate_name)\nbqskit.ir.lang.language.LangException: Unrecognized gate: delay.\n",
    "current_file": "qiskit_circuit_5q_10g_4249_6b20ab.py",
    "involved_functions": [
        "import_from_qasm_with_bqskit",
        "export_to_qasm_with_qiskit"
    ],
    "timestamp": 1735445388.4310288
}
"""
# Section: Prologue
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Session, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Section: Circuit
# <START_GATES>

circ = QuantumCircuit(6, 6)
circ.delay(1, 4, 's')

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


def import_from_qasm_with_bqskit(file_path: str):
    """Import a QASM file using bqskit."""
    from bqskit import Circuit
    bqskit_circuit = Circuit.from_file(file_path)
    print(f'Circuit (bqskit) imported correctly: {file_path}')
    return bqskit_circuit


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
