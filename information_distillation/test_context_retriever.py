import pytest
from information_distillation.context_retriever import get_function_name
from information_distillation.context_retriever import get_list_of_parents
from information_distillation.context_retriever import get_context
from information_distillation.context_retriever import get_context_parents_compressed
from information_distillation.context_retriever import get_parents

file_content = """
def test_function():
    print("Hello, World!")
    return 42

def test_function_2(with_signature: str):
    print("Hello, World!")

    def inner_function(arg1, arg2='default', *args, **kwargs):
        print("inner function")
    return 42

class TestClass(ParentClass):
    def test_method(self):
        print("Hello, World!")
        return 42
"""

eof_context = """
class TestClass(ParentClass):
    def test_method(self):
        print("Hello, World!")
        return 42
"""

inner_function_context = """def test_function_2(with_signature: str):
    ...
    def inner_function(arg1, arg2='default', *args, **kwargs):
        print("inner function")"""


class_method_context_w_lines = """
class TestClass(ParentClass):
    def test_method(self):
        print("Hello, World!")
        return 42
"""


filecontent_advanced_functions = """
def test_function(
        arg1: str,
        arg2: int = 42,
        *args: Any,
        **kwargs: Any
) -> int:
    print("Hello, World!")
    return 42

@deprecate
def deprecated_function():
    print("Hello, World!")
    def inner_function():
        print("inner function")
    return 42
"""


def test_get_function_name():
    assert get_function_name(file_content, 3) == "test_function"


def test_with_signature():
    assert get_function_name(
        file_content, 7, with_signature=True) == "test_function_2(with_signature: str)"


def test_get_parents_function_in_inner_function():
    assert get_list_of_parents(file_content, 9) == [
        {
            "type": "function",
            "name": "def test_function_2(with_signature: str)",
            "lineno": 6,
            "end_lineno": 11,
        },
        {
            "type": "function",
            "name": "def inner_function(arg1, arg2='default', *args, **kwargs)",
            "lineno": 9,
            "end_lineno": 10,
        }]


def test_get_parents_function_in_object_method():
    assert get_list_of_parents(file_content, 15) == [
        {
            "type": "class",
            "name": "class TestClass(ParentClass)",
            "lineno": 13,
            "end_lineno": 16,
        },
        {
            "type": "function",
            "name": "def test_method(self)",
            "lineno": 14,
            "end_lineno": 16,
        }]


def test_get_context():
    assert get_context(file_content, line_number=1,
                       n_context_lines=1) == "\ndef test_function():\n    print(\"Hello, World!\")"


def test_get_context_end_of_file():
    assert get_context(file_content, line_number=15,
                       n_context_lines=4) == eof_context


def test_get_parents_on_function_signature():
    assert get_list_of_parents(
        filecontent_advanced_functions, 3) == [
        {"type": "function",
         "name":
         "def test_function(arg1: str, arg2: int=42, *args: Any, **kwargs: Any) -> int",
         "lineno": 2, "end_lineno": 9, }]


def test_get_parents_on_function_signature_beginning():
    assert get_list_of_parents(
        file_content, 1) == []


def test_get_context_skeleton_top_function_single_line():
    assert get_context_parents_compressed(
        file_content, line_number=1, n_context_lines=0) == "def test_function():"


def test_get_context_skeleton_inner_function_single_line():
    assert get_context_parents_compressed(
        file_content, line_number=9, n_context_lines=0) == inner_function_context


def test_get_context_skeleton_inner_method_3_lines():
    assert get_context_parents_compressed(
        file_content, line_number=14, n_context_lines=3) == class_method_context_w_lines
