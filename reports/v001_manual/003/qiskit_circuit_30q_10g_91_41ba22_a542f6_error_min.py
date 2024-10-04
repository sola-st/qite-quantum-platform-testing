"""This is the content of the error message:
{
    "exception_message": "Gate has an invalid number of parameters",
    "stack_trace": "Traceback (most recent call last):\n  File \"/workspace/qiskit_circuit_30q_10g_91_41ba22.py\", line 248, in <module>\n    parser_call(qasm_file)\n  File \"/workspace/qiskit_circuit_30q_10g_91_41ba22.py\", line 188, in import_from_qasm_with_pytket\n    circuit = circuit_from_qasm_str(qasm_content)\n  File \"/usr/local/lib/python3.10/site-packages/pytket/qasm/qasm.py\", line 987, in circuit_from_qasm_str\n    return Circuit.from_dict(g_parser.parse(qasm_str))  # type: ignore[arg-type]\n  File \"/usr/local/lib/python3.10/site-packages/lark/lark.py\", line 655, in parse\n    return self.parser.parse(text, start=start, on_error=on_error)\n  File \"/usr/local/lib/python3.10/site-packages/lark/parser_frontends.py\", line 104, in parse\n    return self.parser.parse(stream, chosen_start, **kw)\n  File \"/usr/local/lib/python3.10/site-packages/lark/parsers/lalr_parser.py\", line 42, in parse\n    return self.parser.parse(lexer, start)\n  File \"/usr/local/lib/python3.10/site-packages/lark/parsers/lalr_parser.py\", line 88, in parse\n    return self.parse_from_state(parser_state)\n  File \"/usr/local/lib/python3.10/site-packages/lark/parsers/lalr_parser.py\", line 102, in parse_from_state\n    state.feed_token(token)\n  File \"/usr/local/lib/python3.10/site-packages/lark/parsers/lalr_parser_state.py\", line 101, in feed_token\n    value = callbacks[rule](s) if callbacks else s\n  File \"/usr/local/lib/python3.10/site-packages/lark/parse_tree_builder.py\", line 155, in __call__\n    return self.node_builder(filtered)\n  File \"/usr/local/lib/python3.10/site-packages/pytket/qasm/qasm.py\", line 876, in gdef\n    comparison_circ = _get_gate_circuit(\n  File \"/usr/local/lib/python3.10/site-packages/pytket/qasm/qasm.py\", line 1208, in _get_gate_circuit\n    gate_circ.add_gate(optype, unitids)\nRuntimeError: Gate has an invalid number of parameters\n",
    "current_file": "qiskit_circuit_30q_10g_91_41ba22.py",
    "involved_functions": [
        "import_from_qasm_with_pytket",
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
qr = QuantumRegister(30, name='qr')
cr = ClassicalRegister(30, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')

# Apply gate operations
# <START_GATES>

qc.iswap(qr[12], qr[6])

qc.measure(qr, cr)


def get_functions(prefix: str) -> List[Callable]:
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
                          involved_functions: List[str]) -> None:
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


def export_to_qasm_with_qiskit(qiskit_circ: QuantumCircuit, var_name: str
                               ) -> Optional[str]:
    """Export a Qiskit circuit to a Qiskit QASM file."""
    from qiskit import qasm2
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_qiskit = current_file.with_name(
        f'{file_stem}_{var_name}_qiskit.qasm')
    qasm2.dump(qiskit_circ, file_path_qiskit)
    print(f'Saved the Qiskit circuit to {file_path_qiskit}')
    return file_path_qiskit.as_posix()


def import_from_qasm_with_pytket(file_path: str):
    """Import a QASM file using Pytket."""
    from pytket.qasm import circuit_from_qasm_str
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = circuit_from_qasm_str(qasm_content)
    print(f'Circuit (Pytket) imported correctly: {file_path}')
    return circuit


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
