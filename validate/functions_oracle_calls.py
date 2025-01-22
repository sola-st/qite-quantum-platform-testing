
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
