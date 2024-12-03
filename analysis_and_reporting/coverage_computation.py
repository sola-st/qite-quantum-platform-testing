
import time
import json
import click
from pathlib import Path
from typing import List
import shutil
from rich.console import Console
from generators.docker_tooling import run_program_in_docker_pypi

"""This module computes the coverage of the generated programs in terms of platform code.

It computes the coverage of a list of pypi packages in terms of line sof code.
It scans all the programs in a given folder then it runs them in a docker container
with the function:

from generators.docker_tooling import run_program_in_docker_pypi
e.g.
        run_program_in_docker_pypi(
            folder_with_file=Path(tmp_file_path).parent,
            file_name=py_to_execute,
            timeout=6,
            collect_coverage=True,
            packages=["/usr/local/lib/python3.10/site-packages/qiskit/circuit",
                      "/usr/local/lib/python3.10/site-packages/pennylane"],
            output_folder_coverage=tmp_dir,
        )

The files that are selected in alphabetical order are first copied to a temporary folder.
Then the function run_program_in_docker_pypi is called.


Args:
--input_folder (str): The folder containing the programs to be analyzed
--output_folder (str): The folder where the coverage report will be saved
--packages (str): The list of pypi packages to be analyzed. (default:
    /usr/local/lib/python3.10/site-packages/)
--timeout (int): The timeout for each program in seconds (default: 30)
--number_of_programs (int): The number of programs to be analyzed (default: 10)


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

# Example usage:
# python -m analysis_and_reporting.coverage_computation --input_folder /path/to/input --output_folder /path/to/output --packages package1 package2 --timeout 30 --number_of_programs 10


"""

console = Console()


def select_programs(input_path: Path, number_of_programs: int) -> List[Path]:
    """Select a number of programs alphabetically."""
    return sorted(input_path.glob("*.py"))[:number_of_programs]


def create_tmp_folder(output_path: Path) -> Path:
    """Create a temporary folder in the output folder."""
    tmp_dir = output_path / "tmp_execution"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def compute_coverage(
        input_folder: str, output_folder: str, packages: List[str],
        timeout: int, number_of_programs: int) -> None:
    """Compute the coverage of the generated programs.

    Make sure to copy them to a temporary folder.
    """
    console.log(
        f"Starting coverage computation for {number_of_programs} programs.")
    input_path = Path(input_folder)
    output_path = Path(output_folder) / "coverage_reports"
    output_path.mkdir(parents=True, exist_ok=True)

    programs = select_programs(input_path, number_of_programs)
    console.log(f"Selected {len(programs)} programs for analysis.")

    tmp_dir = create_tmp_folder(output_path)
    console.log(f"Temporary folder created at {tmp_dir}")

    for program in programs:
        tmp_file_path = tmp_dir / program.name
        shutil.copy(program, tmp_file_path)
        py_to_execute = tmp_file_path.name
        base_name = py_to_execute.replace(".py", "")
        output_coverage_file = output_path / f"{base_name}.json"
        # check if the file exists, skip
        if output_coverage_file.exists():
            console.log(
                f"Skipping {py_to_execute} as coverage already exists.")
            continue

        console.log(f"Running {py_to_execute} in Docker container.")
        start_time = time.time()
        run_program_in_docker_pypi(
            folder_with_file=Path(tmp_file_path).parent,
            file_name=py_to_execute,
            timeout=timeout,
            collect_coverage=True,
            packages=packages,
            output_folder_coverage=str(output_path),
        )
        end_time = time.time()
        time_file = output_path / f"{base_name}_time.json"
        time_record = {
            "program": py_to_execute,
            "duration": end_time - start_time,
            "start_time": start_time,
            "end_time": end_time,
        }
        time_file.write_text(json.dumps(time_record, indent=4))
        console.log(
            f"Program {py_to_execute} executed in {end_time - start_time} seconds.")

    console.log(
        f"Coverage computation completed. Reports saved in {output_path}")


@click.command()
@click.option('--input_folder', required=True, type=str,
              help='The folder containing the programs to be analyzed')
@click.option('--output_folder', required=True, type=str,
              help='The folder where the coverage report will be saved')
@click.option('--packages', required=True, type=str, multiple=True,
              help='The list of pypi packages to be analyzed')
@click.option('--timeout', default=30, type=int,
              help='The timeout for each program in seconds')
@click.option('--number_of_programs', default=10, type=int,
              help='The number of programs to be analyzed')
def main(
        input_folder: str, output_folder: str, packages: List[str],
        timeout: int, number_of_programs: int) -> None:
    compute_coverage(
        input_folder=input_folder,
        output_folder=output_folder,
        packages=list(packages),
        timeout=timeout,
        number_of_programs=number_of_programs
    )


if __name__ == '__main__':
    main()
