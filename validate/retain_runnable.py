"""Run the python files in docker and retain those that complete successfully.

It scans the input folder, looks for all the python files, then runs each of
them in docker (using the pypi library - docker 7.1.0) in the image called
qiskit_runner . The file is mounted as volume with path in the container
/workspace/to_execute.py . When the file runs successfully (exit code 0), then
it is stored in the output folder.

--input_folder: str folder with the .py files to execute
--output_folder: str, where to store the newly extracted programs.
--image_name: str, the docker image name to run (default: qiskit_runner_legacy)

# Implementation
- it uses click v8 library
- it has a simple main
- the new file is stored with the same name of the original file
- use docker library as much as possible
- make sure to remove all the containers that are run
- make sure to copy the file to execute in a temp folder with the name to_execute.py
    then mount the temp folder as volume to the docker
- make sure to collect the stdout and stderr of each container run
- print the output of the container run in yellow
- make sure to wait for the exit code before reading the logs of the container


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
"""
import os
import shutil
import tempfile
import docker
import click
from pathlib import Path
from rich.console import Console


# Initialize rich console for logging
console = Console()


def run_file_in_docker(file_path: Path, image_name: str) -> bool:
    """Run a Python file in a Docker container and return True if successful."""
    client = docker.from_env()

    # Create a temporary directory to mount to Docker
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = Path(temp_dir) / "to_execute.py"
        shutil.copy(file_path, temp_file_path)

        try:
            # Run the file in the Docker container
            container = client.containers.run(
                image=image_name,
                volumes={str(temp_dir): {'bind': '/workspace', 'mode': 'rw'}},
                command='python /workspace/to_execute.py',
                detach=True,
                stdout=True,
                stderr=True
            )

            # Wait for the container to finish and capture the exit code
            exit_code = container.wait()['StatusCode']

            # Collect and log the output from the container
            logs = container.logs(stdout=True, stderr=True).decode()
            container.remove()

            # Print logs in yellow
            console.log(
                f"[yellow]Output of {file_path.name}:[/yellow]\n{logs}")

            return exit_code == 0

        except docker.errors.APIError as e:
            console.log(f"[red]Error running {file_path.name}: {e}[/red]")
            return False


def process_files(
        input_folder: str, output_folder: str, image_name: str) -> None:
    """Process Python files in the input folder and save successful ones to the output folder."""
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Iterate over all Python files in the input folder
    for file_path in input_path.glob('*.py'):
        console.log(f"[green]Processing {file_path.name}[/green]")
        if run_file_in_docker(file_path, image_name):
            # Copy successful files to the output folder
            shutil.copy(file_path, output_path / file_path.name)
            console.log(f"[blue]Successfully executed {file_path.name}[/blue]")
        else:
            console.log(f"[red]Failed to execute {file_path.name}[/red]")


@click.command()
@click.option('--input_folder', type=str, required=True,
              help='Folder with the Python files to execute.')
@click.option('--output_folder', type=str,
              help='Folder to store successfully executed Python files.')
@click.option('--image_name', type=str, default='qiskit_runner',
              help='Docker image to use for execution.')
def main(input_folder: str, output_folder: str, image_name: str) -> None:
    """Main function to execute Python files in Docker containers."""
    if not output_folder:
        output_folder = input_folder + '_runnable'
    process_files(
        input_folder=input_folder, output_folder=output_folder,
        image_name=image_name)


if __name__ == '__main__':
    main()
