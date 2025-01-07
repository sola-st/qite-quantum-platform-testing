
import time
import json
import click
from pathlib import Path
from typing import List
import shutil
import multiprocessing
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
        timeout: int, number_of_programs: int, process_id: int = 0, console=None) -> None:
    """Compute the coverage of the generated programs.

    Make sure to copy them to a temporary folder.
    """
    if console is None:
        process_id_file = Path(output_folder) / f"process_{process_id}.log"
        f = open(process_id_file, "w")
        console = Console(file=f, force_terminal=True, color_system=None)
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


def create_subfolder_per_process(
        output_path: Path, n_processes: int) -> List[Path]:
    """Create a subfolder for each process."""
    subfolders = [output_path / f"process_{i}" for i in range(n_processes)]
    for subfolder in subfolders:
        subfolder.mkdir(parents=True, exist_ok=True)
    return subfolders


def allocate_programs_to_processes(
        programs: List[Path], n_processes: int) -> List[List[Path]]:
    """Allocate the programs to the processes."""
    programs_per_process = [[] for _ in range(n_processes)]
    for i, program in enumerate(programs):
        programs_per_process[i % n_processes].append(program)
    return programs_per_process


def remove_comparison_oracle(
        target_program: Path,
        line_to_remove: str = "compare_call(a_file, b_file)",
        line_to_replace: str = "pass") -> List[Path]:
    """Replace a specific line in the program with pass.
    The line is given without a starting empty space, however the occurrence
    in the program might start with a certain number of spaces.
    The goal is to replace it with pass, while keeping the same indentation.
    """
    lines = target_program.read_text().split("\n")
    new_lines = []
    for line in lines:
        if line.strip() == line_to_remove:
            new_lines.append(line.replace(line_to_remove, line_to_replace))
        else:
            new_lines.append(line)
    target_program.write_text("\n".join(new_lines))


def copy_programs_to_process_folders(
        programs_per_process: List[List[Path]],
        subfolders: List[Path],
        do_remove_comparison_oracle: bool = True
) -> None:
    """Copy the programs to the subfolders."""
    for i, programs in enumerate(programs_per_process):
        for program in programs:
            tmp_file_path = subfolders[i] / program.name
            shutil.copy(program, tmp_file_path)
            if do_remove_comparison_oracle:
                remove_comparison_oracle(
                    target_program=tmp_file_path,
                    line_to_remove="compare_call(a_file, b_file)",
                    line_to_replace="pass")


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
@click.option('--n_processes', default=1, type=int,
              help='The number of processes to run in parallel')
def main(
        input_folder: str, output_folder: str, packages: List[str],
        timeout: int, number_of_programs: int, n_processes: int) -> None:

    all_programs = [
        program for program in Path(input_folder).glob("*.py")
    ]

    output_path = Path(output_folder)
    subfolders = create_subfolder_per_process(output_path, n_processes)
    programs_per_process = allocate_programs_to_processes(
        programs=all_programs, n_processes=n_processes)
    copy_programs_to_process_folders(
        programs_per_process=programs_per_process, subfolders=subfolders)

    processes = []
    for i, programs in enumerate(programs_per_process):
        process = multiprocessing.Process(
            target=compute_coverage,
            kwargs={
                'input_folder': str(subfolders[i]),
                'output_folder': str(subfolders[i]),
                'packages': list(packages),
                'timeout': timeout,
                'number_of_programs': min(
                    len(programs), number_of_programs // n_processes),
                'process_id': i,
            }
        )
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    # remove all python files in the subfolders
    for subfolder in subfolders:
        for file in subfolder.glob("*.py"):
            file.unlink()


if __name__ == '__main__':
    main()
