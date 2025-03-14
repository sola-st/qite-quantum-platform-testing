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
OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
cx q[1],q[2];
h q[2];
swap q[0],q[1];
h q[0];
cx q[1],q[3];
h q[3];
measure q[1] -> c[0];
swap q[1],q[3];
cx q[2],q[1];
h q[3];
swap q[0],q[1];
measure q[2] -> c[2];
cx q[3],q[1];
measure q[0] -> c[3];
measure q[3] -> c[0];

""", custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
# <END_GATES>


# Helper Functions


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
    # Filter functions that start with the given prefix
    filtered_functions = [func for name, func in functions
                          if name.startswith(prefix)]
    return filtered_functions


def log_exception_to_json(
    exception: Exception,
    stack_trace: str,
    involved_functions: List[str]
) -> None:
    """
    Logs the stack trace, current file, exception message, and involved functions to a JSON file.

    Args:
        exception (Exception): The exception to log.
        stack_trace (str): The full stack trace of the exception.
        involved_functions (List[str]): List of function names involved in the current context.
    """
    # Get current file and generate a unique log file name
    current_file = Path(__file__)
    uuid_suffix = str(uuid.uuid4())[:6]
    log_file_name = f"{current_file.stem}_{uuid_suffix}_error.json"
    log_file_path = current_file.with_name(log_file_name)

    # Create a log dictionary with all details
    log_details: Dict[str, Any] = {
        "exception_message": str(exception),
        "stack_trace": stack_trace,
        "current_file": current_file.name,
        "involved_functions": involved_functions
    }

    # Write the log details to a JSON file
    with log_file_path.open("w") as json_file:
        json.dump(log_details, json_file, indent=4)

    print(f"Log has been saved to {log_file_path}")


# Section: Oracle Functions
# <START_FUNCTIONS_EXPORT>
def export_to_qasm_with_bqskit(
        qiskit_circ: QuantumCircuit, var_name: str) -> Optional[str]:
    """Export a Qiskit circuit to a BQSKit QASM file."""
    from bqskit.ext import qiskit_to_bqskit
    bqskit_circ = qiskit_to_bqskit(qiskit_circ)

    # Determine file path
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_bqskit = current_file.with_name(
        f"{file_stem}_{var_name}_bqskit.qasm")

    # Save BQSKit circuit to QASM
    bqskit_circ.save(str(file_path_bqskit))

    print(f"Saved the BQSKit circuit to {file_path_bqskit}")
    return file_path_bqskit.as_posix()


def export_to_qasm_with_pennylane(
        qiskit_circ: QuantumCircuit, var_name: str) -> Optional[str]:
    """Export a Qiskit circuit to a PennyLane QASM file."""
    import pennylane as qml
    from pennylane.tape import QuantumTape
    from qiskit import QuantumCircuit

    # Convert Qiskit circuit to a simplified form
    simplified_qiskit_circ = qiskit_circ.decompose().decompose()
    n_qubits = simplified_qiskit_circ.num_qubits

    # add at least one empty operation on each qubit to avoid the order change
    prefix_circ = QuantumCircuit(n_qubits)
    for i in range(n_qubits):
        prefix_circ.id(i)
    simplified_qiskit_circ = prefix_circ.compose(simplified_qiskit_circ)

    # Define measurement and PennyLane device
    measurements = [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    circuit_fn = qml.from_qiskit(
        simplified_qiskit_circ, measurements=measurements)
    dev = qml.device('default.qubit', wires=n_qubits)
    qml_circuit = qml.QNode(circuit_fn, dev)

    # Extract the QASM from the PennyLane QNode
    with QuantumTape(shots=10) as tape:
        qml_circuit.construct([], {})
        qasm_str_pennylane = qml_circuit.tape.to_openqasm(
            wires=sorted(
                tape.wires))

    # Determine file path
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_pennylane = current_file.with_name(
        f"{file_stem}_{var_name}_pennylane.qasm")

    # Save PennyLane QASM string to file
    with open(file_path_pennylane, 'w') as f:
        f.write(qasm_str_pennylane)

    print(f"Saved the PennyLane circuit to {file_path_pennylane}")
    return file_path_pennylane.as_posix()


def export_to_qasm_with_pytket(
        qiskit_circ: QuantumCircuit, var_name: str) -> Optional[str]:
    """Export a Qiskit circuit to a Pytket QASM file."""
    from pytket.extensions.qiskit import qiskit_to_tk
    from pytket.qasm import circuit_to_qasm_str

    # Convert Qiskit circuit to Pytket format and save as QASM
    tket_circ = qiskit_to_tk(qiskit_circ.decompose().decompose())
    qasm_str_tket = circuit_to_qasm_str(
        tket_circ, header="qelib1", maxwidth=200)

    # Determine file path
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_pytket = current_file.with_name(
        f"{file_stem}_{var_name}_pytket.qasm")

    with open(file_path_pytket, 'w') as f:
        f.write(qasm_str_tket)

    print(f"Saved the Pytket circuit to {file_path_pytket}")
    return file_path_pytket.as_posix()


def export_to_qasm_with_qiskit(
        qiskit_circ: QuantumCircuit, var_name: str) -> Optional[str]:
    """Export a Qiskit circuit to a Qiskit QASM file."""
    from qiskit import qasm2

    # Determine file path
    current_file = Path(__file__)
    file_stem = current_file.stem
    file_path_qiskit = current_file.with_name(
        f"{file_stem}_{var_name}_qiskit.qasm")

    # Save Qiskit circuit directly to QASM
    qasm2.dump(qiskit_circ, file_path_qiskit)

    print(f"Saved the Qiskit circuit to {file_path_qiskit}")
    return file_path_qiskit.as_posix()

# <END_FUNCTIONS_EXPORT>
# <START_FUNCTIONS_IMPORT>


def import_from_qasm_with_bqskit(file_path: str):
    """Import a QASM file using bqskit."""
    from bqskit import Circuit
    bqskit_circuit = Circuit.from_file(file_path)
    print(f"Circuit (bqskit) imported correctly: {file_path}")
    return bqskit_circuit


def import_from_qasm_with_pennylane(file_path: str):
    """Import a QASM file using PennyLane."""
    import pennylane as qml
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = qml.from_qasm(qasm_content)
    print(f"Circuit (PennyLane) imported correctly: {file_path}")
    return circuit


def import_from_qasm_with_pytket(file_path: str):
    """Import a QASM file using Pytket."""
    from pytket.qasm import circuit_from_qasm_str
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = circuit_from_qasm_str(qasm_content, maxwidth=200)
    print(f"Circuit (Pytket) imported correctly: {file_path}")
    return circuit


def import_from_qasm_with_qiskit(file_path: str):
    """Import a QASM file using Qiskit."""
    from qiskit import qasm2
    with open(file_path, 'r') as f:
        qasm_content = f.read()
    circuit = qasm2.loads(
        qasm_content, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
    print(f"Circuit (Qiskit) imported correctly: {file_path}")
    return circuit

# <END_FUNCTIONS_IMPORT>
# <START_FUNCTIONS_COMPARE>


def compare_qasm_via_qcec(path_qasm_a: str, path_qasm_b: str) -> None:
    """Compare two QASM files using QCEC."""
    from mqt import qcec
    result = qcec.verify(
        str(path_qasm_a),
        str(path_qasm_b),
        transform_dynamic_circuit=True)
    equivalence = str(result.equivalence)
    if (
            equivalence == 'equivalent' or
            equivalence == 'equivalent_up_to_global_phase'
    ):
        print(f"The circuits are equivalent: {path_qasm_a}, {path_qasm_b}")
        return
    raise ValueError(
        f"The circuits are not equivalent: {path_qasm_a}, {path_qasm_b}")

# <END_FUNCTIONS_COMPARE>


# Section: Test Oracle Calls
target_qc = qc

# Section: Stage - QASM Exporter
export_calls = get_functions(prefix="export_to_qasm")
qasm_files_with_provenance = []
for export_call in export_calls:
    try:
        qasm_file = export_call(
            qiskit_circ=target_qc,
            var_name="qc",
        )
        qasm_files_with_provenance.append((qasm_file, export_call.__name__))
    except Exception as e:
        stack_trace = traceback.format_exc()
        involved_functions = [export_call.__name__]
        log_exception_to_json(e, stack_trace, involved_functions)

if len(qasm_files_with_provenance) > 0:
    print(f"Exported QASM files: {qasm_files_with_provenance}")
else:
    print("No QASM files exported.")
    exit(0)

# Section: Stage - Execution
# TODO

# Section: Stage - QASM Parser
parser_calls = get_functions(prefix="import_from_qasm")
for parser_call in parser_calls:
    for qasm_file, export_call_name in qasm_files_with_provenance:
        try:
            parser_call(qasm_file)
        except Exception as e:
            stack_trace = traceback.format_exc()
            involved_functions = [parser_call.__name__, export_call_name]
            log_exception_to_json(e, stack_trace, involved_functions)

# Section: Stage - Comparison

compare_calls = get_functions(prefix="compare_qasm_")
for pair in combinations(qasm_files_with_provenance, 2):
    a_file, a_exporter = pair[0]
    b_file, b_exporter = pair[1]
    for compare_call in compare_calls:
        try:
            compare_call(a_file, b_file)
        except Exception as e:
            stack_trace = traceback.format_exc()
            involved_functions = [
                compare_call.__name__, a_exporter, b_exporter]
            log_exception_to_json(e, stack_trace, involved_functions)
