import pytest
from generators.source_code_manipulation import get_source_code_imports
import sys
import ast
import os
import importlib
import importlib.util


def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_get_source_code_imports():
    """Test that get_source_code_imports correctly extracts import statements from a file."""
    # Create a temporary file with some import statements
    file_content = """import os
from pathlib import Path

def dummy_function():
    pass
"""
    file_path = "/tmp/temp_test_file.py"
    with open(file_path, "w") as file:
        file.write(file_content)

    module = import_module_from_file("temp_test_module", file_path)

    # Call the function to test
    result = get_source_code_imports(module)

    # Expected result
    expected_result = """import os
from pathlib import Path
"""

    # Assert the result is as expected
    assert result == expected_result

    # Clean up the temporary file
    os.remove(file_path)
