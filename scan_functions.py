"""Scripts that scans a folder and extracts all the API declared in a folder.

Given a folder path, it scans all the .py files in the folder and (using the AST)
library it collects all the function names and method names. For each method

--path_to_local_folder: str. path containing the repo to scan.
--output_path: str. path to the JSON file that stores all the API used in the library as a list of objects.
    Each object has the following infos:
    - api_name: name of the api (only function/method name, no args)
    - full_api_name: str. if a method, the name of the object must be pre-pended
        e.g. Object.my_method
    - api_description: str. docstring of the API
    - api_signature: str, function/method name with args
    - file_path: str. Make sure to store the relative path, namely remove the path_to_local_folder prefix

Example use:
    python scan_functions.py --path_to_local_folder platform_repos/mqt-qcec/ --output_path available_apis/mqt-qcec.json

# Implementation
- it uses click v8 library
- it has a simple main
- handle the case in which the file might not be parsable, log the error and continue
- make sure that the AST visitor appropriately logs in a field the current visited class, if any,
    so that it can correctly assign the full path to the functions inside it.
- add an init to the AST visitor to make sure that the parent is "" at the beginning
- also whenever exiting a class, the value of the filed becomes "" again.

# Style
- it uses subfunction appropriately
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses os.path every time that it is dealing with path composition
- it uses pathlib every time that paths are checked or created.
- when accessing a dictionary use .get() api and provide a default value.

"""
import os
import ast
import json
import click
from pathlib import Path
from rich.console import Console

console = Console()


class APIVisitor(ast.NodeVisitor):
    def __init__(self):
        self.api_data = []
        self.current_class = ""

    def visit_ClassDef(self, node):
        """Visit a class definition and set the current class name."""
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = ""  # Reset after finishing the class

    def visit_FunctionDef(self, node):
        """Visit a function or method definition."""
        api_name = node.name
        api_signature = f"{node.name}({', '.join([arg.arg for arg in node.args.args])})"
        api_description = ast.get_docstring(node) or ""
        full_api_name = f"{self.current_class}.{api_name}" if self.current_class else api_name

        self.api_data.append({
            "api_name": api_name,
            "full_api_name": full_api_name,
            "api_description": api_description,
            "api_signature": api_signature,
            "file_path": self.file_path,
        })
        self.generic_visit(node)

    def parse(self, file_path):
        """Parse the file and extract API details."""
        self.file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read(), filename=file_path)
            self.visit(tree)
        except (SyntaxError, UnicodeDecodeError) as e:
            console.log(f"[red]Error parsing {file_path}: {e}")


def scan_folder(path_to_local_folder: str):
    """Scan the folder and extract API details from Python files."""
    visitor = APIVisitor()
    path = Path(path_to_local_folder)
    for file_path in path.rglob('*.py'):
        console.log(f"Parsing file: {file_path}")
        visitor.parse(file_path=str(file_path))
    return visitor.api_data


def save_to_json(api_list: list, output_path: str):
    """Save the extracted API details to a JSON file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(api_list, outfile, indent=4)
    console.log(f"Saved API data to {output_path}")


@click.command()
@click.option('--path_to_local_folder', type=str, required=True,
              help='Path containing the repo to scan.')
@click.option('--output_path', type=str, required=True,
              help='Path to the JSON file to store the API data.')
def main(path_to_local_folder, output_path):
    """Main function to scan folder and extract APIs."""
    console.log("Starting API extraction process.")
    api_list = scan_folder(path_to_local_folder=path_to_local_folder)
    save_to_json(api_list=api_list, output_path=output_path)
    console.log("API extraction completed.")


if __name__ == "__main__":
    main()
