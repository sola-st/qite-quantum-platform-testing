"""Script to extract code changes that mention "deprecate".

Given an input repo name, it uses pydriller to iterate over all the code changes
since the beginning and focuses on the changed files.
It creates a data structure that stores for each commit hash, the number of code changes
it introduces which have the "deprecate" substring in it.
Example:
[
    {
        "hash": "f37bd68005a88f82715e7b65326e941ff021406e",
        "commit_number": 13,
        "code_changes": [
            {
                "file": "path/to/file.txt",
                "lines_removed": [
                    "line 1",
                    "line 2",
                ],
                "lines_added": [
                    "new_line"
                ]
            }
        ]
    }
]

Note that it reports all the code changes that have the "deprecate" substring
either in the lines_removed or lines_added.

--repo_name: str, username/project format like in GitHub
    handle both local paths and remote paths (default: platform_repos/qiskit)
--loc_limit: int, max number of lines of codes for which we analyze the modified files,
    we skip everything that exceeds that (default: 3000)
--file_size_limit: int, maximum number in KB for which we analyze the modified file
    (default 1024KB)
--max_commits: int, maximum number of commits to analyze. if -1 it means to analyze
    all of them. (default: 100)
--output_folder: str, where to store the final json file with all the code changes
    the file has the format: {repo_name}_{max_commits}.json



# Implementation
- it uses click v8 library
- it has a simple main
- use tqdm to give a feedback on the number of commits scanned
- make sure, that if the file has at least one line that has the "deprecated"
    then all the lines of that code change are added to the final json.


# Style
- it uses subfunction appropriately
- always use named arguments when calling a function
    (except for standard library functions)
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses os.path every time that it is dealing with path composition
- it uses pathlib every time that paths are checked or created.
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate


# Reference
```python
for commit in Repository('path/to/the/repo').traverse_commits():
    print('Hash {}, author {}'.format(commit.hash, commit.author.name))

urls = ["repos/repo1", "repos/repo2",
        "https://github.com/ishepard/pydriller.git", "repos/repo3",
        "https://github.com/apache/hadoop.git"]
for commit in Repository(path_to_repo=urls).traverse_commits():
    print("Project {}, commit {}, date {}".format(
           commit.project_path, commit.hash, commit.author_date))

for commit in Repository('path/to/the/repo').traverse_commits():
    for file in commit.modified_files:
        print('{} has complexity of {}, and it contains {} methods'.format(
              file.filename, file.complexity, len(file.methods)))
```

```md
ModifiedFile (object in pydriller)
You can get a list of modified files as well as their diffs and current source code from each commit. All Modifications can be obtained by iterating over the ModifiedFile object. Each modification object references a modified file and has the following fields:

old_path: old path of the file (can be _None_ if the file is added)

new_path: new path of the file (can be _None_ if the file is deleted)

filename: return only the filename (e.g., given a path-like-string such as “/Users/dspadini/pydriller/myfile.py” returns “myfile.py”)

change_type: type of the change: can be Added, Deleted, Modified, or Renamed. If you use change_type.name you get ADD, DELETE, MODIFY, RENAME.

diff: diff of the file as Git presents it (e.g., starting with @@ xx,xx @@).

diff_parsed: diff parsed in a dictionary containing the added and deleted lines. The dictionary has 2 keys: “added” and “deleted”, each containing a list of Tuple (int, str) corresponding to (number of line in the file, actual line).

added_lines: number of lines added

deleted_lines: number of lines removed

source_code: source code of the file (can be _None_ if the file is deleted or only renamed)

source_code_before: source code of the file before the change (can be _None_ if the file is added or only renamed)

methods: list of methods of the file. The list might be empty if the programming language is not supported or if the file is not a source code file. These are the methods after the change.

methods_before: list of methods of the file before the change (e.g., before the commit.)

changed_methods: subset of _methods_ containing only the changed methods.

nloc: Lines Of Code (LOC) of the file

complexity: Cyclomatic Complexity of the file

token_count: Number of Tokens of the file
```

"""


import json
import os
import click
from pathlib import Path
from pydriller import Repository
from tqdm import tqdm
from rich.console import Console
from information_distillation.context_retriever import get_context_parents_compressed
from information_distillation.context_retriever import get_context

console = Console()


def print_context(context: str, target_line: str):
    """Print the context with the target line highlighted."""
    if not context:
        return
    console.print("-" * 80)
    for line in context.split("\n"):
        if line == target_line:
            console.print(line, style="bold red")
        else:
            # print in yellow
            console.print(line, style="yellow")


def analyze_commit(commit, loc_limit, file_size_limit, context_size):
    commit_data = {
        "hash": commit.hash,
        "commit_number": commit.committer_date.isoformat(),
        "code_changes": []
    }

    for modified_file in commit.modified_files:
        if modified_file.nloc and modified_file.nloc > loc_limit:
            continue

        if modified_file.source_code and len(
                modified_file.source_code) / 1024 > file_size_limit:
            continue

        all_lines_added = [
            line
            for lineno, line in modified_file.diff_parsed['added']
        ]
        all_lines_removed = [
            line
            for lineno, line in modified_file.diff_parsed['deleted']
        ]

        lines_added_w_deprecate = [
            (lineno, line) for lineno, line in modified_file.diff_parsed
            ['added'] if 'deprecate' in line.lower()]

        for lineno, line in lines_added_w_deprecate:
            context_compressed = None
            if modified_file.filename.endswith('.py'):
                try:
                    context_compressed = get_context_parents_compressed(
                        file_content=modified_file.source_code,
                        line_number=lineno,
                        n_context_lines=context_size,
                        with_signature=True,
                    )
                except Exception as e:
                    console.log(
                        f"Error in getting context for {modified_file.filename} at line {lineno}: {e}")
                    continue

            context_base = get_context(
                file_content=modified_file.source_code,
                line_number=lineno,
                n_context_lines=context_size,
            )
            # print_context(
            #     context=context_compressed, target_line=line)

            commit_data['code_changes'].append({
                "file": modified_file.new_path or modified_file.old_path,
                "lines_removed": all_lines_removed,
                "lines_added": all_lines_added,
                "target_line": lineno,
                "target_line_content": line,
                "context_compressed": context_compressed,
                "context_base": context_base,
                "context_size": context_size,
            })

    return commit_data if commit_data["code_changes"] else None


@ click.command()
@ click.option('--repo_name', default='platform_repos/qiskit',
               help='Repository name in username/project format or local path.')
@ click.option('--loc_limit', default=3000,
               help='Maximum number of lines of code for analyzing modified files.')
@ click.option('--file_size_limit', default=1024,
               help='Maximum file size in KB for analyzing modified files.')
@ click.option('--max_commits', default=100,
               help='Maximum number of commits to analyze. Use -1 to analyze all.')
@ click.option('--output_folder', default='output',
               help='Folder to store the final JSON file.')
@ click.option('--context_size', default=10,
               help='Number of lines to include in the context.')
def main(
        repo_name, loc_limit, file_size_limit, max_commits, output_folder,
        context_size):
    repo_path = repo_name if repo_name.startswith(
        ('http', '/')) else os.path.join(repo_name)
    output_path = os.path.join(
        output_folder, f"{Path(repo_name).name}_{max_commits}.json")

    repo = Repository(path_to_repo=repo_path, order='reverse')

    all_commits = []
    commit_count = 0

    for commit in tqdm(
            repo.traverse_commits(),
            total=max_commits if max_commits > 0 else None):
        if 0 < max_commits <= commit_count:
            break

        commit_data = analyze_commit(
            commit=commit, loc_limit=loc_limit, file_size_limit=file_size_limit,
            context_size=context_size)
        if commit_data:
            all_commits.append(commit_data)
            commit_count += 1

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(all_commits, f, indent=4)

    console.log(
        f"Analysis complete. Results saved in [bold green]{output_path}[/bold green]")


if __name__ == "__main__":
    main()
