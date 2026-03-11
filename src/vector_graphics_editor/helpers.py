"""Module providing helper functions."""
import re

def camelcase_to_snakecase(func_name: str) -> str:
    """Change format of provided function name from CamelCase to snake_case
    and returns the result.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', func_name).lower()
