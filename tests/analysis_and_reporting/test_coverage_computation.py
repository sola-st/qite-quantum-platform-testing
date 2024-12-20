import pytest
from click.testing import CliRunner
from analysis_and_reporting.coverage_computation import main
from pathlib import Path
import shutil
import docker


def is_docker_available():
    try:
        client = docker.from_env()
        client.ping()  # Pings the Docker daemon to check availability
        return True
    except docker.errors.DockerException:
        return False


def is_image_available(image_name):
    client = docker.from_env()
    try:
        client.images.get(image_name)
        return True
    except docker.errors.ImageNotFound:
        return False


@pytest.fixture
def setup_test_environment(tmp_path):
    """Setup a temporary test environment."""
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    # Create a sample Python file in the input folder
    sample_file = input_folder / "import_qiskit.py"
    sample_file.write_text("import qiskit\nprint(qiskit.__version__)\n")
    return input_folder, output_folder


@pytest.mark.skipif(not is_docker_available(),
                    reason="Docker is not available")
@pytest.mark.skipif(not is_image_available("qiskit_runner"),
                    reason="qiskit_runner image is not available")
def test_main_creates_coverage_report(setup_test_environment):
    """Test that main creates a coverage report in the output folder."""
    input_folder, output_folder = setup_test_environment
    runner = CliRunner()
    result = runner.invoke(main, [
        '--input_folder', str(input_folder),
        '--output_folder', str(output_folder),
        '--packages', '/usr/local/lib/python3.10/site-packages/qiskit/circuit',
        '--timeout', '30',
        '--number_of_programs', '1'
    ])
    assert result.exit_code == 0
    coverage_report = output_folder / "process_0" / "coverage_reports" / "import_qiskit.json"
    assert coverage_report.exists()
    time_report = output_folder / "process_0" / "coverage_reports" / "import_qiskit_time.json"
    assert time_report.exists()
