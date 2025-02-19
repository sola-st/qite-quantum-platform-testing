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

import os
import yaml
import subprocess
import datetime
from pathlib import Path
from typing import Dict, Any, List
import click
from rich.console import Console
from tempfile import NamedTemporaryFile
import signal

console = Console()


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
    raw_config = raw_config.replace(
        '<<RUN_FOLDER>>', datetime.datetime.now().strftime('%Y_%m_%d__%H_%M'))
    raw_config = raw_config.replace(
        '<<THIS_FILE_NAME>>', config_file.stem)

    try:
        config_dict = yaml.safe_load(raw_config)
        raw_config = raw_config.replace(
            '<<BATCH_SIZE>>', str(config_dict['batch_size']))
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
    console.print(f"[bold green]Config dumped to {log_file}[/bold green]")


def build_command(command_config: Dict[str, Any]) -> str:
    """Build the Python command from the configuration."""
    module = command_config['module']
    arguments = command_config['arguments']
    config = command_config.get('config', None)

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


def run_command(command: str, use_screen: bool, log_file: Path) -> None:
    """Run the command, optionally inside a screen."""
    if use_screen:
        screen_cmd = (
            f"screen -L -Logfile {log_file} -m {command}"
        )
        console.print(
            f"[bold blue]Command running in screen session.[/bold blue]")
        result = subprocess.run(screen_cmd, shell=True, check=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Command failed with return code {result.returncode}")
    else:
        result = subprocess.run(command, shell=True, check=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Command failed with return code {result.returncode}")
        console.print(f"[bold blue]Command executed.[/bold blue]")


def replace_program_range(config, program_range: List[int]) -> Dict[str, Any]:
    """Replace the program range in the config."""
    new_config = config.copy()
    new_commands = []
    for command in new_config['commands']:
        new_command = command.copy()
        new_command['config']['program_id_range'] = program_range
        new_commands.append(new_command)
    new_config['commands'] = new_commands
    return new_config


@click.command()
@click.option('--config', type=click.Path(exists=True),
              required=True, help="Path to the YAML config file.")
@click.option('--screen', is_flag=True,
              help="Run command in a screen session.")
@click.option('--continuous_fuzzing', is_flag=True, default=False,
              help="Enable continuous fuzzing mode.")
def main(config: str, screen: bool, continuous_fuzzing: bool) -> None:
    """Main function to execute the command based on the YAML config."""
    config_file = Path(config)
    config_data = fill_and_load_config(config_file)

    # Log file setup
    log_file = create_log_file(config_file)
    dump_config_to_log(config=config_data, log_file=log_file)

    if continuous_fuzzing:
        console.print("[bold red]Continuous fuzzing mode enabled.[/bold red]")

    batch_size = config_data.get('batch_size')
    budget_time_sec = config_data.get('budget_time_sec', None)
    if budget_time_sec:
        console.print(
            f"[bold red]Budget time set to {budget_time_sec} seconds.[/bold red]")

    def timeout_handler(signum, frame):
        console.print("[bold red]Timeout expired. Exiting...[/bold red]")
        raise TimeoutError

    if budget_time_sec:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(budget_time_sec)

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
                    command = build_command(command_config=command_config)
                    console.print(
                        f"[bold yellow]Command {idx})\n{command}[/bold yellow]")
                    run_command(command=command, use_screen=screen,
                                log_file=log_file)
            else:
                command = build_command(command_config=config_data['command'])
                console.print(
                    f"[bold yellow]Command to run:\n{command}[/bold yellow]")
                run_command(command=command, use_screen=screen,
                            log_file=log_file)

            if not continuous_fuzzing:
                break

    except TimeoutError:
        pass
    finally:
        if budget_time_sec:
            signal.alarm(0)


if __name__ == '__main__':
    main()


# Example of usage
# python entry.py --config config/v001.yaml --screen
