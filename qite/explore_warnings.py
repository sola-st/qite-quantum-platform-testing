import click
import json
import os
import pandas as pd
from pathlib import Path
from multiprocessing import Pool
from rich.console import Console
from rich.table import Table
from typing import List, Dict, Any
from rich.prompt import IntPrompt
import inquirer


console = Console()


def get_top_errors(
        df: pd.DataFrame, top_k: int, target_column: str) -> pd.DataFrame:
    error_counts = df[target_column].value_counts().head(top_k).reset_index()
    error_counts.columns = [target_column.capitalize(), 'Count']
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


def print_top_errors(error_counts: pd.DataFrame, top_k: int,
                     target_column: str) -> None:
    n_total_errors = error_counts['Count'].sum()
    table = Table(
        title=f"Top {top_k} Most Frequent {target_column.capitalize()}s "
        f"(total {target_column}s: {n_total_errors})")
    table.add_column(target_column.capitalize(), justify="left")
    table.add_column("Count", justify="right")
    for _, row in error_counts.iterrows():
        table.add_row(row[target_column.capitalize()], str(row['Count']))
    console.print(table)


def get_files_with_error(
        df: pd.DataFrame, error_msg: str, target_column: str, max_n_files: int = 3) -> List[str]:
    """Get file paths with a specific error message."""
    error_files = df[df[target_column] == error_msg].head(max_n_files)
    return error_files['file_path'].tolist()


def prompt_user_for_error_selection(
        top_errors: pd.DataFrame, target_column: str) -> int:
    """Prompt the user to select an error index."""
    choices = [(f"{i}: {row[target_column.capitalize()]}", i)
               for i, row in top_errors.iterrows()]
    truncated_choices = []
    max_width = console.width - 10
    for choice, i in choices:
        choice = choice.replace("\n", " (NL)")
        if len(choice) > max_width:
            choice = choice[:max_width] + "..."
        truncated_choices.append((choice, i))
    question = [
        inquirer.List(
            'error_index',
            message=f"Please select a {target_column} index to get file paths",
            choices=truncated_choices,
        )
    ]
    answers = inquirer.prompt(question)
    return answers['error_index']


def display_files_with_error(
        df: pd.DataFrame, error_msg: str, target_column: str) -> None:
    """Display file paths with a specific error message."""
    error_files = get_files_with_error(
        df=df, error_msg=error_msg, target_column=target_column)
    if error_files:
        choices = [(file, file) for file in error_files]
        question = [
            inquirer.List(
                'file_path',
                message=f"Select a file with {target_column} '{error_msg}' to process",
                choices=choices,)]
        answers = inquirer.prompt(question)
        selected_file = answers['file_path']

        console.print(f"Selected file: {selected_file}")
        if target_column == "equivalence":
            comparison_metadata = selected_file
            input_folder = str(Path(selected_file).parent.parent)
            output_folder = str(Path(input_folder) / "minimize_comparison")

            command = f"python -m qite.delta_debugging_comparison --comparison_metadata {comparison_metadata} --input_folder {input_folder} --output_folder {output_folder}"
            console.print(f"Running command: {command}")
            os.system(command)
        elif target_column == "error":
            error_json = selected_file
            input_folder = str(Path(selected_file).parent.parent)
            output_folder = str(Path(input_folder) / "minimized")

            command = f"python -m qite.delta_debugging --error_json {error_json} --input_folder {input_folder} --output_folder {output_folder}"
            console.print(f"Running command: {command}")
            os.system(command)
    else:
        console.print(f"No files found with {target_column} '{error_msg}'")


@click.command()
@click.option('--folder_path', required=True, type=click.Path(
    exists=True, file_okay=False, dir_okay=True,
    path_type=Path), help='Path to the folder containing JSON files.')
@click.option('--top_k', default=3, help='Number of top errors to display.')
@click.option('--target_field', default='error',
              help='Target field to analyze (must be top-level field).')
def main(folder_path: Path, top_k: int, target_field: str) -> None:
    """Main CLI command to process JSON files and display top errors."""
    df = process_files_in_parallel(folder_path=folder_path)
    if target_field not in df.columns:
        console.log(f"No '{target_field}' field found in any JSON file.")
        return
    top_errors = get_top_errors(
        df=df, top_k=top_k, target_column=target_field)
    print_top_errors(error_counts=top_errors, top_k=top_k,
                     target_column=target_field)

    error_index = prompt_user_for_error_selection(
        top_errors=top_errors, target_column=target_field)
    error_msg = top_errors.iloc[error_index][target_field.capitalize()]
    display_files_with_error(df=df, error_msg=error_msg,
                             target_column=target_field)

# Example usage:
# python -m qite.explore_warnings --folder_path program_bank/v024/2025_02_05__23_59/error --top_k 3


if __name__ == "__main__":
    main()


# Target folder for example: program_bank/v024/2025_02_05__23_59/error
