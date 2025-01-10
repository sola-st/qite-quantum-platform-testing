import os
import glob
import click

# Global variable specifying the input folders
input_folders = ["1.0", "1.1", "1.2"]


def merge_yaml_files(base_folder, folders):
    merged_content = []
    for folder in sorted(folders):
        folder_path = os.path.join(base_folder, folder)
        yaml_files = sorted(glob.glob(os.path.join(folder_path, "*.yaml")))
        if not yaml_files:
            print(f"No YAML files found in folder: {folder_path}")
            continue
        for yaml_file in yaml_files:
            with open(yaml_file, 'r') as file:
                content = file.read()
                header = f"## Folder: {folder}\n### File: {os.path.basename(yaml_file)}\n"
                merged_content.append(header + content)

    output_file = os.path.join(base_folder, "_".join(sorted(folders)) + ".md")
    with open(output_file, 'w') as file:
        file.write("\n\n".join(merged_content))
    print(f"Merged content written to {output_file}")


@click.command()
@click.option('--base-folder', default=".",
              help='Base folder containing the input folders', required=True)
@click.option('--folders', default="1.0,1.1,1.2",
              help='Comma-separated list of input folders', required=True)
def main(base_folder, folders):
    folder_list = folders.split(',')
    merge_yaml_files(base_folder, folder_list)


if __name__ == "__main__":
    main()

# Example usage:
# python -m information_distillation.compact_changelogs --base-folder data/changelogs/v001/changes/snapshot_changes --folders 1.0,1.1,1.2
