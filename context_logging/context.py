import logging
import time
from collections import UserDict
from contextlib import ContextDecorator
from contextvars import ContextVar
from datetime import timedelta
from inspect import getframeinfo, stack
from typing import Any, Callable, ChainMap, Dict, List, Optional, Type, cast

ROOT = 'root'
logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())


class Context(ContextDecorator):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        log_execution_time: bool = True,
        fill_exception_context: bool = True,
        **kwargs: Any,
    ) -> None:
        self.name = name or _default_name()
        self.info = kwargs
        self._log_execution_time = log_execution_time
        self._fill_exception_context = fill_exception_context

        self.start_time: Optional[float] = None
        self.finish_time: Optional[float] = None

    def start(self) -> None:
        ctx_stack.get().append(self)
        self.start_time = time.monotonic()

    def finish(self, exc: Optional[Exception] = None) -> None:
        self.finish_time = time.monotonic() - cast(float, self.start_time)

        if self._log_execution_time:
            logger.info(
                '%s: executed in %s',
                self.name,
                _seconds_to_time(self.finish_time),
            )

        if exc and self._fill_exception_context and current_context:
            if not getattr(exc, '__context_logging__', None):
                exc.__context_logging__ = True  # type: ignore
                exc.args += (dict(current_context),)

        ctx_stack.get().remove(self)

    def __enter__(self) -> None:
        self.start()

    def __exit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        traceback: Any,
    ) -> bool:
        self.finish(exc_value)
        return False


ctx_stack: ContextVar[List[Context]] = ContextVar(
    'ctx', default=[Context(name=ROOT)]
)


class ContextProxy(UserDict):  # type: ignore
    def __init__(  # pylint:disable=super-init-not-called
        self, get_info: Callable[[], Dict[str, Any]]
    ) -> None:
        self._get_info = get_info

    @property
    def data(self) -> Dict[str, Any]:  # type: ignore
        return self._get_info()


def _root_context() -> Dict[str, Any]:
    return ctx_stack.get()[0].info


def _current_context() -> ChainMap[str, Any]:
    _stack = ctx_stack.get()
    return ChainMap(*(c.info for c in _stack[::-1]))


current_context = ContextProxy(_current_context)  # type: ignore
root_context = ContextProxy(_root_context)


def _default_name() -> str:
    """
    >>> _default_name()
    'Context /path_to_code/code.py:10'
    """
    caller = getframeinfo(stack()[2][0])
    return f'Context {caller.filename}:{caller.lineno}'


def _seconds_to_time(seconds: float) -> str:
    """
    >>> _seconds_to_time(seconds=10000)
    '2:46:40'
    """
    return str(timedelta(seconds=seconds))
