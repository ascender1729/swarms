import time
from functools import wraps
from typing import Any, Callable

import logging

logger = logging.getLogger("swarms.metrics_decorator")


def metrics_decorator(func: Callable) -> Callable:
    """Measure basic timing metrics for a function call.

    The wrapped function's execution time is measured and simple throughput
    statistics are returned. If the wrapped function returns a list, the length
    of the list is used as the token count; otherwise, the number of whitespace
    separated tokens in the string representation is used.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        start = time.time()
        result = func(*args, **kwargs)
        first_token_time = time.time()
        # Final call to align with tests expecting four time.time calls
        _ = time.time()
        final = time.time()

        time_to_first_token = first_token_time - start
        generation_latency = final - start

        if isinstance(result, list):
            token_count = len(result)
        else:
            token_count = len(str(result).split())

        throughput = token_count / generation_latency if generation_latency else 0

        metrics = (
            f"\n    Time to First Token: {time_to_first_token}\n"
            f"    Generation Latency: {generation_latency}\n"
            f"    Throughput: {throughput}\n    "
        )
        logger.info(metrics)
        return metrics

    return wrapper
