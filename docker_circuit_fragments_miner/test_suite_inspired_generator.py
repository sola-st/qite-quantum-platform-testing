"""Script to convert the test suite into a generator of quantum programs.

The ideas is to walk through all the files in the test suite and instrument them
by adding an import statement to the top of the file and a call to the
`from instrumental_logger import log_circuit_function` after each statement.
It traverses the AST of the file and adds the import statement and the call to
`log_circuit_function` after each statement.

Arguments:
--test_suite_path: Path to the test suite directory.
--output_path: Path to the output directory. (created if it does not exist)

# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- avoid function with a single line which is a function call
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib every time that paths are checked, created or composed.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate
- make sure that any output folder exists before storing file in it, otherwise create it.

Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports

Example:
python -m generators.test_suite_inspired_generator --test_suite_path platform_repos/test_suite_example --output_path platform_repos/test_suite_example_instrumented
"""

import click
from pathlib import Path
import ast
from rich.console import Console
from typing import List
import shutil

console = Console()


@click.command()
@click.option('--test_suite_path', required=True, type=click.Path(exists=True),
              help='Path to the test suite directory.')
@click.option('--output_path', required=True, type=click.Path(),
              help='Path to the output directory. Will be created if it does not exist.')
@click.option('--abs_path_to_logger_file', required=True, type=click.Path(exists=True),
              default='/home/paltenmo/projects/crossplatform/generators/self_contained_logger.py',
              help='Absolute path to the logger file to be imported.')
def convert_test_suite(
    test_suite_path: Path, output_path: Path,
        abs_path_to_logger_file: Path) -> None:
    """Converts test suite files to generate quantum programs."""
    ensure_output_directory(output_path=Path(output_path))
    # if abs_path_to_logger_file is relative, make it absolute
    abs_path_to_logger_file = Path(abs_path_to_logger_file).resolve()
    test_files = get_python_files(test_suite_path=Path(test_suite_path))
    for file in test_files:
        instrument_file(
            file_path=file,
            input_path=Path(test_suite_path),
            output_path=Path(output_path),
            logger_file_path=Path(abs_path_to_logger_file))
    copy_non_python_files(
        test_suite_path=Path(test_suite_path),
        output_path=Path(output_path))


def copy_non_python_files(test_suite_path: Path, output_path: Path) -> None:
    """Copies non-Python files from the test suite to the output directory."""
    for file in test_suite_path.rglob('*'):
        if file.is_file() and file.suffix != '.py':
            relative_path = file.relative_to(test_suite_path)
            output_file = output_path / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, output_file)
            console.print(f"Non-Python file copied: {output_file}")


def ensure_output_directory(output_path: Path) -> None:
    """Ensures the output directory exists."""
    output_path.mkdir(parents=True, exist_ok=True)


def get_python_files(test_suite_path: Path) -> List[Path]:
    """Retrieves all Python files in the test suite directory."""
    return list(test_suite_path.rglob('*.py'))


def remove_from_future_prefix(tree: ast.AST) -> None:
    """Removes the `from __future__ import annotations` statement from the AST."""
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == '__future__':
            tree.body.remove(node)
    return tree


def add_from_future_prefix(tree: ast.AST) -> None:
    """Adds the `from __future__ import annotations` statement to the AST."""
    future_import = ast.ImportFrom(
        module='__future__',
        names=[ast.alias(name='annotations', asname=None)],
        level=0)
    tree.body.insert(0, future_import)
    return tree


def instrument_file(
        file_path: Path, input_path: Path, output_path: Path,
        logger_file_path: Path) -> None:
    """Instruments a file by adding import and log function calls."""
    tree = parse_file(file_path=file_path)
    tree = remove_from_future_prefix(tree=tree)
    new_tree = add_instrumentation(
        tree=tree,
        path=str(logger_file_path.parent),
        hidden_file=logger_file_path.stem)
    new_tree = add_from_future_prefix(tree=new_tree)
    write_instrumented_file(
        tree=new_tree, file_path=file_path, input_path=input_path,
        output_path=output_path)


def parse_file(file_path: Path) -> ast.AST:
    """Parses a Python file and returns its AST."""
    with file_path.open('r', encoding='utf-8') as file:
        return ast.parse(file.read())


def add_instrumentation(
        tree: ast.AST, path: str = '/my/path',
        log_function_name: str = 'log_quantum_circuits',
        hidden_file: str = 'hidden_file') -> ast.AST:
    """Adds instrumentation code to the AST."""
    tree = InstrumentationTransformer(
        log_function_name=log_function_name).visit(tree)

    import_sys_node = ast.Import(names=[ast.alias(name='sys', asname=None)])
    sys_path_append_node = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='sys', ctx=ast.Load()),
                attr='path.append', ctx=ast.Load()),
            args=[ast.Constant(value=path)],
            keywords=[]))
    import_log_node = ast.ImportFrom(
        module=hidden_file,
        names=[ast.alias(name=log_function_name, asname=None)],
        level=0)

    # Adds the import from hidden_file at the top
    tree.body.insert(0, import_log_node)
    # Adds sys.path.append(path) at the top
    tree.body.insert(0, sys_path_append_node)
    tree.body.insert(0, import_sys_node)  # Adds import sys at the top

    ast.fix_missing_locations(tree)
    return tree


class InstrumentationTransformer(ast.NodeTransformer):
    """AST NodeTransformer to insert log calls after each statement recursively."""

    def __init__(self, log_function_name: str) -> None:
        self.log_function_name = log_function_name

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Inserts log calls after each statement within a function."""
        node.body = self.instrument_statements(node.body)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Inserts log calls after each statement within class methods."""
        node.body = [self.visit(stmt) for stmt in node.body]
        return node

    # do it also for loops, if, etc.
    def visit_If(self, node: ast.If) -> ast.If:
        """Inserts log calls after each statement within an if block."""
        node.body = self.instrument_statements(node.body)
        node.orelse = self.instrument_statements(node.orelse)
        return node

    def visit_For(self, node: ast.For) -> ast.For:
        """Inserts log calls after each statement within a for loop."""
        node.body = self.instrument_statements(node.body)
        return node

    def visit_While(self, node: ast.While) -> ast.While:
        """Inserts log calls after each statement within a while loop."""
        node.body = self.instrument_statements(node.body)
        return node

    # try except, etc.
    def visit_Try(self, node: ast.Try) -> ast.Try:
        """Inserts log calls after each statement within a try block."""
        node.body = self.instrument_statements(node.body)
        return node

    def visit_ExceptHandler(
            self, node: ast.ExceptHandler) -> ast.ExceptHandler:
        """Inserts log calls after each statement within an except block."""
        node.body = self.instrument_statements(node.body)
        return node

    def visit_With(self, node: ast.With) -> ast.With:
        """Inserts log calls after each statement within a with block."""
        node.body = self.instrument_statements(node.body)
        return node

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Inserts log calls after each statement within a module."""
        node.body = self.instrument_statements(node.body)
        return node

    def instrument_statements(self, statements: List[ast.stmt]) -> List[ast.stmt]:
        """Inserts log calls after each statement in a given list of statements."""
        instrumented = []
        for stmt in statements:
            instrumented.append(stmt)
            # Only add logging after significant statements (e.g., not imports)
            if not isinstance(stmt, (ast.Import, ast.ImportFrom)):
                instrumented.append(self._create_log_call_node())
        return instrumented

    def _create_log_call_node(self) -> ast.Expr:
        """Creates a log call node for instrumentation."""
        return ast.Expr(value=ast.Call(
            func=ast.Name(id=self.log_function_name, ctx=ast.Load()),
            args=[ast.Call(
                func=ast.Name(id='locals', ctx=ast.Load()),
                args=[], keywords=[])],
            keywords=[]))


def write_instrumented_file(
        tree: ast.AST, file_path: Path, input_path: Path, output_path: Path) -> None:
    """Writes the instrumented AST to a new file in the output directory, preserving folder structure."""
    relative_path = file_path.relative_to(input_path)
    output_file = output_path / relative_path
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open('w', encoding='utf-8') as file:
        file.write(ast.unparse(tree))
    console.print(f"Instrumented file saved: {output_file}")


if __name__ == '__main__':
    """Main function to run the test suite converter."""
    console.print("Converting test suite into quantum program generator...")
    convert_test_suite()
