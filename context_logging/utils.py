# pylint:disable=not-context-manager
from contextlib import ContextDecorator
from datetime import timedelta
from functools import wraps
from inspect import getframeinfo, iscoroutinefunction, stack
from typing import Any, Callable


class SyncAsyncContextDecorator(ContextDecorator):
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        if iscoroutinefunction(func):

            @wraps(func)
            async def async_inner(*args: Any, **kwds: Any) -> Any:
                with self._recreate_cm():  # type: ignore
                    return await func(*args, **kwds)

            return async_inner

        @wraps(func)
        def sync_inner(*args: Any, **kwds: Any) -> Any:
            with self._recreate_cm():  # type: ignore
                return func(*args, **kwds)

        return sync_inner


def context_name_with_code_path() -> str:
    """
    >>> _default_name()
    'Context /path_to_code/code.py:10'
    """
    caller = getframeinfo(stack()[2][0])
    return f'Context {caller.filename}:{caller.lineno}'


def seconds_to_time_string(seconds: float) -> str:
    """
    >>> _seconds_to_time(seconds=10000)
    '2:46:40'
    """
    return str(timedelta(seconds=seconds))
