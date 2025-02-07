import click
import json
import pandas as pd
from pathlib import Path
from multiprocessing import Pool
from rich.console import Console
from rich.table import Table
from typing import List, Dict, Any
from rich.prompt import IntPrompt
import inquirer

"""
Task Description:
-----------------
Implement a command line interface (CLI) script that processes JSON files in a given folder and outputs the top 3 most frequent error values with their counts in a formatted console output. The script should efficiently load all JSON files in parallel using a multiprocessing pool and store the data in a pandas DataFrame.

Requirements:
-------------
1. Input:
   - The script should accept a folder path as an input argument.
   - The folder contains JSON files, each with a single JSON object.
   - Each JSON object has a field "error" and other fields. All fields are at the top level (no nested fields).
   - Some JSON files might have fewer fields, but all will have the "error" field.

2. DataFrame:
   - Load all JSON files into a pandas DataFrame.
   - Include all fields from the JSON files in the DataFrame.
   - Handle missing fields or null values by including them as NaN in the DataFrame.

3. Error Field:
   - Ensure the "error" field is present in all JSON files.
   - If the "error" field is missing or null, handle it gracefully (e.g., skip the file or log a warning).

4. Parallel Processing:
   - Use a multiprocessing pool to load JSON files in parallel.
   - Limit the number of parallel processes/threads to a reasonable number to avoid overwhelming the system.

5. Output:
   - Calculate the top 3 most frequent error values and their counts.
   - Print the results in a formatted and "pretty" console output using a library like `tabulate` or `rich`.

6. Environment and Dependencies:
   - Use Python 3.x.
   - Required libraries: `pandas`, `json`, `multiprocessing`, `tabulate` or `rich`.

7. Error Handling:
   - Handle errors during file loading or JSON parsing gracefully.
   - Log errors to a file or display them in the console.

8. Testing and Validation:
   - Include unit tests to validate the script's functionality.
   - Ensure the script handles various edge cases, such as missing fields, empty JSON files, and large numbers of files.

Example Usage:
--------------
$ python process_json.py /path/to/json/folder

Expected Output:
----------------
+----------------+-------+
| Error Value    | Count |
+----------------+-------+
| error_value_1  | 10    |
| error_value_2  | 8     |
| error_value_3  | 5     |
+----------------+-------+

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
Make sure to add a function and call that function only in the main cli command.
The goal is to be able to import that function also from other files.


"""
console = Console()


def get_top_errors(df: pd.DataFrame, top_k: int) -> pd.DataFrame:
    error_counts = df['error'].value_counts().head(top_k).reset_index()
    error_counts.columns = ['Error Value', 'Count']
    return error_counts


def load_json_file(file_path: Path) -> Dict[str, Any]:
    try:
        with file_path.open('r') as file:
            data = json.load(file)
            data['file_path'] = str(file_path)
            return data
    except Exception as e:
        console.log(f"Error loading {file_path}: {e}")
        return {}


def process_files_in_parallel(folder_path: Path) -> pd.DataFrame:
    json_files = list(folder_path.glob('*.json'))
    with Pool() as pool:
        data = pool.map(load_json_file, json_files)
    return pd.DataFrame(data)


def print_top_errors(error_counts: pd.DataFrame, top_k: int) -> None:
    n_total_errors = error_counts['Count'].sum()
    table = Table(
        title=f"Top {top_k} Most Frequent Errors "
        f"(total errors: {n_total_errors})")
    table.add_column("Error Value", justify="left")
    table.add_column("Count", justify="right")
    for _, row in error_counts.iterrows():
        table.add_row(row['Error Value'], str(row['Count']))
    console.print(table)


def get_files_with_error(
        df: pd.DataFrame, error_msg: str, max_n_files: int = 3) -> List[str]:
    """Get file paths with a specific error message."""
    error_files = df[df['error'] == error_msg].head(max_n_files)
    return error_files['file_path'].tolist()


def prompt_user_for_error_selection(top_errors: pd.DataFrame) -> int:
    """Prompt the user to select an error index."""
    choices = [(f"{i}: {row['Error Value']}", i)
               for i, row in top_errors.iterrows()]
    truncated_choices = []
    max_width = console.width - 10
    print("Max width:", max_width)
    for choice, i in choices:
        if len(choice) > max_width:
            choice = choice[:max_width] + "..."
        truncated_choices.append((choice, i))
    question = [
        inquirer.List(
            'error_index',
            message="Please select an error index to get file paths",
            choices=truncated_choices,
        )
    ]
    answers = inquirer.prompt(question)
    return answers['error_index']


def display_files_with_error(df: pd.DataFrame, error_msg: str) -> None:
    """Display file paths with a specific error message."""
    error_files = get_files_with_error(df=df, error_msg=error_msg)
    if error_files:
        console.print(f"Files with error '{error_msg}':")
        for file in error_files:
            console.print(file)
    else:
        console.print(f"No files found with error '{error_msg}'")


@click.command()
@click.option('--folder_path', required=True, type=click.Path(
    exists=True, file_okay=False, dir_okay=True,
    path_type=Path), help='Path to the folder containing JSON files.')
@click.option('--top_k', default=3, help='Number of top errors to display.')
def main(folder_path: Path, top_k: int) -> None:
    """Main CLI command to process JSON files and display top errors."""
    df = process_files_in_parallel(folder_path=folder_path)
    if 'error' not in df.columns:
        console.log("No 'error' field found in any JSON file.")
        return
    top_errors = get_top_errors(df=df, top_k=top_k)
    print_top_errors(error_counts=top_errors, top_k=top_k)

    error_index = prompt_user_for_error_selection(top_errors=top_errors)
    error_msg = top_errors.iloc[error_index]['Error Value']
    display_files_with_error(df=df, error_msg=error_msg)

# Example usage:
# python -m qite.explore_warnings --folder_path program_bank/v024/2025_02_05__23_59/error --top_k 3


if __name__ == "__main__":
    main()


# Target folder for example: program_bank/v024/2025_02_05__23_59/error
