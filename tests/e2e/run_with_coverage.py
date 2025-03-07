import subprocess
import pytest
from pathlib import Path


TEST_DIR = Path(__file__).parent
ROOT_DIR = TEST_DIR.parent.parent


def test_basic_execution():
    """Test basic command execution with run_qite_in_docker.sh"""
    result = subprocess.run([
        'bash',
        ROOT_DIR / 'docker/coverage_toolkit/run_qite_in_docker.sh',
        '-c',
        'tests/e2e/config/coverage_qasm.yaml'
    ], capture_output=True, text=True)

    assert 'Programs stored in folder:' in result.stdout, \
        'Expected output message not found'
    # get the second last line of the output, which has a path
    # to the program bank
    lines = result.stdout.split('\n')
    folder_line_idx = [i for i, line in enumerate(
        lines) if 'Programs stored in folder:' in line][-1]
    program_bank_path = lines[folder_line_idx + 1].strip()
    # check that there is at least one file with ".coverage" name
    coverage_files = list(Path(program_bank_path).glob('.coverage*'))
    assert len(coverage_files) > 0, 'No coverage files found in program bank'
    # check that it contains three xml files called coverage.xml, rust_coverage.xml and cpp_coverage.xml
    xml_files = list(Path(program_bank_path).glob('*.xml'))
    assert set([file.name for file in xml_files]) == {
        'coverage.xml', 'rust_coverage.xml', 'cpp_coverage.xml'}, \
        'Expected xml files not found in program bank' \
        ' (coverage.xml, rust_coverage.xml, cpp_coverage.xml)'
    # check that the coverage.xml file is not empty
    assert xml_files[0].stat().st_size > 0, 'coverage.xml is empty'


def test_interrupted_execution():
    """Test interrupted command execution with run_qite_in_docker.sh"""
    process = subprocess.Popen([
        'bash',
        ROOT_DIR / 'docker/coverage_toolkit/run_qite_in_docker.sh',
        '-c',
        'tests/e2e/config/exceeding_time_limit.yaml'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout, stderr = process.communicate()
    assert process.returncode == 0, f'Error: {stderr}'
    assert 'Time limit exceeded' in stdout, \
        'The run output does not contain "Time limit exceeded"'
