import subprocess
import time
from pathlib import Path
from datetime import (
    datetime,
    timedelta
)

TEST_DIR = Path(__file__).parent
ROOT_DIR = TEST_DIR.parent.parent


def wait_for_screen_session(session_name: str, timeout: int = 300) -> bool:
    """Wait for screen session to complete with timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = subprocess.run(
            ['screen', '-ls', session_name],
            capture_output=True,
            text=True
        )
        if session_name not in result.stdout:
            return True  # Session ended
        time.sleep(1)
    return False  # Timeout


def test_basic_execution():
    """Test basic command execution."""
    result = subprocess.run([
        'python',
        ROOT_DIR / 'entry.py',
        '--config',
        TEST_DIR / 'config/only_qasm_gen.yaml'
    ], capture_output=True, text=True)
    assert result.returncode == 0, f'Error: {result.stderr}'


def test_screen_mode():
    """Test screen mode execution."""
    # get time in this format and get also the next minute hh_mm
    # (e.g. 20_43)
    time_now = datetime.now()
    time_now_str = time_now.strftime('%H_%M')
    time_next_minute = time_now + timedelta(minutes=1)
    time_next_minute_str = time_next_minute.strftime('%H_%M')

    result = subprocess.run([
        'screen',
        '-dmS',
        'only_qasm_gen',
        'python',
        str(ROOT_DIR / 'entry.py'),
        '--config',
        str(TEST_DIR / 'config/only_qasm_gen.yaml'),
    ], capture_output=True, text=True)
    assert result.returncode == 0, f'Error: {result.stderr}'
    # check that the screen session was created
    # (the session should be called 'only_qasm_gen)
    result = subprocess.run(
        ['screen', '-ls', 'only_qasm_gen'], capture_output=True, text=True)
    assert 'only_qasm_gen' in result.stdout, 'Screen session was not created'
    # wait until it finishes
    assert wait_for_screen_session('only_qasm_gen', timeout=300), \
        'Screen session did not finish within 300 seconds' \
        ' (when given max 150 seconds)'
    # Check if log file was created
    all_logs = list(Path('logs').glob('*.log'))
    logs_ending_with_time = [
        log
        for log in all_logs
        if (
            log.name.endswith(time_now_str + '.log') or
            log.name.endswith(time_next_minute_str + '.log')
        ) and (log.name.startswith('only_qasm_gen'))
    ]
    assert len(logs_ending_with_time) > 0, 'No log file was created'


def test_interrupted_execution():
    """Test interrupted command execution."""
    process = subprocess.Popen([
        'python',
        ROOT_DIR / 'entry.py',
        '--config',
        TEST_DIR / 'config/exceeding_time_limit.yaml'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    assert process.returncode == 0, f'Error: {stderr}'
    assert 'Time limit exceeded' in stdout, \
        'The run output does not contain "Time limit exceeded"'
    # ensre the last two lines are
    # Programs stored in folder:
    # program_bank/exceeding_time_limit/2025_03_06__20_43
    print(stdout.split('\n')[-5:])
    assert 'Programs stored in folder:' in stdout.split('\n')[-3]
    assert 'program_bank/' in stdout.split('\n')[-2]
