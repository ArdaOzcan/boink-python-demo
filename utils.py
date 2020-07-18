import re
from string import ascii_uppercase


def camel_to_snake(name):
    """Convert a camelCase or PascalCase string to snake_case.

    Args:
        name (str): Original string.

    Returns:
        str: camel_case string.
    """

    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
