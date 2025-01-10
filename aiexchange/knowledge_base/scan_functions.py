
import os
import ast
import json
import argparse
from pathlib import Path


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
            print(f"Error parsing {file_path}: {e}")


def scan_folder(path_to_local_folder: str):
    """Scan the folder and extract API details from Python files."""
    visitor = APIVisitor()
    path = Path(path_to_local_folder)
    for file_path in path.rglob('*.py'):
        print(f"Parsing file: {file_path}")
        visitor.parse(file_path=str(file_path))
    return visitor.api_data


def save_to_json(api_list: list, output_path: str):
    """Save the extracted API details to a JSON file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(api_list, outfile, indent=4)
    print(f"Saved API data to {output_path}")


def main():
    """Main function to scan folder and extract APIs."""
    parser = argparse.ArgumentParser(
        description='Scan folder and extract API details.')
    parser.add_argument('--path_to_local_folder', type=str, required=True,
                        help='Path containing the repo to scan.')
    parser.add_argument('--output_path', type=str, required=True,
                        help='Path to the JSON file to store the API data.')
    args = parser.parse_args()

    print("Starting API extraction process.")
    api_list = scan_folder(path_to_local_folder=args.path_to_local_folder)
    save_to_json(api_list=api_list, output_path=args.output_path)
    print("API extraction completed.")


if __name__ == "__main__":
    main()
