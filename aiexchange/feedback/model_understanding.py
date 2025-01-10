from typing import List, Dict


def remove_backticks_lines(text: str) -> str:
    new_lines = [line for line in text.split(
        '\n') if not line.startswith('```')]
    return '\n'.join(new_lines)
