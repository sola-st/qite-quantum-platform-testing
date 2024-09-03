"""Filter relevant code changes.

This script gets as input the list of code changes given a path e.g. qiskit_100.json
it has the following structure:

```json
    {
        "hash": "6b6efc7d547e5baef7d906c850e2bc69ed6430fb",
        "commit_number": "2024-08-23T11:04:35+00:00",
        "code_changes": [
            {
                "file": "test/utils/base.py",
                "lines_removed": [],
                "lines_added": [
                    "        # Safe to remove once `FakeBackend` is removed (2.0)",
                    "        warnings.filterwarnings(",
                    "            \"ignore\",  # If \"default\", it floods the CI output",
                    "            category=DeprecationWarning,",
                    "            message=r\".*from_backend using V1 based backend is deprecated as of Aer 0.15*\",",
                    "            module=\"qiskit.providers.fake_provider.fake_backend\",",
                    "        )",
                    ""
                ],
                "target_line": 163,
                "target_line_content": "            message=r\".*from_backend using V1 based backend is deprecated as of Aer 0.15*\",",
                "context_compressed": "class QiskitTestCase(BaseTestCase):\n    ...\n    def setUpClass(cls):\n        ...\n            category=DeprecationWarning,\n            message=r\".*The abstract Provider and ProviderV1 classes are deprecated.*\",\n            module=\"qiskit_aer\",\n        )\n\n        # Safe to remove once `FakeBackend` is removed (2.0)\n        warnings.filterwarnings(\n            \"ignore\",  # If \"default\", it floods the CI output\n            category=DeprecationWarning,\n            message=r\".*from_backend using V1 based backend is deprecated as of Aer 0.15*\",\n            module=\"qiskit.providers.fake_provider.fake_backend\",\n        )\n\n        allow_DeprecationWarning_message = [\n            r\"The property ``qiskit\\.circuit\\.bit\\.Bit\\.(register|index)`` is deprecated.*\",\n        ]\n        for msg in allow_DeprecationWarning_message:\n            warnings.filterwarnings(\"default\", category=DeprecationWarning, message=msg)\n\n    def __init__(self, *args, **kwargs):\n        super().__init__(*args, **kwargs)...",
                "context_base": "            category=DeprecationWarning,\n            message=r\".*The abstract Provider and ProviderV1 classes are deprecated.*\",\n            module=\"qiskit_aer\",\n        )\n\n        # Safe to remove once `FakeBackend` is removed (2.0)\n        warnings.filterwarnings(\n            \"ignore\",  # If \"default\", it floods the CI output\n            category=DeprecationWarning,\n            message=r\".*from_backend using V1 based backend is deprecated as of Aer 0.15*\",\n            module=\"qiskit.providers.fake_provider.fake_backend\",\n        )\n\n        allow_DeprecationWarning_message = [\n            r\"The property ``qiskit\\.circuit\\.bit\\.Bit\\.(register|index)`` is deprecated.*\",\n        ]\n        for msg in allow_DeprecationWarning_message:\n            warnings.filterwarnings(\"default\", category=DeprecationWarning, message=msg)\n\n    def __init__(self, *args, **kwargs):\n        super().__init__(*args, **kwargs)",
                "context_size": 10
            }
        ]
    },
    {
        "hash": "072548ff09cabfa8b9db8297926c5a609adde10b",
        ...
```

It iterates over all the hashes and for each code change in it.
It collects all the code changes into a single list with hash and commit number
and writes it to a file.
Args:
- input_path: str, path to the input json file.
- output_folder: str, path to the output folder.

The output file has the same name but with the _filtered.json suffix
Create a single function.
"""

import json
import click
import re
from typing import List, Dict
from string import punctuation
from rich.console import Console


def flatten_code_changes(input_path: str, output_folder: str) -> str:
    """Flatten the code changes in the input json file.

    Args:
    - input_path: str, path to the input json file.
    - output_folder: str, path to the output folder.

    Returns:
    - output_path: str, path to the output file.

    The output file has the same name but with the _flatten.json suffix.
    """
    with open(input_path, "r") as file:
        data = json.load(file)
    flattened_data = []
    for commit in data:
        hash = commit["hash"]
        commit_number = commit["commit_number"]
        code_changes = commit["code_changes"]
        for code_change in code_changes:
            code_change["hash"] = hash
            code_change["commit_number"] = commit_number
            flattened_data.append(code_change)
    output_path = input_path.replace(".json", "_flattened.json")
    with open(output_path, "w") as file:
        json.dump(flattened_data, file, indent=4)
    return output_path


def remove_duplicates_on_field(
        input_path: str, output_folder: str, field_name: str,
        output_suffix: str = None) -> str:
    """Remove duplicates on the given field of the input json file.

    Args:
    - input_path: str, path to the input json file.
    - output_folder: str, path to the output folder.
    - field_name: str, field to remove duplicates on.
    - output_suffix: str, suffix to add to the output file name.

    Returns:
    - output_path: str, path to the output file.

    The output file has the same name but with the given output_suffix.
    If no output_suffix is given, the suffix is the same name of the field
    but escaped (replacing all the spaces and special characters with _).
    """
    with open(input_path, "r") as file:
        data = json.load(file)
    unique_data = []
    seen = set()
    for item in data:
        field = item[field_name]
        if field not in seen:
            seen.add(field)
            unique_data.append(item)
    if not output_suffix:
        output_suffix = "".join([c
                                 if c not in punctuation else "_"
                                 for c in field_name])
    output_path = input_path.replace(".json", f"_{output_suffix}.json")
    with open(output_path, "w") as file:
        json.dump(unique_data, file, indent=4)
    return output_path


def remove_lines_with_regex(
        input_path: str, output_folder: str, regex: str,
        output_suffix: str) -> str:
    """Remove code changes where the target line matches the given regex.

    Args:
    - input_path: str, path to the input json file.
    - output_folder: str, path to the output folder.
    - regex: str, regex to match the target line.
    - output_suffix: str, suffix to add to the output file name.

    Returns:
    - output_path: str, path to the output file.

    The output file has the same name but with the given output_suffix.
    """
    with open(input_path, "r") as file:
        data = json.load(file)
    filtered_data = []
    for item in data:
        if not re.match(regex, item["target_line_content"]):
            filtered_data.append(item)
    output_path = input_path.replace(".json", f"_{output_suffix}.json")
    with open(output_path, "w") as file:
        json.dump(filtered_data, file, indent=4)
    return output_path


def count_element_json(input_path: str) -> int:
    """Count the number of elements in a json list.

    Args:
    - input_path: str, path to the input json file.

    Returns:
    - count: int, number of elements in the json.
    """
    with open(input_path, "r") as file:
        data = json.load(file)
    return len(data)


def process_data(input_path: str, output_folder: str) -> str:
    """Process the data in the input json file.

    Args:
    - input_path: str, path to the input json file.
    - output_folder: str, path to the output folder.

    The output file has the same name but with the _filtered.json suffix.
    """
    console = Console()
    console.print(f"Processing data in {input_path}...")
    flattened_path = flatten_code_changes(input_path, output_folder)
    n_elems = count_element_json(flattened_path)
    console.print(f"Flattened data has {n_elems} elements.")
    context_path = remove_duplicates_on_field(
        flattened_path, output_folder, "context_compressed")
    n_elems_context = count_element_json(context_path)
    console.print(f"Context-deduplicated data has {n_elems_context} elements.")
    regex_path = remove_lines_with_regex(
        context_path, output_folder,
        regex="from\s+\w+(\.\w+)*\s+import\s+\w*(deprecate|deprecated|deprecation)\w*|import\s+\w+(\.\w+)*\.(deprecate|deprecated|deprecation)\w*",
        output_suffix="deprecated_import")
    n_elems_regex = count_element_json(regex_path)
    console.print(f"Deprecated data has {n_elems_regex} elements.")

    # target_path = remove_duplicates_on_field(
    #     context_path, output_folder, "target_line")
    # n_elems_target = count_element_json(target_path)
    # console.print(f"Target data has {n_elems_target} elements.")
    return regex_path


@click.command()
@click.option("--input_path", required=True, type=str,
              help="Path to the input json file.")
@click.option("--output_folder", required=True, type=str,
              help="Path to the output folder.")
def main(input_path: str, output_folder: str) -> None:
    """Process the data in the input json file."""
    process_data(input_path, output_folder)


if __name__ == "__main__":
    main()
