

# Mine APIs
The API path is create with the following command:

In file `aiexchange/knowledge_base/test_library.py`, change temp_output_dir to the path where you want to save the entities.json file.
```python
def test_preprocess_extract_entities_success():
    """
    Test that preprocess_extract_entities runs the script in Docker and returns the expected output.
    """
    with tempfile.TemporaryDirectory() as temp_output_dir:
        result = preprocess_extract_entities(
            image_name="qiskit_image_0.45.0",
            directory_to_scan="/usr/local/lib/python3.10/site-packages/qiskit",
            output_dir=temp_output_dir,
        )
        lines = result.splitlines()
        not_empty_lines = [line for line in lines if line.strip()]
        last_line = not_empty_lines[-1]
        assert last_line == "API extraction completed."
        # check that the entities.json file is created
        assert "entities.json" in os.listdir(temp_output_dir)
```


# Mine Migration Doc

The two files:
- `aiexchange/knowledge_base/migration_doc/v001/features_changes.md` from here: https://docs.quantum.ibm.com/migration-guides/qiskit-1.0-features
- `aiexchange/knowledge_base/migration_doc/v001/packaging_changes.md` from here: https://docs.quantum.ibm.com/migration-guides/qiskit-1.0-installation

The last `aiexchange/knowledge_base/migration_doc/v001/1.0_1.1_1.2.md`
is created by using `information_distillation/compact_changelogs.py` on a clone version of the Qiskit repository.