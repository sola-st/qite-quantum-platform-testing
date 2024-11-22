import pytest
import os
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


@pytest.fixture
def qiskit_file_content():
    return """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
print(qc)
"""


@pytest.fixture
def multiple_sources():
    return """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
print(qc)
import pennylane as qml
# we indicate the name of the registers and their number of qubits.
wires = qml.registers({"x": 4, "y":4, "output":6,"work_wires": 4})
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


@pytest.mark.skipif(not is_docker_available(),
                    reason="Docker is not available")
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


@pytest.mark.skipif(not is_docker_available(),
                    reason="Docker is not available")
def test_qiskit_with_coverage(qiskit_file_content):
    """
    Test that run_program_in_docker_w_timeout successfully runs a Qiskit program in a Docker container and collects coverage.

    It creates a dummy Python file that imports Qiskit, runs it in a Docker container with a timeout of 6 seconds and collects coverage.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file_path = Path(tmp_dir) / "qiskit_file.py"
        with open(tmp_file_path, 'w') as tmp_file:
            tmp_file.write(qiskit_file_content)
            tmp_file.flush()

        # print all files in the output folder
        print("FOLDER CONTENT")
        print(os.listdir(tmp_dir))

        py_to_execute = Path(tmp_file_path).name
        base_name = py_to_execute.replace(".py", "")
        print(f"file name to execute: {py_to_execute}")
        expected_json_report = Path(tmp_dir) / f"{base_name}.json"
        run_program_in_docker_pypi(
            folder_with_file=Path(tmp_file_path).parent,
            file_name=py_to_execute,
            timeout=6,
            collect_coverage=True,
            packages="/usr/local/lib/python3.10/site-packages/qiskit/circuit",
            output_folder_coverage=tmp_dir,
        )
        # print all files in the output folder
        print([f for f in Path(tmp_dir).iterdir()])
        # check that it produced the coverage report
        assert expected_json_report.exists(), "The coverage report was not generated."

        # print its content
        with open(expected_json_report, 'r') as f:
            print(f.read())

    time.sleep(3)
    # check that the container is stopped
    command_list = get_running_container_commands()
    assert not any(Path(
        tmp_file_path).name in cmd for cmd in command_list), "The filename was found in a container command after the timeout."


@pytest.mark.skipif(not is_docker_available(),
                    reason="Docker is not available")
def test_coverage_report_with_multiple_sources(multiple_sources):
    """
    Test that the coverage report is correctly generated when multiple sources are used.

    It creates a dummy Python file that imports Qiskit and PennyLane, runs it in a Docker container with a timeout of 6 seconds and collects coverage.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file_path = Path(tmp_dir) / "multiple_sources.py"
        with open(tmp_file_path, 'w') as tmp_file:
            tmp_file.write(multiple_sources)
            tmp_file.flush()

        py_to_execute = Path(tmp_file_path).name
        base_name = py_to_execute.replace(".py", "")
        expected_json_report = Path(tmp_dir) / f"{base_name}.json"
        run_program_in_docker_pypi(
            folder_with_file=Path(tmp_file_path).parent,
            file_name=py_to_execute,
            timeout=6,
            collect_coverage=True,
            packages=["/usr/local/lib/python3.10/site-packages/qiskit/circuit",
                      "/usr/local/lib/python3.10/site-packages/pennylane"],
            output_folder_coverage=tmp_dir,
        )

        # check that it produced the coverage report
        assert expected_json_report.exists(), "The coverage report was not generated."

        content = expected_json_report.read_text()
        # check that the content contains the sources
        assert "qiskit/circuit" in content, "The coverage report does not contain the Qiskit source."
        assert "pennylane" in content, "The coverage report does not contain the PennyLane source."
        # print its content
        print(content)
