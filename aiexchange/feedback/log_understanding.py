import re
from typing import List


def is_code_fixed(logs: str) -> bool:
    return "traceback" not in logs.lower() and "SyntaxError" not in logs


def extract_filenames_from_traceback(traceback: str) -> List[str]:
    """
    Extracts all filenames from the given traceback string.

    Args:
        traceback (str): The traceback string.

    Returns:
        List[str]: A list of filenames extracted from the traceback.
    """
    pattern = r'File "([^"]+)"'
    matches = re.findall(pattern, traceback)
    files_occurrences = list(set(matches)) if matches else []
    # get from import errors
    import_errors = re.findall(
        r'ImportError: cannot import name \'[^\']+\' from \'[^\']+\' \(([^)]+)\)',
        traceback)
    files_occurrences.extend(import_errors)
    # Remove /workspace/code_sample.py if present
    files_occurrences = [
        file for file in files_occurrences
        if file != "/workspace/code_sample.py"]
    return files_occurrences


def extract_objects_from_traceback(traceback: str) -> List[str]:
    """
    Extracts all object names (functions, classes, variables) from the given traceback string.

    Args:
        traceback (str): The traceback string.

    Returns:
        List[str]: A list of object names extracted from the traceback.
    """
    # NameErrors
    pattern = r'NameError: name \'([^\']+)\' is not defined'
    matches = re.findall(pattern, traceback)
    entities_from_name_errors = list(set(matches)) if matches else []
    # AttributeErrors
    pattern = r"AttributeError: module '[^']+' has no attribute '([^']+)'"
    matches = re.findall(pattern, traceback)
    entities_from_attribute_errors = list(set(matches)) if matches else []
    # AttributeError: type object 'ScheduleBlock' has no attribute 'from_schedule'
    pattern = r"AttributeError: type object '[^']+' has no attribute '([^']+)'"
    matches = re.findall(pattern, traceback)
    entities_from_attribute_errors.extend(
        list(set(matches)) if matches else [])
    # AttributeError: 'Schedule' object has no attribute 'encode'
    pattern = r"AttributeError: '[^']+' object has no attribute '([^']+)'"
    matches = re.findall(pattern, traceback)
    entities_from_attribute_errors.extend(
        list(set(matches)) if matches else [])
    # ImportErrors
    pattern = r"ImportError: cannot import name '([^']+)' from '[^']+'"
    matches = re.findall(pattern, traceback)
    entities_from_import_errors = list(set(matches)) if matches else []
    # TypeErrors
    # TypeError: transpile() got an unexpected keyword argument 'noise_model' -> transpile
    # TypeError: QasmBackendConfiguration.__init__() missing 1 required positional argument: 'coupling_map' -> QasmBackendConfiguration
    pattern = r"TypeError: ([^\(\.]+)[\(\.]"
    matches = re.findall(pattern, traceback)
    entities_from_type_errors = list(set(matches)) if matches else []

    return (
        entities_from_name_errors
        + entities_from_attribute_errors
        + entities_from_import_errors
        + entities_from_type_errors
    )


def extract_missing_modules_from_traceback(traceback: str) -> List[str]:
    """
    Extracts all missing module names from the given traceback string.

    Args:
        traceback (str): The traceback string.

    Returns:
        List[str]: A list of missing module names extracted from the traceback.
    """
    pattern = r"ModuleNotFoundError: No module named '([^']+)'"
    matches = re.findall(pattern, traceback)
    missing_modules = list(set(matches)) if matches else []
    return sorted(missing_modules)
