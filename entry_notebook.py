"""The script executes a notebook with papermill using parameters from a yaml file.

The script takes the following arguments:
- notebook: The notebook file to execute (default folder: notebooks, consider only .ipynb files)
- config: The yaml file with parameters (default folder: config/notebooks)
- output: The output folder to store the resulting file (default: data/notebooks)
In case one parameters is not provided, the script should query the user interactively for the missing parameters.

The output file should have the same name as the input notebook file plus
the current date and time in the format YYYY_MM_DD_HH_MM followed by
the name of the configuration file (replacing the spaces with underscores).
e.g. notebook_2021_09_01_12_30_config_file_name.ipynb

It then executes the notebook with the parameters in the yaml file.
The resulting file is stored in the output folder.

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
"""
import click
import yaml
from pathlib import Path
from rich.console import Console
import papermill as pm
from datetime import datetime
from typing import Optional


console = Console()


def load_yaml_config(config_path: Path) -> dict:
    """Load parameters from a yaml file."""
    with config_path.open('r') as file:
        return yaml.safe_load(file)


def ensure_output_folder_exists(output_folder: Path) -> None:
    """Ensure the output folder exists, create if not."""
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)


def execute_notebook(notebook: Path, config: dict, output: Path) -> None:
    """Execute the notebook with the given parameters."""
    pm.execute_notebook(
        input_path=str(notebook),
        output_path=str(output),
        parameters=config
    )


def list_files_in_folder(folder: Path, extension: str) -> Path:
    """List all files with the given extension in the folder and ask the user to pick one."""
    files = list(folder.glob(f'*.{extension}'))
    if not files:
        console.log(f"No {extension} files found in the folder {folder}.")
        raise click.ClickException(
            f"No {extension} files found in the folder {folder}.")

    files.sort(key=lambda x: x.name, reverse=True)

    for i, file in enumerate(files, start=1):
        console.log(f"{i}: {file.name}")

    choice = click.prompt(
        f"Please choose a {extension} file by number", type=int)
    if choice < 1 or choice > len(files):
        raise click.ClickException("Invalid choice.")

    return files[choice - 1]


@click.command()
@click.option('--notebook', required=False, type=click.Path(
    exists=True, dir_okay=False, path_type=Path),
    help='The notebook file to execute.')
@click.option('--config', required=False, type=click.Path(
    exists=True, dir_okay=False, path_type=Path),
    help='The yaml file with parameters.')
@click.option('--output', required=True, default='data/notebooks_executions',
              type=click.Path(file_okay=False, path_type=Path),
              help='The output folder to store the resulting file.')
def main(
        notebook: Optional[Path],
        config: Optional[Path],
        output: Path) -> None:
    """Main function to execute the notebook with parameters from yaml file."""
    if notebook is None:
        notebook = list_files_in_folder(
            folder=Path('notebooks'),
            extension='ipynb')

    if config is None:
        config = list_files_in_folder(
            folder=Path('config/notebooks'),
            extension='yaml')

    if config.is_dir():
        config_files = list(config.glob('*.yaml'))
        macro_experiment_name = config.stem
        if not config_files:
            raise click.ClickException(
                f"No yaml files found in the folder {config}.")
    else:
        macro_experiment_name = ""
        config_files = [config]

    for config_file in config_files:
        config_data = load_yaml_config(config_path=config_file)
        ensure_output_folder_exists(output_folder=output)
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M')
        config_name = config_file.stem.replace(' ', '_')
        output_file = output / \
            f"{notebook.stem}_{timestamp}_{macro_experiment_name}_{config_name}.ipynb"
        execute_notebook(notebook=notebook,
                         config=config_data, output=output_file)
        console.log(f"Notebook executed and saved to {output_file}")


if __name__ == '__main__':
    main()

    # Example of call:
    # python entry_notebook.py --notebook notebooks/example_notebook.ipynb --config config/notebooks/example_config.yaml --output data/notebooks
