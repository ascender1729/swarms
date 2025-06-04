from functools import wraps
from typing import Any, Callable

import logging

logger = logging.getLogger("swarms.math_eval")


def math_eval(func1: Callable, func2: Callable) -> Callable:
    """Decorator to compare outputs of two functions for the same input.

    The decorated function will execute ``func1`` and ``func2`` with the same
    arguments. Any exceptions are logged and ``None`` is returned for the
    failing function. A warning is logged if the outputs differ.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            try:
                result1 = func1(*args, **kwargs)
            except Exception as e:  # pragma: no cover - just logs
                logger.error(f"Error in func1: {e}")
                result1 = None

            try:
                result2 = func2(*args, **kwargs)
            except Exception as e:  # pragma: no cover - just logs
                logger.error(f"Error in func2: {e}")
                result2 = None

            if result1 != result2:
                logger.warning("Outputs do not match")

            return result1, result2

        return wrapper

    return decorator
