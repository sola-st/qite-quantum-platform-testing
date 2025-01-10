import pytest
from aiexchange.feedback.log_understanding import extract_objects_from_traceback
from aiexchange.feedback.log_understanding import extract_missing_modules_from_traceback


@pytest.mark.parametrize("traceback, expected", [
    ("NameError: name 'undefined_variable' is not defined", ['undefined_variable']),
    ("AttributeError: module 'some_module' has no attribute 'missing_attribute'", ['missing_attribute']),
    ("ImportError: cannot import name 'missing_function' from 'some_module'", ['missing_function']),
    ("TypeError: some_function() got an unexpected keyword argument 'unexpected_arg'", ['some_function']),
    ("TypeError: QasmBackendConfiguration.__init__() missing 1 required positional argument: 'coupling_map'", ['QasmBackendConfiguration'])
])
def test_extract_objects_from_traceback(traceback, expected):
    """
    Test that extract_objects_from_traceback correctly extracts object names from various errors in traceback.
    """
    assert extract_objects_from_traceback(traceback) == expected


@pytest.mark.parametrize("traceback, expected", [
    ("ModuleNotFoundError: No module named 'nonexistent_module'", ['nonexistent_module']),
    ("ModuleNotFoundError: No module named 'another_missing_module'", ['another_missing_module']),
    ("ModuleNotFoundError: No module named 'module1'\nModuleNotFoundError: No module named 'module2'", ['module1', 'module2']),
    ("Some other error message without module not found", []),
    ("ModuleNotFoundError: No module named 'module_with_numbers123'", ['module_with_numbers123']),
    ("ModuleNotFoundError: No module named 'qiskit.providers.ibmq'", ['qiskit.providers.ibmq'])
])
def test_extract_missing_modules_from_traceback(traceback, expected):
    """
    Test that extract_missing_modules_from_traceback correctly extracts missing module names from various errors in traceback.
    """
    assert extract_missing_modules_from_traceback(traceback) == expected
