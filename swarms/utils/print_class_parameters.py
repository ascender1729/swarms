import inspect
from typing import Any, Dict

import logging

logger = logging.getLogger("swarms.print_class_parameters")


def print_class_parameters(cls: Any, api_format: bool = False) -> Dict[str, str]:
    """Return or display constructor parameter types for a class.

    Args:
        cls: The class object to introspect.
        api_format: If True, return a dictionary mapping parameter names to the
            string representation of their annotations. When False, the mapping
            is also printed.

    Raises:
        Exception: If ``cls`` is not a class or has no ``__init__`` signature.
    """
    if not inspect.isclass(cls) or cls.__module__ == "builtins":
        raise Exception("Input must be a user-defined class")
    if cls.__init__ is object.__init__:
        raise Exception("Class has no __init__ method")

    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]  # skip self
    if not params:
        raise Exception("Class has no parameters")

    result: Dict[str, str] = {p.name: str(p.annotation) for p in params}

    if not api_format:
        for name, ann in result.items():
            logger.info(f"{name}: {ann}")
    return result
