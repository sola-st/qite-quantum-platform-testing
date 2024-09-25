"""Script to minimize a python file containing a test case using delta debugging.

The script takes as inputs:
--input_folder: the folder containing the python file to minimize
--path_to_error: a path to a json file containing the error information

The output is a minimized python file that reproduces the error and it is stored
in the same folder with the same name of the error but with the suffix "_min.py"
instead of ".json".
The new file contains also a dump of the content of the error file as the
docstring of the file.

The python file has a section with the instructions which are the have to be
minimized. The instructions are enclosed in two lines with the following content:
# <START_GATES>
# <END_GATES>
The script will minimize the content between these two lines using the library
ddmin.py.


Convert the function above into a click v8 interface in Python.
- map all the arguments to a corresponding option (in click) which is required
- add all the default values of the arguments as default of the click options
- use only underscores
- add a main with the command
- add the required imports

# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib every time that paths are checked, created or composed.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate


Use the following code as inspiration.


"""
import analysis_and_reporting.ddmin_qiskit as dd
import json
import pathlib
from rich.console import Console
import click
import tempfile
from typing import List, Dict, Any, Tuple, Optional
from generators.source_code_manipulation import (
    get_function_names_starting_with_prefix,
    remove_first_lvl_functions,
)
from generators.docker_tooling import run_program_in_docker


console = Console()


def load_error_info(path_to_error: pathlib.Path) -> Tuple[str, Dict[str, Any]]:
    """Load error information from a JSON file and extract the filename."""
    with open(path_to_error, 'r') as f:
        error_info = json.load(f)

    # Get the current file name from the error info
    current_file = error_info.get("current_file", "unknown_file")
    return current_file, error_info


def extract_instructions(
        file_path: pathlib.Path, start_tag: str, end_tag: str) -> Tuple[
            List[str], List[str], List[str]]:
    """Extract instructions enclosed by start_tag and end_tag."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    start_index = next(i for i, line in enumerate(lines)
                       if line.strip() == start_tag)
    end_index = next(i for i, line in enumerate(lines)
                     if line.strip() == end_tag)

    before_chunk = lines[:start_index + 1]
    after_chunk = lines[end_index:]

    return before_chunk, lines[start_index + 1:end_index], after_chunk


# def repro_func(
#         lst_steps: List[str],
#         header: str = None, footer: str = None, error_clue: str = None) -> bool:
#     """Return False if any instruction contains 'ms'."""
#     return not any('ms' in step for step in lst_steps)


def repro_func(
        lst_steps: List[str],
        header: str = None, footer: str = None, error_clue: str = None) -> bool:
    """Run the python file in docker and return False if the exception contains the error clue.

    Run in docker.
    """
    # create a temporary directory to store the file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = pathlib.Path(temp_dir) / "to_execute.py"
        with open(temp_file_path, 'w') as f:
            f.write(header)
            f.write("".join(lst_steps))
            f.write(footer)

        # print file content
        # print(f"File content:\n{temp_file_path.read_text()}")

        # run the file in docker
        try:
            run_program_in_docker(
                folder_with_file=temp_dir,
                file_name=temp_file_path.name,
            )
            # check the new json if a new error is logged
            json_files_ending_with_error = [
                file for file in pathlib.Path(temp_dir).iterdir()
                if file.name.endswith("_error.json")
            ]
            if json_files_ending_with_error:
                with open(json_files_ending_with_error[0], 'r') as f:
                    error_info = json.load(f)
                    new_error_message = error_info.get("exception_message", "")
                    print(f"New exception message: {new_error_message}")
                    if error_clue in new_error_message:
                        return False
        except Exception as e:
            print(f"Error during docker: {e}")
            return True
    return True


def dump_json_with_max_length(data, indent=4, max_length=80):
    json_str = json.dumps(data, indent=indent)
    lines = json_str.split('\n')
    formatted_lines = []
    for line in lines:
        while len(line) > max_length:
            split_index = line.rfind(' ', 0, max_length)
            if split_index == -1:
                split_index = max_length
            formatted_lines.append(line[:split_index])
            line = ' ' * indent + line[split_index:].lstrip()
        formatted_lines.append(line)
    return '\n'.join(formatted_lines)


def save_minimized_file(minimized_content: List[str],
                        error_info: Dict[str, Any],
                        output_path: pathlib.Path,
                        header: str = None,
                        footer: str = None,
                        ) -> None:
    """Save the minimized content to a new Python file."""
    with open(output_path, 'w') as f:
        f.write('"""This is the content of the error message:\n')
        f.write(dump_json_with_max_length(error_info))
        f.write('\n"""\n')
        if header:
            f.write(header)
            f.write('\n')
        f.writelines(minimized_content)
        if footer:
            f.write('\n')
            f.write(footer)


def add_raise_exception_to_footer(footer: str) -> str:
    """Add raise exception after each log_exception_to_json call."""
    lines = footer.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if line.lstrip().startswith("log_exception_to_json"):
            number_of_spaces = len(line) - len(line.lstrip())
            new_lines.append(
                f"{' ' * number_of_spaces}raise e")
    return "\n".join(new_lines)


def minimize_instructions(input_folder: pathlib.Path,
                          path_to_error: pathlib.Path,
                          clue_message: str) -> None:
    """Minimize the instructions in the Python file based on error info."""
    current_file, error_info = load_error_info(path_to_error)
    current_file = pathlib.Path(current_file)
    python_file_path = input_folder / current_file

    # get the fixed header and footer
    header_lines, instructions, footer_lines = extract_instructions(
        file_path=python_file_path,
        start_tag='# <START_GATES>',
        end_tag='# <END_GATES>')
    header = "".join(header_lines)
    footer = "".join(footer_lines)

    # change the footer to contain only the functions related to the error
    involved_functions = error_info.get("involved_functions", [])
    console.log("Involved functions:")
    for function in involved_functions:
        console.log(f"  - {function}")
    # get all the function names in the footer starting with:
    # export_to_qasm, import_from_qasm, compare_qasm
    footer_functions = get_function_names_starting_with_prefix(
        footer, prefix="export_to_qasm")
    footer_functions += get_function_names_starting_with_prefix(
        footer, prefix="import_from_qasm")
    footer_functions += get_function_names_starting_with_prefix(
        footer, prefix="compare_qasm")

    # remove all the functions that are not in footer_functions
    functions_to_remove = [
        function for function in footer_functions
        if function not in involved_functions
    ]
    footer = remove_first_lvl_functions(
        source_code=footer, functions_to_remove=functions_to_remove)

    # add raise exception to the footer
    # footer = add_raise_exception_to_footer(footer)

    source_code = debugger = dd.DDMin(
        instructions, repro_func,
        kwargs_test_func={"header": header, "footer": footer,
                          "error_clue": clue_message})
    minimized_instructions = debugger.execute()

    output_file_path = input_folder / f"{path_to_error.stem}_min.py"
    save_minimized_file(
        minimized_instructions, error_info, output_file_path,
        header=header, footer=footer)

    console.log(f"[green]Minimized file saved as:[/green] {output_file_path}")


@click.command()
@click.option('--input_folder', type=click.Path(exists=True),
              required=True,
              help='Folder containing the Python file to minimize.')
@click.option('--path_to_error', type=click.Path(exists=True),
              required=True,
              help='Path to the JSON file containing the error info.')
@click.option('--clue_message', type=str,
              required=True,
              help='The clue message to look for in the error.')
def main(input_folder: str, path_to_error: str, clue_message: str) -> None:
    """Main function to run the minimization process."""
    minimize_instructions(input_folder=pathlib.Path(input_folder),
                          path_to_error=pathlib.Path(path_to_error),
                          clue_message=clue_message)


if __name__ == '__main__':
    main()
