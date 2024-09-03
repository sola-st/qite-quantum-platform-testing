LLM knowledge editing to allow for generation of new version of Qiskit code without retraining.


- Get the code hunks and commits of code hunks that include the "deprecate" substring:
```shell
python -m information_distillation.get_code_hunks_with_deprecate --repo_name platform_repos/qiskit --max_commits 100 --output_folder deprecated_apis
```

- Filter the code changes to remove duplicates:
```shell
python -m information_distillation.filter_code_changes --input_path deprecated_apis/qiskit_100.json --output_folder deprecated_apis/
```

- Extract the API name before and after using Groq for each code change:
```shell
python -m  information_distillation.get_api_mapping --input_json deprecated_apis/qiskit_-1_flattened_context_compressed_deprecated_import.json --output_folder deprecated_apis/ --json_schema information_distillation/get_api_mapping.json
```
