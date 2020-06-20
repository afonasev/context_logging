import time
from collections import UserDict
from contextlib import ContextDecorator
from contextvars import ContextVar
from typing import Any, Callable, ChainMap, Dict, List, Optional, Type, cast

from .config import config
from .logger import logger
from .utils import context_name_with_code_path, seconds_to_time_string

ROOT = 'root'


class Context(ContextDecorator):
    def __init__(
        self,
        name: Optional[str] = None,
        *,
        log_execution_time: Optional[bool] = None,
        fill_exception_context: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.name = name or context_name_with_code_path()
        self.info = kwargs

        if log_execution_time is None:
            log_execution_time = config.LOG_EXECUTION_TIME_DEFAULT
        self._log_execution_time = log_execution_time

        if fill_exception_context is None:
            fill_exception_context = config.FILL_EXEPTIONS_DEFAULT
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
                seconds_to_time_string(self.finish_time),
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
    ) -> None:
        self.finish(exc_value)


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
