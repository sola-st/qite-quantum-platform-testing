import pytest
from pathlib import Path
from generators.docker_tooling import run_program_in_docker_pypi
import subprocess
import time
import tempfile
import docker


@pytest.fixture
def long_running_file_content():
    return """
import time
time.sleep(15)
"""


@pytest.fixture
def hello_world_file_content():
    return """
import time
time.sleep(3)
print("Hello, World!")
"""


def is_docker_available():
    try:
        client = docker.from_env()
        client.ping()  # Pings the Docker daemon to check availability
        return True
    except docker.errors.DockerException:
        return False


@pytest.mark.skipif(not is_docker_available(),
                    reason="Docker is not available")
def get_running_container_commands():
    """
    Retrieve the commands used to run all currently running Docker containers.
    This function connects to the Docker environment, lists all running containers,
    and extracts the command used to run each container.
    Returns:
        list: A list of commands (as lists of strings) used to run the currently running containers.
    """

    client = docker.from_env()
    containers = client.containers.list()
    commands = []
    for container in containers:
        commands.append(" ".join(container.attrs['Config']['Cmd']))
    return commands


@pytest.mark.skipif(not is_docker_available(),
                    reason="Docker is not available")
def test_hello_world(hello_world_file_content):
    """
    Test that run_program_in_docker_w_timeout successfully runs a simple Python program in a Docker container.

    It creates a dummy Python file that prints "Hello, World!", runs it in a Docker container with a timeout of 6 seconds and then checks that the process was killed.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
        tmp_file.write(hello_world_file_content.encode())
        tmp_file_path = tmp_file.name

    run_program_in_docker_pypi(
        folder_with_file=Path(tmp_file_path).parent,
        file_name=Path(tmp_file_path).name,
        timeout=6
    )

    # check that the container is stopped
    command_list = get_running_container_commands()
    assert not any(Path(
        tmp_file_path).name in cmd for cmd in command_list), "The filename was found in a container command after the timeout."


def test_long_running_file(long_running_file_content):
    """
    Test that run_program_in_docker_w_timeout successfully kills the process when a long running process is run.

    It creates a dummy Python file that sleeps for 15 seconds, runs it in a Docker container with a timeout of 6 seconds and then checks that the process was killed.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
        tmp_file.write(long_running_file_content.encode())
        tmp_file_path = tmp_file.name

    run_program_in_docker_pypi(
        folder_with_file=Path(tmp_file_path).parent,
        file_name=Path(tmp_file_path).name,
        timeout=6
    )

    time.sleep(3)
    # check that the container is stopped
    command_list = get_running_container_commands()
    print(command_list)
    assert not any(Path(
        tmp_file_path).name in cmd for cmd in command_list), "The filename was found in a container command after the timeout."
