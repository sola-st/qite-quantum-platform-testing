
import docker
import json
from pathlib import Path
from typing import Tuple, List, Union
import subprocess
import threading
import tempfile
import shutil
from validate.functions_oracle_calls import get_all_qasm_files


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
            result = subprocess.run(
                ["docker", "ps", "-q", "--filter", "ancestor=qiskit_runner",
                 "|", "xargs", "-r", "docker", "stop"],
                capture_output=True, text=True)
            console.log(f"Stopped containers: {result.stdout}")
        else:
            print(f"Execution timed out after {timeout} seconds.")


def get_qasm_files_involved_in_error(output_dir: str) -> List[str]:
    """Get all the qasm files that are involved in the error.

    Error files end in _error.json.
    """
    error_metadata = [
        json.loads(filepath.read_text())
        for filepath in Path(output_dir).glob("*_error.json")]
    qasm_files = []
    for metadata in error_metadata:
        qasm_files.extend(get_all_qasm_files(metadata))
    return qasm_files


def run_program_in_docker_pypi(
        folder_with_file: Path, file_name: str, timeout: int = 60, console=None,
        collect_coverage: bool = False,
        packages: List[str] = ["/usr/local/lib/python3.10/site-packages/qiskit"],
        output_folder_coverage: str = None,
        ignore_every_other_file_in_folder: bool = False,
        copy_back_only_relevant_qasm_files: bool = False) -> None:
    """Runs the generated program in a Docker container with a timeout.

    It uses the pypi docker package to run the program in a container and get
    its container id to stop it if it times out.

    Args:
        - ignore_every_other_file_in_folder: If True, only the file_name file
          is copied to a temporary directory.
        - copy_back_only_relevant_qasm_files: If True, only the qasm files that
          appear in some error logs or are ancestors of those files are copied
          from the docker container to the host. Note that this is only
          used in the case of ignore_every_other_file_in_folder=True.
    """
    client = docker.from_env()
    if ignore_every_other_file_in_folder:
        temp_dir = tempfile.TemporaryDirectory()
        path_temp_dir = Path(temp_dir.name)
        # copy the file to a temporary directory
        shutil.copy(folder_with_file / file_name, path_temp_dir)
        old_folder_with_file = folder_with_file
        folder_with_file = path_temp_dir

    abs_folder = folder_with_file.resolve()
    if collect_coverage:
        assert output_folder_coverage is not None, "The output_folder_coverage for coverage must be provided if collect_coverage is True."
        abs_output_folder_coverage = Path(output_folder_coverage).resolve()
    if isinstance(packages, str):
        packages = [packages]
    container = None
    timer = None

    def stop_container():
        if container:
            container.stop()
            if console:
                console.log(
                    f"Container {container.id} stopped due to timeout.")
            else:
                print(f"Container {container.id} stopped due to timeout.")

    if collect_coverage:
        base_name = file_name.replace(".py", "")
        command = f"python -m slipcover --json --out /workspace/coverage_output/{base_name}.json --source {','.join(packages)} -m {base_name}"
        print(command)
        volumes = {
            str(abs_folder): {'bind': '/workspace', 'mode': 'rw'},
            str(abs_output_folder_coverage): {'bind': '/workspace/coverage_output', 'mode': 'rw'}
        }
    else:
        base_name = file_name.replace(".py", "")
        command = f"python -m {base_name}"
        volumes = {str(abs_folder): {'bind': '/workspace', 'mode': 'rw'}}

    try:
        container = client.containers.run(
            image='qiskit_runner',
            command=command,
            volumes=volumes,
            working_dir='/workspace',
            detach=True
        )
        if console:
            console.log(f"Container {container.id} started.")
        else:
            print(f"Container {container.id} started.")

        timer = threading.Timer(timeout, stop_container)
        timer.start()

        result = container.wait()
        success = result['StatusCode'] == 0
        output = container.logs().decode()

        if success:
            if console:
                console.log(f"Program {file_name} executed successfully.")
                console.print(f"Output: {output}")
            else:
                print(f"Program {file_name} executed successfully.")
                print(f"Output: {output}")
        else:
            if console:
                console.log(f"Failed to execute {file_name} in Docker.")
                console.print(f"Error: {output}", style="bold red")
            else:
                print(f"Failed to execute {file_name} in Docker.")
                print(f"Error: {output}")

    except docker.errors.DockerException as e:
        if console:
            console.log(f"Error running container: {e}", style="bold red")
        else:
            print(f"Error running container: {e}")

    finally:
        if container:
            container.remove(force=True)
        if timer and timer.is_alive():
            timer.cancel()
        if ignore_every_other_file_in_folder:
            error_causing_qasm_files = get_qasm_files_involved_in_error(
                output_dir=str(path_temp_dir))
            # copy all new files to the original folder
            for file in path_temp_dir.iterdir():
                if file.is_file():
                    if copy_back_only_relevant_qasm_files:
                        # keep only files that are:
                        # - error file
                        # - are prefix of any qasm file involved in the error
                        if any(
                            str(qasm_file).startswith(str(Path(file).stem))
                            for qasm_file in error_causing_qasm_files
                        ) or str(file).endswith("_error.json"):
                            shutil.copy(file, old_folder_with_file)
                    else:
                        # copy anything
                        shutil.copy(file, old_folder_with_file)
            # remove the temporary directory
            temp_dir.cleanup()
