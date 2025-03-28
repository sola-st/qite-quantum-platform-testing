import click
import os
import subprocess
import logging
import shutil
import time
import json


def collect_and_store_xml_files(input_folder: str, output_folder: str) -> str:
    """Function to collect XML files from input folder and store them in numbered subfolders"""
    if not os.path.exists(input_folder):
        print(f"Input folder {input_folder} does not exist")
        return

    # Get all XML files in input folder
    xml_files = [f for f in os.listdir(input_folder) if f.endswith('.xml')]
    if not xml_files:
        print("No XML files found in input folder")
        return

    # Create target folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Find next available subfolder number
    existing_folders = [d for d in os.listdir(output_folder)
                        if os.path.isdir(os.path.join(output_folder, d))]
    next_num = 1
    if existing_folders:
        next_num = max(int(f) for f in existing_folders if f.isdigit()) + 1

    # Create new subfolder
    new_folder = os.path.join(output_folder, f"{next_num:04d}")
    os.makedirs(new_folder)

    # Move all XML files to new subfolder using shutil
    for xml_file in xml_files:
        src = os.path.join(input_folder, xml_file)
        dst = os.path.join(new_folder, xml_file)
        shutil.move(src, dst)

    print(f"Moved {len(xml_files)} XML files to {new_folder}")
    return new_folder


def run_coverage_scripts(input_folder: str, output_folder: str,
                         end_timestamp: int = None) -> None:
    start_time = time.time()

    scripts_dir = os.getenv('FOLDER_WITH_COVERAGE_COLLECTION_SCRIPTS')
    if not scripts_dir:
        print("FOLDER_WITH_COVERAGE_COLLECTION_SCRIPTS environment variable not set")
        return

    if not os.path.isdir(input_folder):
        raise ValueError(
            f"Input folder {input_folder} is not a valid directory")

    collection_scripts = [
        f for f in os.listdir(scripts_dir)
        if f.startswith('collect_') and f.endswith('.sh') and os.path.isfile(
            os.path.join(scripts_dir, f))]

    if not collection_scripts:
        print("No collection scripts found")
        return

    for script in collection_scripts:
        script_path = os.path.join(scripts_dir, script)
        try:
            print(f"Executing {script} with input folder {input_folder}")
            cmd = f"bash {script_path} {input_folder}"
            print(cmd)
            subprocess.run(cmd, shell=True, check=True)
            # subprocess.run([script_path, input_folder], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script}: {e}")

    new_folder_with_cov = collect_and_store_xml_files(
        input_folder, output_folder)

    # copy the last list in _qite_stats.jsonl to the same folder
    stats_file = os.path.join(input_folder, "_qite_stats.jsonl")
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            lines = f.readlines()
        if lines:
            last_line = lines[-1]
            with open(os.path.join(new_folder_with_cov, "_qite_stats.jsonl"), 'a') as f:
                f.write(last_line)

    # Calculate execution time and store in time.json
    execution_time = time.time() - start_time
    time_data = {"coverage_computation_time": execution_time}
    with open(os.path.join(new_folder_with_cov, "time.json"), 'w') as f:
        json.dump(time_data, f)

    # run this script asynchronously without caring about the output
    # python -m qite.compute_coverage --folder_path /path/to/coverage/files
    cmd = f"python -m qite.compute_coverage --folder_path {new_folder_with_cov}"
    subprocess.Popen(cmd, shell=True)


@click.command()
@click.option('--input_folder', required=True, help='Input folder path')
@click.option('--output_folder', required=True,
              help='Output folder for collected XML files')
@click.option('--end_timestamp', type=int, default=None, help='End timestamp')
def cli(input_folder: str, output_folder: str, end_timestamp: int = None) -> None:
    # check file .timeout in the input folder
    if os.path.exists(os.path.join(input_folder, ".timeout")):
        print("Timeout file found, exiting.")
        return

    run_coverage_scripts(input_folder, output_folder, end_timestamp)

    if end_timestamp and time.time() > end_timestamp:
        print("Current time exceeds end timestamp, exiting.")
        # store .timeout file in the input folder
        with open(os.path.join(input_folder, ".timeout"), 'w') as f:
            f.write(f"Time limit exceeded: {time.time()} > {end_timestamp}")
        return


if __name__ == '__main__':
    cli()
