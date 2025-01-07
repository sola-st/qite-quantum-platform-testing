import os
import json
import requests
import click
from tqdm import tqdm
from pydriller import Repository
from datetime import datetime

# Constants
DEFAULT_REPO_URL = 'https://github.com/Qiskit/qiskit'
DEFAULT_RELEASE_NOTES_DIR = 'releasenotes/notes/'
DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_REPO_DIR = 'qiskit_repo'

# Function to clone the repository


def clone_repo(repo_url, repo_dir):
    if not os.path.exists(repo_dir) or not os.listdir(repo_dir):
        os.system(f'git clone {repo_url} {repo_dir}')

# Function to download release notes


def download_release_notes(repo_dir, release_notes_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for root, _, files in os.walk(os.path.join(repo_dir, release_notes_dir)):
        for file in files:
            version = os.path.basename(root)
            version_dir = os.path.join(output_dir, version)
            os.makedirs(version_dir, exist_ok=True)
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                content = f.read()
            with open(os.path.join(version_dir, file), 'w') as f:
                f.write(content)

# Function to scrape file changes using Pydriller


def scrape_file_changes(repo_dir, output_dir):
    repo = Repository(repo_dir, only_in_branch='main')
    for commit in tqdm(repo.traverse_commits()):
        print(f'Processing commit {commit.hash}')
        n_modified_files = len(commit.modified_files)
        # if n_modified_files > 100:
        #     print(
        #         f'Skipping commit {commit.hash} with {n_modified_files} files')
        #     continue
        for modification in commit.modified_files:
            versions = get_versions_from_commit(commit)
            if not versions:
                # skipp because no release notes found in commit
                continue
            commit_dir = os.path.join(output_dir, commit.hash)
            os.makedirs(commit_dir, exist_ok=True)
            if modification.new_path:
                hunk_dir = os.path.join(
                    commit_dir, modification.new_path.replace('/', '_'))
            else:
                hunk_dir = os.path.join(
                    commit_dir, "DELETED_" + modification.old_path.replace('/', '_'))
            os.makedirs(hunk_dir, exist_ok=True)
            metadata = {
                'commit_id': commit.hash,
                'commit_timestamp': str(commit.committer_date),
                'added_lines': modification.diff_parsed['added'],
                'deleted_lines': modification.diff_parsed['deleted'],
                'filepath': modification.new_path or modification.old_path,
                'qiskit_versions': versions
            }
            with open(os.path.join(hunk_dir, 'metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=4)
            content = modification.source_code if modification.source_code else 'deleted file'
            with open(os.path.join(hunk_dir, 'content.txt'), 'w') as f:
                f.write(content)

# Function to get version from commit message


def get_version_from_file(file_path):
    """example:
    https://github.com/Qiskit/qiskit/blob/main/releasenotes/notes/0.18/add-alignment-management-passes-650b8172e1426a73.yaml
    --> 0.18
    """
    if DEFAULT_RELEASE_NOTES_DIR not in file_path:
        return None
    version = file_path.split(DEFAULT_RELEASE_NOTES_DIR)[1].split('/')[0]
    # check that it has only numbers and dots with regex
    is_valid = all([c.isdigit() or c == '.' for c in version])
    return version if is_valid else None


def get_versions_from_commit(commit) -> list[str]:
    versions = set()
    for modification in commit.modified_files:
        if modification.new_path and (
                DEFAULT_RELEASE_NOTES_DIR in modification.new_path):
            version = get_version_from_file(modification.new_path)
            if version:
                versions.add(version)
        if modification.old_path and (
                DEFAULT_RELEASE_NOTES_DIR in modification.old_path):
            version = get_version_from_file(modification.old_path)
            if version:
                versions.add(version)
    return list(versions)

# Main function


def process_repository(repo_url, release_notes_dir, output_dir, repo_dir):
    clone_repo(repo_url, repo_dir)
    # TIMELINE VIEW: changes over time
    output_dir_timeline_changes = os.path.join(output_dir, 'timeline_changes')
    os.makedirs(output_dir_timeline_changes, exist_ok=True)
    scrape_file_changes(repo_dir, output_dir_timeline_changes)
    # SNAPSHOT VIEW: at the latest time
    output_dir_snapshot_changes = os.path.join(output_dir, 'snapshot_changes')
    os.makedirs(output_dir_snapshot_changes, exist_ok=True)
    download_release_notes(repo_dir, release_notes_dir,
                           output_dir_snapshot_changes)


@click.command()
@click.option('--repo_url', default=DEFAULT_REPO_URL, required=True,
              help='URL of the repository to clone')
@click.option('--release_notes_dir', default=DEFAULT_RELEASE_NOTES_DIR,
              required=True, help='Directory containing release notes')
@click.option('--output_dir', default=DEFAULT_OUTPUT_DIR, required=True,
              help='Directory to save the output')
@click.option('--repo_dir', default=DEFAULT_REPO_DIR, required=True,
              help='Directory to clone the repository into')
def main(repo_url, release_notes_dir, output_dir, repo_dir):
    process_repository(repo_url, release_notes_dir, output_dir, repo_dir)


if __name__ == '__main__':
    main()

# Example usage:
# python -m information_distillation.get_changelogs --repo_url https://github.com/Qiskit/qiskit --release_notes_dir releasenotes/notes/ --output_dir data/changelogs/v001/changes --repo_dir data/changelogs/v001/repo
