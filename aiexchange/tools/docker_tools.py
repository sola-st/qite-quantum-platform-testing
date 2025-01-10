import tempfile
import docker
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from aiexchange.feedback.model_understanding import remove_backticks_lines


def get_file_content_in_docker(
        image_name: str, file_path: str) -> Optional[str]:
    """
    Run a Docker container with the specified image and retrieve the content of a specific file.

    Args:
        image_name (str): The name of the Docker image to run.
        file_path (str): The path of the file inside the Docker container to retrieve.

    Returns:
        Optional[str]: The content of the specified file, or None if the file does not exist.
    """
    client = docker.from_env()

    try:
        container = client.containers.run(
            image_name,
            f"cat {file_path}",
            detach=True,
        )
        container.wait()
        logs = container.logs().decode('utf-8')
        if f"cat: {file_path}: No such file or directory" in logs:
            return None
        return logs
    except Exception as e:
        return str(e)
    finally:
        container.remove()


def get_grep_output_in_docker(
        image_name: str, pattern: str, context_size: int = 10,
        file_dir: str = "/usr/local/lib/python3.10/site-packages/qiskit",
        regex_enabled: bool = False,
        compress: bool = False) -> Optional[str]:
    client = docker.from_env()

    folder_name = file_dir.split("/")[-1]

    try:
        regex_flag = ""
        if regex_enabled:
            regex_flag = "-E"
        grep_command = f'grep -r -C {context_size} {regex_flag} "{pattern}" {file_dir}'
        container = client.containers.run(
            image_name,
            grep_command,
            detach=True,
        )
        container.wait()
        logs = container.logs().decode('utf-8')
        if compress:
            logs = logs.replace(file_dir, folder_name)
        return logs
    except Exception as e:
        return str(e)
    finally:
        container.remove()


def run_qiskit_code_in_docker(code: str, image_name: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as code_file:
        code_file.write(remove_backticks_lines(code).encode())
        code_file_path = code_file.name

    client = docker.from_env()

    try:
        container = client.containers.run(
            image_name,
            f"python /workspace/code_sample.py",
            volumes={code_file_path: {'bind': '/workspace/code_sample.py', 'mode': 'rw'}},
            detach=True
        )
        container.wait()
        logs = container.logs().decode('utf-8')
        return logs
    except Exception as e:
        return str(e)
    finally:
        container.remove()
        code_file.close()


def run_script_in_docker(
        script_path: str, image_name: str, options: Dict[str, str] = dict({}),
        output_dir: Optional[str] = None,
        console=None) -> str:
    """
    Resolve the script_path and mount it in the Docker container at
    /workspace/arbitrary_script.py.
    """
    client = docker.from_env()
    abs_script_path = Path(script_path).resolve()
    abs_output_dir = Path(output_dir).resolve() if output_dir else None
    # convert the arguments to a string
    options_str = " ".join(
        [f"--{key} {value}" for key, value in options.items()])

    volumes = {abs_script_path: {
        'bind': '/workspace/arbitrary_script.py', 'mode': 'ro'}}
    if abs_output_dir:
        # if it is a file, we need to mount the parent folder
        if "." in abs_output_dir.name:
            output_path_folder = str(abs_output_dir.parent)
        else:
            output_path_folder = str(abs_output_dir)
        volumes[output_path_folder] = {
            'bind': "/workspace/output_folder", 'mode': 'rw'}
    container = None
    try:
        container = client.containers.run(
            image_name,
            f"python /workspace/arbitrary_script.py {options_str}",
            detach=True,
            volumes=volumes,
        )
        container.wait()
        logs = container.logs().decode('utf-8')
        return logs
    except Exception as e:
        return str(e)
    finally:
        if container:
            container.remove()
