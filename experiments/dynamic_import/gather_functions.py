
import inspect
import sys
from typing import List, Callable

# Define some example functions that start with 'export_'


def export_qiskit():
    print("Exporting with Qiskit!")


def export_pytket():
    print("Exporting with Pytket!")


def export_pennylane():
    print("Exporting with PennyLane!")


def not_export():
    print("This function does not start with 'export_'")

# Function to find all 'export_' functions and execute them


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


if __name__ == "__main__":
    export_functions = get_functions("export_")
    for func in export_functions:
        func()
        print(str(func.__name__))
