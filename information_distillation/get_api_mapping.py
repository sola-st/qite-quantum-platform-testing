"""Given the code changes with "deprecate" it asks the LLM to find the API before and after.

The code changes are already given as computed by a previous step.
The script scans all the code changes in the input JSON file and creates another
version of the same file in the output folder.
The new version has some a new field which is a list of code mapping objects of the form:
- deprecated_entity: str, entity that is removed
- deprecated_entity_type: str, either class, method, function, argument, parameter, or other
- deprecated_fully_qualified_name: str, the fully qualified name of the entity
    removed
- replacement_entity: str, entity that is added (if any, None otherwise)
- replacement_entity_type: str, either class, method, function, argument, parameter, or other
    (if any, None otherwise)
- replacement_fully_qualified_name: str, the fully qualified name of the entity
    that is added (if any, None otherwise)
- line_with_deprecate: str, the line containing the "deprecate" substring


The input file has the following format:
[
    {
        "hash": "f37bd68005a88f82715e7b65326e941ff021406e",
        "commit_number": 13,
        "code_changes": [
            {
                "file": "path/to/file.txt",
                "lines_removed": [
                    "line 1",
                    ...
                    "content and deprecate",
                    "line n",
                ],
                "lines_added": [
                    "new_line"
                ]
            }
        ]
    },
    ...
]

The output file has the following format:
[
    {
        "hash": "f37bd68005a88f82715e7b65326e941ff021406e",
        "commit_number": 13,
        "code_changes": [
            {
                "file": "path/to/file.txt",
                "code_mappings: [
                    {
                        "deprecated_entity": "OldClass",
                        "deprecated_entity_type": "class",
                        "deprecated_fully_qualified_name": "com.example.oldpackage.OldClass",
                        "replacement_entity": "NewClass",
                        "replacement_entity_type": "class",
                        "replacement_fully_qualified_name": "com.example.newpackage.NewClass",
                        "line_with_deprecate": "content and deprecate",
                        "deprecated_since_version": "0.46.0",
                        "removed_in_version": "0.50.0",
                    },
                    ...
                ]
            }
        ]
    },
    ...
]
Note that one file might have more than one mapping.
The strategy to get all the mapping consists in iterating over all the lines
that contain "deprecate" (namely the line contain the substring "deprecate"),
then for each of them, the script prompts the LLM.
The approach extracts the context, at maximum 7 lines above and 7 lines below
the line that contains the "deprecate" substring.
If less than 7 lines are available, those are considered.
The context and the json schema (in string form) are included in the prompt given to the LLM.
Also the file path is included in the prompt.
The output from the LLM must be constrained to a json structure using jsonformer.
If the fields cannot be determined reliably, return None in all the fields where
the certainty is lower than 90%.


--input_json: str, path to the json file with code changes
--model_name: str, huggingface name (default: unsloth/Meta-Llama-3.1-8B-bnb-4bit)
--output_folder: str, path to where to store the file (default: deprecated_apis)
--json_schema: str, path to the json schema to condition the output (default: information_distillation/get_api_mapping.json")

# Implementation
- it uses click v8 library (make all the argument options required with default values)
- make sure to run the model on the cuda gpu
- use temperature 0.01 to query the LLM
- it has a simple main
- the new output json has the name of the original file but the suffix "_mapping.json"
    and it is stored in the output folder
- use a json schema to define the new data format we expect as output: it is a list
    of objects like the one described above as code mapping
- make sure to have a subfunction to extract the context around the "deprecate" lines
- use the following json schema to condition the jsonformer output
- the max tokens allowed in the output are 1024.
- parse the output of the llm using a try except block to robustly account for any
    llm output that does not precisely conform to the json schema, if any
- make sure to use jsonformer to query the LLM, there is no need to use generate()
    api, pass the prompt directly to the jsonformer constructor as in the example

# Debug Features
- the llm prompt is printed to the console before running the LLM (use yellow color)
- the llm output is printed to the console
- the parsed json output is printed to the console


# Style
- it uses subfunction appropriately
- always use named arguments when calling a function
    (except for standard library functions)
- when the program has at least a for loop print the indices of the most
    external one: e.g., 1/50 with the total after the slash
- keep the style consistent to pep8 (max 80 char)
- to print the logs it uses the console from Rich library
- always import all the required libraries
- make sure to have docstring for each subfunction and keep it brief to the point
(also avoid comments on top of the functions)
- it uses pathlib to deal with path composition and the creation of new folders
- use type annotations with typing List, Dict, Any, Tuple, Optional as appropriate

# Reference API

````python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "unsloth/Meta-Llama-3.1-8B-bnb-4bit"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

messages = [
    {"role": "system", "content": "You are ..."},
    {"role": "user", "content": "Question to the LLM ... "},
]

input_prompt = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
).to(model.device)

```

```python
from jsonformer import Jsonformer
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("databricks/dolly-v2-12b")
tokenizer = AutoTokenizer.from_pretrained("databricks/dolly-v2-12b")

json_schema = { ... }

prompt = "Generate a person's information based on the following schema:"
jsonformer = Jsonformer(model, tokenizer, json_schema, prompt)
generated_data = jsonformer()

print(generated_data)
```
"""
import click
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from transformers import AutoTokenizer, AutoModelForCausalLM
from jsonformer import Jsonformer
import torch
from tqdm import tqdm
from utils.endpoint_groq import call_groq_api_json
from groq import Groq
from jinja2 import Template
from copy import deepcopy

# Initialize the console for logging
console = Console()


def load_json(file_path: str) -> Any:
    with open(file_path, 'r') as file:
        return json.load(file)


def save_json(data: Any, file_path: str) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def extract_context(
        lines: List[str],
        index: int, context_size: int = 7) -> List[str]:
    start = max(0, index - context_size)
    end = min(len(lines), index + context_size + 1)
    return lines[start:end]


def create_prompt(
        file_path: str, context: List[str],
        target_line: str, json_schema: str) -> str:
    context_text = '\n'.join(context)
    prompt = (
        f"Given the following code context and the JSON schema, identify the deprecated and replacement entities. "
        f"File path: {file_path}\n\n"
        f"Context:\n{context_text}\n\n"
        f"JSON Schema:\n{json_schema}\n\n"
        f"Target Line:\n{target_line}\n\n"
        f"Response format should follow the JSON schema. If more than one mapping is present, return only the first. For the version use the semantic version only e.g. \"0.46.0\", and if not specified put \"None\". Your mapping should refer only to the \"deprecate\" in the target line.\n")
    return prompt


def process_deprecation(lines: List[str],
                        line_index: int, file_path: str,
                        model: AutoModelForCausalLM, tokenizer: AutoTokenizer,
                        json_schema: Dict[str, Any],
                        groq_client: Groq
                        ) -> Optional[Dict
                                      [str, Any]]:
    context = extract_context(lines, line_index)
    target_line = lines[line_index]
    prompt = create_prompt(file_path, context, target_line, json_schema)
    console.print(f"Prompt:\n{prompt}", style="yellow")

    # breakpoint()

    # JSONFORMER
    # messages = [
    #     {"role": "system", "content": "You are a json formatter."},
    #     {"role": "user", "content": f"Given this LLM output make it in json format: {generated_output_groq}"},
    # ]

    # input_prompt = tokenizer.apply_chat_template(
    #     messages,
    #     add_generation_prompt=True,
    #     tokenize=False,
    # )
    # jsonformer = Jsonformer(model, tokenizer, json_schema, input_prompt)
    # generated_data = jsonformer()
    # console.print(f"Parsed JSON Output:\n{generated_data}")
    # return generated_data
    # breakpoint()

    try:
        # GROQ
        generated_output_groq = call_groq_api_json(
            client=groq_client,
            prompt=prompt,
            model_name="llama-3.1-8b-instant",
        )
        console.print(generated_output_groq)
        time.sleep(2)
        return generated_output_groq
    except Exception as e:
        console.print(f"Error parsing JSON output: {e}", style="red")
        return None


def main(
    input_json: str,
    model_name: str,
    output_folder: str,
    json_schema: str,
    groq_token_path: str
) -> None:
    # Load model and tokenizer
    # tokenizer = AutoTokenizer.from_pretrained(
    #     "meta-llama/Meta-Llama-3.1-8B-Instruct")
    # model = AutoModelForCausalLM.from_pretrained(
    #     model_name,
    #     torch_dtype=torch.bfloat16,
    #     device_map="auto"
    # )
    model, tokenizer = None, None

    # Initialize Groq client
    with open(groq_token_path, 'r') as file:
        api_key = file.read().strip()
    groq_client = Groq(api_key=api_key)

    # Load input JSON
    data = load_json(input_json)
    # data = data[:10]
    # import random
    # random = random.Random(42)
    # random.shuffle(data)

    # Create output folder if it does not exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Load JSON schema
    json_schema = load_json(json_schema)

    # import jinja2 template get_api_mapping.jinja
    # path in the same folder of this file
    jinja_path = os.path.join(
        os.path.dirname(__file__), 'get_api_mapping.jinja')
    with open(jinja_path, 'r') as file:
        template = Template(file.read())

    code_mappings = []
    failed_code_changes = []

    # Process each code_change
    for i, change in tqdm(enumerate(data)):
        console.print(f"Processing code_change {i + 1}/{len(data)}")

        file_path = change['file']
        context_compressed = change['context_compressed']
        target_line = change['target_line_content']

        prompt = template.render(
            FILE_PATH=file_path,
            CONTEXT_COMPRESSED=context_compressed,
            JSON_SCHEMA=json_schema,
            TARGET_LINE=target_line
        )
        console.print(f"Prompt:\n{prompt}", style="yellow")

        try:
            # GROQ
            generated_output_groq = call_groq_api_json(
                client=groq_client,
                prompt=prompt,
                # model_name="llama-3.1-70b-versatile",
                model_name="llama-3.1-8b-instant",
            )
            # parse the output
            llm_json_output = json.loads(generated_output_groq)
            console.print(generated_output_groq, style="green")
            time.sleep(2)
        except Exception as e:
            console.print(f"Error parsing JSON output: {e}", style="red")
            failed_code_changes.append(change)
            continue

        # join the change and the llm output dicts
        single_dict = {
            **change,
            **llm_json_output
        }
        # drop lines_added and lines_removed (because too big)
        single_dict.pop('lines_added', None)
        single_dict.pop('lines_removed', None)
        code_mappings.append(single_dict)

    #     for line_index, line in enumerate(lines_added):
    #         if 'deprecate' in line:
    #             mapping = process_deprecation(
    #                 lines_added, line_index, file_path, model, tokenizer,
    #                 schema, groq_client)
    #             if mapping:
    #                 code_mappings.append(mapping)

    #     if code_mappings:
    #         output_commit['code_changes'].append({
    #             "file": file_path,
    #             "code_mappings": code_mappings
    #         })

    #     all_commits.append(
    #         output_commit
    #     )

    console.print(f"Processed {len(data)} code changes.")
    console.print(f"Resulting in {len(code_mappings)} code mappings.")
    output_file = Path(
        output_folder) / f"{Path(input_json).stem}_mapping.json"
    save_json(code_mappings, output_file)
    console.print(f"Output saved to {output_file}")

    if failed_code_changes:
        # store them to anotehr file with _failed suffix
        output_file_failed = Path(
            output_folder) / f"{Path(input_json).stem}_mapping_failed.json"
        save_json(failed_code_changes, output_file_failed)
        console.print(f"Failed code changes saved to {output_file_failed}")


@click.command()
@click.option('--input_json', type=click.Path(exists=True),
              required=True,
              help='Path to the input JSON file with code changes.')
@click.option('--model_name', default='unsloth/Meta-Llama-3.1-8B-bnb-4bit',
              show_default=True, help='Huggingface model name.')
@click.option('--output_folder', default='deprecated_apis', show_default=True,
              help='Folder to save the output JSON files.')
@click.option('--json_schema', type=click.Path(exists=True),
              default='information_distillation/get_api_mapping.json',
              show_default=True, help='Path to the JSON schema.')
@click.option('--groq_token_path', type=str, default='groq_token.txt',
              help='Path to the file containing the Groq API token.')
def run(
        input_json: str, model_name: str, output_folder: str, json_schema: str,
        groq_token_path: str) -> None:
    main(input_json=input_json, model_name=model_name,
         output_folder=output_folder, json_schema=json_schema,
         groq_token_path=groq_token_path)


if __name__ == "__main__":
    run()
