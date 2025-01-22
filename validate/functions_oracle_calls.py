
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


from pytket.extensions.qiskit import qiskit_to_tk as converter_to_pytket
from pennylane import from_qiskit as converter_to_pennylane
from bqskit.ext import qiskit_to_bqskit as converter_to_bqskit


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
    output_dir: str = None
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
                qasm_file = export_call(
                    qiskit_circ=target_qc,
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
                platform_specific_qc = converter_call(target_qc)
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
