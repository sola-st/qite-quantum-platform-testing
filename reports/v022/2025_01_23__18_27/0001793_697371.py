# Section: Prologue
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Session, Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# Section: Circuit
qr = QuantumRegister(11, name='qr')
cr = ClassicalRegister(11, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
# TIMESTAMP: 1737648255.013264

# Apply gate operations
# <START_GATES>
qc.p(1.095686, qr[8])
qc.rxx(2.607111, qr[5], qr[1])
qc.mcrz(4.172311, [qr[6], qr[7], qr[5]], qr[10])
qc.t(qr[5])
qc.iswap(qr[10], qr[5])
# <END_GATES>

# Section: Measurement
qc.measure(qr, cr)




# Helper Functions
import os
import traceback
import json
import uuid
import sys
import time
import inspect
from pathlib import Path
from typing import List, Dict, Any, Callable, Tuple, Optional



# Section: Oracle Functions
# <START_FUNCTIONS_EXPORT>
def export_to_qasm_with_bqskit(
        qiskit_circ: QuantumCircuit, var_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a Qiskit circuit to a BQSKit QASM file."""
    from bqskit.ext import qiskit_to_bqskit
    bqskit_circ = qiskit_to_bqskit(qiskit_circ)

    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_bqskit = current_file.with_name(
            f"{file_stem}_{var_name}_bqskit.qasm")
    else:
        file_path_bqskit = Path(abs_output_file)

    # Save BQSKit circuit to QASM
    bqskit_circ.save(str(file_path_bqskit))

    print(f"Saved the BQSKit circuit to {file_path_bqskit}")
    return file_path_bqskit.as_posix()

def export_to_qasm_with_pennylane(
        qiskit_circ: QuantumCircuit, var_name: str,
        abs_output_file: str = None) -> Optional[str]:
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
    if not abs_output_file:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_pennylane = current_file.with_name(
            f"{file_stem}_{var_name}_pennylane.qasm")
    else:
        file_path_pennylane = Path(abs_output_file)

    # Save PennyLane QASM string to file
    with open(file_path_pennylane, 'w') as f:
        f.write(qasm_str_pennylane)

    print(f"Saved the PennyLane circuit to {file_path_pennylane}")
    return file_path_pennylane.as_posix()

def export_to_qasm_with_pytket(
        qiskit_circ: QuantumCircuit, var_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a Qiskit circuit to a Pytket QASM file."""
    from pytket.extensions.qiskit import qiskit_to_tk
    from pytket.qasm import circuit_to_qasm_str

    # Convert Qiskit circuit to Pytket format and save as QASM
    tket_circ = qiskit_to_tk(qiskit_circ.decompose().decompose())
    qasm_str_tket = circuit_to_qasm_str(
        tket_circ, header="qelib1", maxwidth=200)

    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_pytket = current_file.with_name(
            f"{file_stem}_{var_name}_pytket.qasm")
    else:
        file_path_pytket = Path(abs_output_file)

    with open(file_path_pytket, 'w') as f:
        f.write(qasm_str_tket)

    print(f"Saved the Pytket circuit to {file_path_pytket}")
    return file_path_pytket.as_posix()

def export_to_qasm_with_qiskit(
        qiskit_circ: QuantumCircuit, var_name: str,
        abs_output_file: str = None) -> Optional[str]:
    """Export a Qiskit circuit to a Qiskit QASM file."""
    from qiskit import qasm2

    # Determine file path
    if not abs_output_file:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_qiskit = current_file.with_name(
            f"{file_stem}_{var_name}_qiskit.qasm")
    else:
        file_path_qiskit = Path(abs_output_file)

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
# <START_FUNCTIONS_OPTIMIZE>
def optimize_with_pennylane(
        pnqc, var_name: str,
        output_dir: Optional[str] = None):
    """Optimize a PennyLane circuit and export as qasm."""
    import pennylane as qml
    from pennylane.tape import QuantumTape
    from copy import deepcopy

    # print("Un-optimized PennyLane circuit:")
    # print(qml.draw(pnqc)())

    # print("Optimized PennyLane circuit:")
    optimized_circuit = deepcopy(pnqc)
    optimized_circuit = qml.compile(optimized_circuit)
    # optimized_circuit = qml.transforms.cancel_inverses(optimized_circuit)
    # optimized_circuit = qml.transforms.merge_rotations(optimized_circuit)
    # optimized_circuit = qml.transforms.single_qubit_fusion(optimized_circuit)
    # print(qml.draw(optimized_circuit)())
    # Define measurement and PennyLane device
    # measurements = [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    # circuit_fn = qml.from_qiskit(
    #     simplified_qiskit_circ, measurements=measurements)

    # add one measurement to the circuit
    dev = qml.device('default.qubit', wires=128)

    @qml.qnode(dev)
    def optimized_circuit_qnode():
        optimized_circuit()
        return qml.expval(qml.PauliZ(0))

    # Extract the QASM from the PennyLane QNode
    with QuantumTape(shots=10) as tape:
        optimized_circuit_qnode.construct([], {})
        qasm_str_pennylane = optimized_circuit_qnode.tape.to_openqasm(
            wires=sorted(
                tape.wires))

    # Determine file path
    if output_dir is not None:
        file_path_pennylane = Path(
            output_dir) / f"{var_name}_optimized_pennylane.qasm"
    else:
        current_file = Path(__file__)
        file_stem = current_file.stem
        file_path_pennylane = current_file.with_name(
            f"{file_stem}_{var_name}_optimized_pennylane.qasm")

    # Save PennyLane QASM string to file
    with open(file_path_pennylane, 'w') as f:
        f.write(qasm_str_pennylane)

    print(f"Saved Optimized PennyLane circuit to {file_path_pennylane}")

def optimize_with_pytket(
        tkqc, var_name: str, output_dir: Optional[str] = None):
    """Optimize a pytket circuit and export as qasm."""
    from pytket.qasm import circuit_to_qasm_str
    from pytket.passes import (
        FullPeepholeOptimise, PeepholeOptimise2Q, RemoveRedundancies,
        EulerAngleReduction, KAKDecomposition,
        CliffordPushThroughMeasures, FlattenRegisters,
        PauliSimp, GreedyPauliSimp,
        OptimisePhaseGadgets,
        ZXGraphlikeOptimisation
    )
    from pytket.circuit import OpType

    optimization_passes = {
        "FullPeepholeOptimise": FullPeepholeOptimise(),
        "PeepholeOptimise2Q": PeepholeOptimise2Q(),
        "RemoveRedundancies": RemoveRedundancies(),
        "EulerAngleReduction": EulerAngleReduction(q=OpType.Rz, p=OpType.Rx),
        "KAKDecomposition": KAKDecomposition(),
        "CliffordPushThroughMeasures": CliffordPushThroughMeasures(),
        "FlattenRegisters": FlattenRegisters(),
        "PauliSimp": PauliSimp(),
        "GreedyPauliSimp": GreedyPauliSimp(),
        "OptimisePhaseGadgets": OptimisePhaseGadgets(),
        "ZXGraphlikeOptimisation": ZXGraphlikeOptimisation()
    }

    for opt_pass_name, optimization_pass in optimization_passes.items():
        i_qc = deepcopy(tkqc)
        optimization_pass.apply(i_qc)
        i_opt_circuit_qasm = circuit_to_qasm_str(
            i_qc, header="qelib1", maxwidth=200)

        # Determine file path
        if output_dir is not None:
            file_path_pytket = Path(
                output_dir) / f"{var_name}_{opt_pass_name}_pytket.qasm"
        else:
            current_file = Path(__file__)
            file_stem = current_file.stem
            file_path_pytket = current_file.with_name(
                f"{file_stem}_{var_name}_{opt_pass_name}_pytket.qasm")

        with open(file_path_pytket, 'w') as f:
            f.write(i_opt_circuit_qasm)

        print(
            f"Saved Optimized Pytket circuit ({opt_pass_name}) to {file_path_pytket}")

def optimize_with_qiskit(
        qiskit_circ: QuantumCircuit, var_name: str,
        output_dir: Optional[str] = None):
    """Optimize a Qiskit circuit and export as qasm."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit.qasm2 import dump

    for optimization_level in range(4):
        pass_manager = generate_preset_pass_manager(
            optimization_level=optimization_level,
            seed_transpiler=12345)
        i_qc = deepcopy(qiskit_circ)
        i_qc = pass_manager.run(i_qc)

        # Determine file path
        if output_dir is not None:
            file_path_qiskit = Path(
                output_dir) / f"{var_name}_opt_level_{optimization_level}_qiskit.qasm"
        else:
            current_file = Path(__file__)
            file_stem = current_file.stem
            file_path_qiskit = current_file.with_name(
                f"{file_stem}_{var_name}_opt_level_{optimization_level}_qiskit.qasm")

        # Save Qiskit circuit directly to QASM
        dump(i_qc, file_path_qiskit)

        print(
            f"Saved Optimized Qiskit circuit (optimization level {optimization_level}) to {file_path_qiskit}")

# <END_FUNCTIONS_OPTIMIZE>
# <START_ORACLE_FUNCTIONS>

from typing import List, Callable, Dict, Any
import sys
import inspect
import json
import time
from copy import deepcopy
import traceback
import uuid
from pathlib import Path
from qiskit import QuantumCircuit
from itertools import combinations


from pytket.extensions.qiskit import qiskit_to_tk as converter_to_pytket
from pennylane import from_qiskit as converter_to_pennylane
from bqskit.ext import qiskit_to_bqskit as converter_to_bqskit
from itertools import combinations


def get_functions(prefix: str) -> Dict[str, Callable]:
    """
    Finds all functions in the current module that start with the given prefix
    and returns a list of these functions without executing them.

    Args:
        prefix (str): The prefix to filter functions by.

    Returns:
        Dict[str, Callable]: A dictionary with the platform name as key and
        the function as value.
    """
    current_module = sys.modules[__name__]
    functions = inspect.getmembers(current_module, inspect.isfunction)
    # Filter functions that start with the given prefix
    filtered_functions = [(name, func) for name, func in functions
                          if name.startswith(prefix)]
    # return a dictionary with the last word after _ as key
    # and the function as value
    dict_filtered_functions = {
        name.split("_")[-1]: func for name, func in filtered_functions}
    return dict_filtered_functions


def log_exception_to_json(
    exception: Exception,
    stack_trace: str,
    involved_functions: List[str],
    output_dir: str = None,
    extra_info: Dict[str, Any] = None,
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

    if output_dir:
        log_file_path = Path(output_dir) / log_file_name

    # Create a log dictionary with all details
    log_details: Dict[str, Any] = {
        "exception_message": str(exception),
        "stack_trace": stack_trace,
        "current_file": current_file.name,
        "involved_functions": involved_functions,
        "timestamp": time.time(),
        "extra_info": extra_info,
    }

    # Write the log details to a JSON file
    with log_file_path.open("w") as json_file:
        json.dump(log_details, json_file, indent=4)

    print(f"Log has been saved to {log_file_path}")


def get_copy_of_all_circuits_vars() -> Dict[str, QuantumCircuit]:
    """
    Returns a copy of all QuantumCircuit variables in the current module.

    Returns:
        Dict[str, QuantumCircuit]: A dictionary with variable names as keys and QuantumCircuit objects as values.
    """
    all_circuits_vars = {
        var_name: deepcopy(var_value)
        for var_name, var_value in globals().items()
        if isinstance(var_value, QuantumCircuit)
    }
    return all_circuits_vars


def oracle_exporter(output_dir: str = None) -> None:
    """Run all the oracle functions to export QASM files.

    If no output directory is provided, the QASM files will be saved in the
    current directory.
    """
    export_calls = get_functions(prefix="export_to_qasm_with_")

    all_circuits_vars = get_copy_of_all_circuits_vars()

    if output_dir:
        abs_path_output_dir = Path(output_dir).resolve()

    for var_name, target_qc in all_circuits_vars.items():
        for platform, export_call in export_calls.items():
            try:
                if output_dir:
                    abs_output_file = abs_path_output_dir / \
                        f"{var_name}_{platform}_exporter.qasm"
                else:
                    abs_output_file = None
                qc_to_export = deepcopy(target_qc)
                qasm_file = export_call(
                    qiskit_circ=qc_to_export,
                    var_name=var_name,
                    abs_output_file=abs_output_file)
            except Exception as e:
                stack_trace = traceback.format_exc()
                involved_functions = [export_call.__name__]
                log_exception_to_json(
                    e, stack_trace, involved_functions,
                    output_dir=output_dir)


def oracle_optimizer(output_dir: str = None) -> None:
    """Run all the oracle functions to optimize the QC and export QASM files.

    If no output directory is provided, the QASM files will be saved in the
    current directory.
    """
    optimize_calls = get_functions(prefix="optimize_with_")

    all_circuits_vars = get_copy_of_all_circuits_vars()

    def converter_to_qiskit(qc: QuantumCircuit) -> QuantumCircuit:
        return qc

    converters_calls = {
        "bqskit": converter_to_bqskit,
        "pytket": converter_to_pytket,
        "pennylane": converter_to_pennylane,
        "qiskit": converter_to_qiskit
    }

    if output_dir:
        abs_path_output_dir = Path(output_dir).resolve()
    else:
        abs_path_output_dir = None

    for var_name, target_qc in all_circuits_vars.items():
        for platform, platform_specific_optimize_call in optimize_calls.items():
            converter_call = converters_calls.get(platform)
            try:
                qc_to_convert = deepcopy(target_qc)
                platform_specific_qc = converter_call(qc_to_convert)
                qasm_file = platform_specific_optimize_call(
                    platform_specific_qc,
                    var_name=var_name,
                    output_dir=abs_path_output_dir)
            except Exception as e:
                stack_trace = traceback.format_exc()
                involved_functions = [
                    converter_call.__name__,
                    platform_specific_optimize_call.__name__,
                ]
                log_exception_to_json(
                    e, stack_trace, involved_functions,
                    output_dir=output_dir)


def oracle_importer(input_dir: str = None) -> None:
    """Run all the oracle functions to import QASM files.

    If no input directory is provided, the QASM files will be read from the
    current directory.
    """
    parser_calls = get_functions(prefix="import_from_qasm_with_")

    if input_dir:
        dir_w_qasm = Path(input_dir)
    else:
        dir_w_qasm = Path(".")

    for qasm_file in dir_w_qasm.glob("*.qasm"):
        for platform, parser_call in parser_calls.items():
            try:
                parsed_qc = parser_call(str(qasm_file))
            except Exception as e:
                stack_trace = traceback.format_exc()
                involved_functions = [parser_call.__name__]
                extra_info = {"input_qasm_file": str(qasm_file)}
                platform_generating_programs = [
                    pname for pname in parser_calls.keys()
                    if pname in qasm_file.stem]
                if len(platform_generating_programs) > 0:
                    extra_info["platform_generating_programs"] = platform_generating_programs
                log_exception_to_json(
                    e, stack_trace, involved_functions,
                    extra_info=extra_info,
                    output_dir=input_dir)


def oracle_comparator(input_dir: str = None) -> None:
    """Run all the oracle functions to compare QASM files.

    If no input directory is provided, the QASM files will be read from the
    current directory.
    """
    compare_calls = get_functions(prefix="compare_qasm_via_")

    if input_dir:
        dir_w_qasm = Path(input_dir)
    else:
        dir_w_qasm = Path(".")

    qasm_files = list(dir_w_qasm.glob("*.qasm"))
    combinations_of_qasm_files = combinations(qasm_files, 2)

    for pair in combinations_of_qasm_files:
        for comparator_name, compare_call in compare_calls.items():
            try:
                compare_call(pair[0], pair[1])
            except Exception as e:
                stack_trace = traceback.format_exc()
                involved_functions = [compare_call.__name__]
                extra_info = {
                    "qasm_file_1": str(pair[0]),
                    "qasm_file_2": str(pair[1]),
                }
                log_exception_to_json(
                    e, stack_trace, involved_functions,
                    extra_info=extra_info,
                    output_dir=input_dir)

# def oracle_call() -> None:

#     all_circuits_vars = get_copy_of_all_circuits_vars()

#     for key, value in all_circuits_vars.items():
#         target_qc = value
#         var_name = key

#         # Section: Stage - QASM Exporter
#         export_calls = get_functions(prefix="export_to_qasm")
#         qasm_files_with_provenance = []
#         for export_call in export_calls:
#             try:
#                 qasm_file = export_call(
#                     qiskit_circ=target_qc,
#                     var_name=var_name,
#                 )
#                 qasm_files_with_provenance.append(
#                     (qasm_file, export_call.__name__))
#             except Exception as e:
#                 stack_trace = traceback.format_exc()
#                 involved_functions = [export_call.__name__]
#                 log_exception_to_json(e, stack_trace, involved_functions)

#         if len(qasm_files_with_provenance) > 0:
#             print(f"Exported QASM files: {qasm_files_with_provenance}")
#         else:
#             print("No QASM files exported.")
#             exit(0)

#         # Section: Stage - Optimization
#         optimize_calls = get_functions(prefix="optimize_with_")

#         converters = [
#             converter_to_bqskit,
#             converter_to_pytket,
#             converter_to_pennylane
#         ]
#         for optimize_call in optimize_calls:
#             try:
#                 from copy import deepcopy
#                 i_qc = deepcopy(target_qc)
#             except Exception as e:
#                 stack_trace = traceback.format_exc()
#                 involved_functions = [optimize_call.__name__]
#                 log_exception_to_json(e, stack_trace, involved_functions)

#         # Section: Stage - QASM Parser
#         new_qasm_files_with_provenance = deepcopy(qasm_files_with_provenance)
#         parser_calls = get_functions(prefix="import_from_qasm")
#         for parser_call in parser_calls:
#             for qasm_file, export_call_name in qasm_files_with_provenance:
#                 try:
#                     parsed_qc = parser_call(qasm_file)
#                     # Section: Stage - Optimization
#                     for optimize_call in optimize_calls:
#                         # check that parser and optimizer are of the same platform
#                         # because we need to parse QASM to a circuit object
#                         # of a specific platform and the we can optimize it only
#                         # with the optimizer of the same platform
#                         if all(
#                             not (
#                                 platform in parser_call.__name__ and platform in optimize_call.__name__)
#                             for platform in ["qiskit", "bqskit", "pennylane", "bqskit"]
#                         ):
#                             continue

#                         try:
#                             optimized_files = optimize_call(
#                                 parsed_qc, var_name=var_name, output_dir=".")
#                             for optimized_file in optimized_files:
#                                 new_qasm_files_with_provenance.append(
#                                     (optimized_file, optimize_call.__name__))
#                         except Exception as e:
#                             stack_trace = traceback.format_exc()
#                             involved_functions = [
#                                 export_call_name,
#                                 parser_call.__name__,
#                                 optimize_call.__name__]
#                             log_exception_to_json(
#                                 e, stack_trace, involved_functions)
#                 except Exception as e:
#                     stack_trace = traceback.format_exc()
#                     involved_functions = [
#                         parser_call.__name__, export_call_name]
#                     log_exception_to_json(e, stack_trace, involved_functions)

#         # Section: Stage - Comparison
#         from itertools import combinations

#         compare_calls = get_functions(prefix="compare_qasm_")
#         for pair in combinations(new_qasm_files_with_provenance, 2):
#             a_file, a_exporter = pair[0]
#             b_file, b_exporter = pair[1]
#             for compare_call in compare_calls:
#                 try:
#                     compare_call(a_file, b_file)
#                 except Exception as e:
#                     stack_trace = traceback.format_exc()
#                     involved_functions = [
#                         compare_call.__name__, a_exporter, b_exporter]
#                     log_exception_to_json(e, stack_trace, involved_functions)

# <END_ORACLE_FUNCTIONS>


# Section: Test Oracle Calls
# <START_TEST_ORACLE_CALLS>
oracle_exporter()
oracle_optimizer()
oracle_importer()
oracle_comparator()
# <END_TEST_ORACLE_CALLS>







