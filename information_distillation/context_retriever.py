"""Script to retrieve the context of given line of code in a file."""

import ast
from typing import List, Dict


def get_function_signature(node):
    if not isinstance(node, ast.FunctionDef):
        raise TypeError("Node is not a FunctionDef")
    # Function name
    name = node.name
    # Arguments
    args = []
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)
    # Default values for arguments
    defaults = [None] * (len(args) - len(node.args.defaults)
                         ) + [ast.unparse(d) for d in node.args.defaults]
    # Combine arguments and defaults
    args_with_defaults = []
    for arg, default in zip(args, defaults):
        if default:
            args_with_defaults.append(f"{arg}={default}")
        else:
            args_with_defaults.append(arg)
    # Varargs and kwargs
    if node.args.vararg:
        vararg_str = f"*{node.args.vararg.arg}"
        if node.args.vararg.annotation:
            vararg_str += f": {ast.unparse(node.args.vararg.annotation)}"
        args_with_defaults.append(vararg_str)
    if node.args.kwarg:
        kwarg_str = f"**{node.args.kwarg.arg}"
        if node.args.kwarg.annotation:
            kwarg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
        args_with_defaults.append(kwarg_str)
    # Return type annotation
    if node.returns:
        return_annotation = f" -> {ast.unparse(node.returns)}"
    else:
        return_annotation = ""
    # Format the signature
    signature = f"{name}({', '.join(args_with_defaults)}){return_annotation}"
    return signature


def get_parent_classes(node):
    if not isinstance(node, ast.ClassDef):
        raise TypeError("Node is not a ClassDef")
    parent_classes = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            parent_classes.append(base.id)
        elif isinstance(base, ast.Attribute):
            parent_classes.append(f"{base.value.id}.{base.attr}")

    return parent_classes


def get_function_name(file_content: str, line_number: int,
                      with_signature: bool = False) -> str:
    """Get the function name of the given line number."""
    tree = ast.parse(file_content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.lineno <= line_number <= node.end_lineno:
                if with_signature:
                    return get_function_signature(node)
                return node.name
    return None


def get_context(
        file_content: str, line_number: int, n_context_lines: int = 5) -> str:
    """Get the context of the given line number."""
    lines = file_content.split("\n")
    start_line = max(0, line_number - n_context_lines)
    end_line = min(len(lines), line_number + n_context_lines + 1)
    context = lines[start_line:end_line]
    return "\n".join(context)


def get_parents(
        file_content: str, line_number: int) -> str:
    """Get the parent function and class of the given line number."""
    tree = ast.parse(file_content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.lineno <= line_number < node.end_lineno:
                return f"Function: {node.name}"
        if isinstance(node, ast.ClassDef):
            if node.lineno <= line_number < node.end_lineno:
                return f"Class: {node.name}"
    return None


def get_list_of_parents(
        file_content: str, line_number: int, context_lines: int = 5,
        with_signature: bool = True) -> List[Dict[str, str]]:
    """Get the list of parent functions and classes of the given line number."""
    tree = ast.parse(file_content)
    parents = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.lineno <= line_number <= node.end_lineno:
                function_name = get_function_signature(
                    node) if with_signature else node.name
                new_parent = {
                    "type": "function",
                    "name": "def " + function_name,
                    "lineno": node.lineno,
                    "end_lineno": node.end_lineno,
                }
                parents.append(new_parent)
        if isinstance(node, ast.ClassDef):
            if node.lineno <= line_number <= node.end_lineno:
                class_parents = get_parent_classes(node)
                new_parent = {
                    "type": "class",
                    "name": f"class {node.name}({', '.join(class_parents)})",
                    "lineno": node.lineno,
                    "end_lineno": node.end_lineno,
                }
                parents.append(new_parent)
    return parents


def get_context_parents_compressed(
        file_content: str, line_number: int, with_signature: bool = True,
        n_context_lines: int = 0) -> str:
    """Get the context and parent functions and classes of the given line number."""
    parents: List[Dict[str, str]] = get_list_of_parents(
        file_content, line_number, with_signature=with_signature)
    context: str = ""
    top_line = max(0, line_number - n_context_lines)
    end_of_file_line = len(file_content.split("\n"))
    bottom_line = min(end_of_file_line, line_number + n_context_lines)
    for level, parent in enumerate(parents):
        parent_type = parent["type"]
        parent_name = parent["name"]
        parent_lineno = parent["lineno"]
        parent_end_lineno = parent["end_lineno"]
        if top_line < parent_lineno:
            break
        if parent_lineno <= line_number <= parent_end_lineno:
            indentation = "    " * level
            context += indentation + parent_name + ":\n"
            if parent_lineno != line_number:
                indentation_subcontent = "    " * (level + 1)
                context += indentation_subcontent + "...\n"
    context += get_context(file_content, line_number, n_context_lines)
    if line_number < bottom_line and bottom_line < end_of_file_line:
        context += "..."
    return context
