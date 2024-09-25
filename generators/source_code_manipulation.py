import inspect
import importlib
from typing import List


def get_source_code_functions_w_prefix(
        prefix: str, module: str) -> str:
    """Get the source code of the functions with the given prefix from the module."""
    functions = inspect.getmembers(module, inspect.isfunction)
    filtered_functions = [
        func for name, func in functions if name.startswith(prefix)]
    # get source code of the functions
    filtered_functions = [inspect.getsource(
        func) for func in filtered_functions]
    return "\n".join(filtered_functions)


def get_functions_w_prefix(
    file_path: str, prefix: str
) -> List[str]:
    """Get the functions with the given prefix from the module."""
    module = importlib.import_module(file_path)
    functions = inspect.getmembers(module, inspect.isfunction)
    filtered_functions = [
        name for name, func in functions if name.startswith(prefix)]
    return filtered_functions
