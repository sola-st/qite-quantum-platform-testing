
import docker
from pathlib import Path
from typing import Tuple
import subprocess


def _execute_in_docker(
        image_name: str, command: str, input_folder: Path, console=None) -> Tuple[bool, str]:
    """Execute the command inside the Docker container and handle parsing."""
    client = docker.from_env()
    abs_folder = input_folder.resolve()
    try:
        output = client.containers.run(
            image=image_name,
            command=command,
            volumes={str(abs_folder): {'bind': '/workspace', 'mode': 'rw'}},
            working_dir='/workspace'
        )
        if console:
            console.print(f"Output: {output.decode()}")
        else:
            print(f"Output: {output.decode()}")
        return True, output.decode()
    except docker.errors.ContainerError as e:
        if console:
            console.print(f"Error parsing: {e}", style="bold red")
        else:
            print(f"Error parsing: {e}")
        return False, str(e)


def run_program_in_docker(
        folder_with_file: Path, file_name: str, console=None) -> None:
    """Runs the generated Qiskit program in a Docker container."""
    if isinstance(folder_with_file, str):
        folder_with_file = Path(folder_with_file)
    docker_command = f"python /workspace/{file_name}"
    success, output = _execute_in_docker(
        image_name='qiskit_runner',
        command=docker_command,
        input_folder=folder_with_file,
    )
    if success:
        if console:
            console.log(f"Program {file_name} executed successfully.")
        else:
            print(f"Program {file_name} executed successfully.")
    else:
        if console:
            console.log(f"Failed to execute {file_name} in Docker.")
        else:
            print(f"Failed to execute {file_name} in Docker.")


def run_program_in_docker_w_timeout(
        folder_with_file: Path, file_name: str, timeout: int = 60, console=None) -> None:
    """Runs the generated program in a Docker container with a timeout."""
    if isinstance(folder_with_file, str):
        folder_with_file = Path(folder_with_file)
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "-v",
             f"{folder_with_file.resolve()}:/workspace", "qiskit_runner",
             "python", f"/workspace/{file_name}"],
            capture_output=True, text=True, timeout=timeout)
        success = result.returncode == 0
        if not success:
            exception_info = subprocess.CalledProcessError(
                result.returncode, result.args, result.stdout, result.stderr)
            if console:
                console.log(f"Error: {exception_info}")
            else:
                print(f"Error: {exception_info}")
    except subprocess.TimeoutExpired:
        if console:
            console.log(f"Execution timed out after {timeout} seconds.")
        else:
            print(f"Execution timed out after {timeout} seconds.")
