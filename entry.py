"""Create a script to execute python modules using a specific yaml config.


An example of config file is the following: v001.yaml
command:
  module: generators.morphq_like_w_oracles
  arguments:
    prompt: generators/morphq_w_oracles.jinja
    output_folder: program_bank
    max_n_qubits: 5
    max_n_gates: 10
    max_n_programs: 1000

This becomes the following command:
python -m generators.morphq_like_w_oracles --prompt generators/morphq_w_oracles.jinja --output_folder program_bank --max_n_qubits 5 --max_n_gates 10 --max_n_programs 1000

This script runs it as follows:
python entry.py --config v001.yaml --screen

If screen is given it will run in a screen and the session log will be stored
at the path logs/v001_{YYYY_MM_DD_HH_MM}.log
The log is initialized with the content of the config file.

In case of screen the command is:
screen -L -Logfile logs/v001_{YYYY_MM_DD_HH_MM}.log -dm python -m generators.morphq_like_w_oracles --prompt generators/morphq_w_oracles.jinja --output_folder program_bank --max_n_qubits 5 --max_n_gates 10 --max_n_programs 1000

Remember to first dump the config file in the yaml format to the log.
Use a proper header to inform the user on the section from the config file
and the rest.

Note that this should also work with flags like --debug, --verbose, --quiet
The config:
command:
  module: generators.morphq_like_w_oracles
  arguments:
    prompt: generators/morphq_w_oracles.jinja
    output_folder: program_bank
    max_n_qubits: 5
    max_n_gates: 10
    max_n_programs: 1000
    debug: True

Becomes the command:
python -m generators.morphq_like_w_oracles --prompt generators/morphq_w_oracles.jinja --output_folder program_bank --max_n_qubits 5 --max_n_gates 10 --max_n_programs 1000 --debug

There might be cases in which we have more that one module to run, in that case
we can have a list of commands in the config file:
commands:
  - module: generators.morphq_like_w_oracles
    arguments:
      prompt: generators/morphq_w_oracles.jinja
      output_folder: program_bank
      max_n_qubits: 5
      max_n_gates: 10
      max_n_programs: 1000
  - module: generators.morphq_like_w_oracles
    arguments:
      prompt: generators/morphq_w_oracles.jinja
      output_folder: program_bank
      max_n_qubits: 5
      max_n_gates: 10
      max_n_programs: 1000
      debug: True

They are executed in order, one after the other.

# Style
- use subfunctions appropriately
- each function has at maximum 7 lines of code of content, break them to smaller functions otherwise
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

"""

from typing import TextIO
import os
import sys
import yaml
import subprocess
import datetime
from pathlib import Path
from typing import Dict, Any, List
import click
from rich.console import Console
from tempfile import NamedTemporaryFile
import signal
from uuid import uuid4


# Add at top of file after imports
current_process = None
console = None


class TeePrinter:
    """Print to multiple outputs."""

    def __init__(self, *files: TextIO):
        self.files = files

    def write(self, data: str) -> None:
        """Write to all files."""
        for f in self.files:
            f.write(data)
            f.flush()

    def flush(self) -> None:
        """Flush all files."""
        for f in self.files:
            f.flush()


def create_dual_console(log_file: Path) -> Console:
    """Create a console that prints to both file and stdout."""
    log_handle = log_file.open('a')
    tee = TeePrinter(sys.stdout, log_handle)
    return Console(
        file=tee,
        color_system=None,
        force_terminal=True
    )


def cleanup_process():
    """Cleanup running process if it exists."""
    global current_process
    if current_process:
        try:
            current_process.terminate()
            # os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        except Exception:
            pass


def fill_and_load_config(config_file: Path) -> Dict[str, Any]:
    """
    Load the YAML configuration file and replace specific placeholders.
    This function reads a YAML configuration file and replaces the following placeholders:
    - <<RUN_FOLDER>>: Replaced with the current date and time in the format '%Y_%m_%d__%H_%M'.
    - <<THIS_FILE_NAME>>: Replaced with the filename of the YAML file without its extension.
    - <<BATCH_SIZE>>: Replaced with the value of the 'batch_size' field in the configuration file.
      If 'batch_size' is not present in the configuration file but the placeholder is present,
      an exception is raised.
    Args:
        config_file (Path): The path to the YAML configuration file.
    Returns:
        Dict[str, Any]: The loaded configuration as a dictionary.
    Raises:
        Exception: If 'batch_size' is not present in the configuration file but the placeholder
                   '<<BATCH_SIZE>>' is present in the file content.
    """
    """Load the YAML configuration file."""
    # replace the keywords:
    # <<RUN_FOLDER>> -> '%Y_%m_%d__%H_%M'
    # <<THIS_FILE_NAME>> -> filename of the yaml file without extension
    # <<BATCH_SIZE>> -> value in the field batch_size (this is useful for
    # continuous mode)

    raw_config = config_file.read_text()
    unique_id = str(uuid4())[:6]
    raw_config = raw_config.replace(
        '<<RUN_FOLDER>>', datetime.datetime.now().strftime('%Y_%m_%d__%H_%M') +
        "_" + unique_id)
    raw_config = raw_config.replace(
        '<<THIS_FILE_NAME>>', config_file.stem)

    try:
        config_dict = yaml.safe_load(raw_config)
        batch_size = int(config_dict['batch_size'])
        raw_config = raw_config.replace(
            '<<BATCH_SIZE>>', str(batch_size))
        raw_config = raw_config.replace(
            '<<HALF_BATCH_SIZE>>', str(batch_size // 2))
    except KeyError:
        raise Exception(
            "Placeholder '<<BATCH_SIZE>>' found but 'batch_size' is not defined in the config file.")

    return yaml.safe_load(raw_config)


def create_log_file(config_file: Path) -> Path:
    """Create the log file path and directory."""
    timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    log_file = Path('logs') / f"{config_file.stem}_{timestamp}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    return log_file


def dump_config_to_log(config: Dict[str, Any], log_file: Path) -> None:
    """Dump the YAML configuration into the log file."""
    with log_file.open('w') as f:
        yaml.dump(config, f)
    global console
    console = create_dual_console(log_file)
    console.print(f"== Config dumped to {log_file} ==")


def build_command(command_config: Dict[str, Any], end_timestamp: int) -> str:
    """Build the Python command from the configuration."""
    module = command_config['module']
    arguments = command_config['arguments']
    config = command_config.get('config', None)
    arguments['end_timestamp'] = end_timestamp

    # Convert the arguments to command line options
    cmd_parts = [f"python -m {module}"]
    for key, value in arguments.items():
        if str(value) in ['True', 'False'] or isinstance(value, bool):
            if str(value) == 'True':
                cmd_parts.append(f"--{key}")
        elif isinstance(value, List):
            for item in value:
                cmd_parts.append(f"--{key} '{item}'")
        else:
            flag = f"--{key}"
            cmd_parts.append(f"{flag} {value}")

    # Handle the config file if present
    if config:
        with NamedTemporaryFile(delete=False, suffix='.yaml') as temp_config_file:
            with open(temp_config_file.name, 'w') as f:
                yaml.dump(config, f)
            temp_config_file_path = temp_config_file.name
        cmd_parts.append(f"--config {temp_config_file_path}")

    return " ".join(cmd_parts)


def run_command(command: str) -> None:
    """Run the command with proper output handling."""
    global current_process
    global console

    try:
        current_process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        for line in current_process.stdout:
            console.print(line, end='')

        current_process.wait()
        if current_process.returncode != 0:
            raise subprocess.CalledProcessError(
                current_process.returncode, command)
    finally:
        cleanup_process()


def replace_program_range(config, program_range: List[int]) -> Dict[str, Any]:
    """Replace the program range in the config."""
    new_config = config.copy()
    new_commands = []
    for command in new_config['commands']:
        new_command = command.copy()
        if 'config' in new_command:
            if 'program_id_range' in new_command['config']:
                new_command['config']['program_id_range'] = program_range
        new_commands.append(new_command)
    new_config['commands'] = new_commands
    return new_config


@click.command()
@click.option('--config', type=click.Path(exists=True),
              required=True, help="Path to the YAML config file.")
@click.option('--continuous_fuzzing', is_flag=True, default=False,
              help="Enable continuous fuzzing mode.")
def main(config: str, continuous_fuzzing: bool) -> None:
    """Main function to execute the command based on the YAML config."""
    global console
    config_file = Path(config)
    config_data = fill_and_load_config(config_file)

    # Log file setup
    log_file = create_log_file(config_file)
    dump_config_to_log(config=config_data, log_file=log_file)

    if continuous_fuzzing:
        console.print("+++ Continuous fuzzing mode enabled. +++")

    batch_size = config_data.get('batch_size')
    budget_time_sec = config_data.get('budget_time_sec', None)
    if budget_time_sec:
        console.print(
            f"*** Budget time set to {budget_time_sec} seconds. ***")

    def timeout_handler(signum, frame):
        """Handle timeout by cleaning up processes."""
        console.print("!!! Timeout expired. Cleaning up... !!!")
        cleanup_process()
        raise TimeoutError

    def signal_handler(signum, frame):
        """Handle interrupt signals."""
        console.print(
            "\n--- Received interrupt signal. Cleaning up... ---")
        cleanup_process()
        raise KeyboardInterrupt

    end_timestamp = -1
    if budget_time_sec:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(budget_time_sec)
        print(f"Setting alarm to {budget_time_sec}")
        c_time = int(datetime.datetime.now().timestamp())
        print(f"Current time: {c_time}")
        end_timestamp = int(c_time + budget_time_sec)
        print(f"End time: {end_timestamp}")

    try:
        batch_number = 0
        while True:
            program_range = [
                batch_number * batch_size,
                (batch_number + 1) * batch_size
            ]
            batch_number += 1
            config_data = replace_program_range(config_data, program_range)
            # Build and run the command
            if 'commands' in config_data:
                for idx, command_config in enumerate(
                        config_data['commands'],
                        start=1):
                    command = build_command(
                        command_config=command_config,
                        end_timestamp=end_timestamp
                    )
                    console.print(
                        f"== Command {idx})\n{command}==")
                    run_command(command=command)
            else:
                command = build_command(command_config=config_data['command'])
                console.print(
                    f"== Command to run:\n{command}==")
                run_command(command=command, end_timestamp=end_timestamp)

            if end_timestamp != -1 and int(
                    datetime.datetime.now().timestamp()) > end_timestamp:
                console.print("Time limit exceeded. Exiting.")
                break

            if not continuous_fuzzing:
                break

    except TimeoutError:
        pass
    finally:
        if budget_time_sec:
            signal.alarm(0)

    # print the name of the folder where the programs are stored as
    # the last line of the log
    print(f"Programs stored in folder:")
    output_folder = None
    for command in config_data['commands']:
        if command['module'] == 'qite.qite_loop':
            output_folder = command['arguments']['input_folder']
            break
    if not output_folder:
        output_folder = config_data['commands'][
            -1]['arguments']['input_folder']
    print(output_folder)


if __name__ == '__main__':
    main()


# Example of usage
# python entry.py --config config/v001.yaml --screen
