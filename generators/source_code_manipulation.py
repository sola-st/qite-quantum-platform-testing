
import astor
import ast
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


def get_function_names_starting_with_prefix(
        source_code: str, prefix: str) -> List[str]:
    """Get the names of the functions starting with the given prefix."""
    lines = source_code.split("\n")
    # get all lines starting with "def "
    function_lines = [line for line in lines
                      if line.strip().startswith("def ")]
    # get the function names starting with the prefix
    function_names = [line.split("(")[0].split("def ")[1]
                      for line in function_lines]
    # filter the function names starting with the prefix
    function_names = [name for name in function_names
                      if name.startswith(prefix)]
    return function_names


class FunctionRemover(ast.NodeTransformer):
    """AST transformer to remove specified first-level functions."""

    def __init__(self, functions_to_remove: List[str]):
        self.functions_to_remove = set(functions_to_remove)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Remove the function if its name is in the removal list."""
        if node.name in self.functions_to_remove:
            return None  # Remove this function
        return self.generic_visit(node)  # Visit other nodes


def remove_first_lvl_functions(
        source_code: str, functions_to_remove: List[str]) -> str:
    """Remove the given first-level functions from the source code.

    Use the ast module to parse the source code and remove the functions.
    """
    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Create a function remover instance
    remover = FunctionRemover(functions_to_remove)

    # Transform the AST to remove specified functions
    modified_tree = remover.visit(tree)

    # Convert the modified AST back to source code
    return astor.to_source(modified_tree)
