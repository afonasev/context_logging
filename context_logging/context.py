import time
from collections import UserDict
from contextvars import ContextVar, Token
from typing import Any, ChainMap, Dict, Optional, Type, cast

from deprecated import deprecated

from .config import config
from .logger import logger
from .utils import (
    SyncAsyncContextDecorator,
    context_name_with_code_path,
    seconds_to_time_string,
)

ROOT_CONTEXT_NAME = 'root'


class ContextFactory(SyncAsyncContextDecorator):
    def __init__(
        self,
        name: Optional[str] = None,
        *,
        log_execution_time: Optional[bool] = None,
        fill_exception_context: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        self.name = name or context_name_with_code_path()
        self._context_data = kwargs

        if log_execution_time is None:
            log_execution_time = config.LOG_EXECUTION_TIME_DEFAULT
        self._log_execution_time = log_execution_time

        if fill_exception_context is None:
            fill_exception_context = config.FILL_EXEPTIONS_DEFAULT
        self._fill_exception_context = fill_exception_context

    @deprecated
    def start(self) -> None:
        self.__enter__()

    @deprecated
    def finish(self) -> None:
        self.__exit__(None, None, None)

    def __enter__(self) -> 'ContextObject':
        context = self.create_context()
        context.start()
        return context

    def __exit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        traceback: Any,
    ) -> None:
        context = _current_context.get()
        context.finish(exc_value)

    def create_context(self) -> 'ContextObject':
        return ContextObject(
            name=self.name,
            log_execution_time=self._log_execution_time,
            fill_exception_context=self._fill_exception_context,
            context_data=self._context_data.copy(),
        )


class ContextObject(UserDict):  # type: ignore
    def __init__(  # pylint:disable=super-init-not-called
        self,
        name: str,
        log_execution_time: bool,
        fill_exception_context: bool,
        context_data: Dict[Any, Any],
    ) -> None:
        self.name = name

        self._log_execution_time = log_execution_time
        self._fill_exception_context = fill_exception_context
        self._context_data = context_data

        self._parent_context: Optional[ContextObject] = None
        self._parent_context_token: Optional[Token[ContextObject]] = None
        self._start_time: Optional[float] = None

    @property
    def data(self) -> ChainMap[Any, Any]:  # type: ignore
        return ChainMap(self._context_data, self._parent_context or {})

    def start(self) -> None:
        self._parent_context = _current_context.get()
        self._parent_context_token = _current_context.set(self)
        self._start_time = time.monotonic()

    def finish(self, exc: Optional[Exception] = None) -> None:
        if self._log_execution_time:
            finish_time = time.monotonic() - cast(float, self._start_time)

            logger.info(
                '%s: executed in %s',
                self.name,
                seconds_to_time_string(finish_time),
            )

        if exc and self._fill_exception_context and current_context:
            if not getattr(exc, '__context_logging__', None):
                exc.__context_logging__ = True  # type: ignore
                exc.args += (dict(current_context),)

        _current_context.reset(
            cast(Token, self._parent_context_token)  # type: ignore
        )


root_context = ContextFactory(name=ROOT_CONTEXT_NAME).create_context()

_current_context: ContextVar[ContextObject] = ContextVar(
    'ctx', default=root_context
)


class CurrentContextProxy(UserDict):  # type: ignore
    def __init__(self) -> None:  # pylint:disable=super-init-not-called
        pass

    @property
    def data(self) -> ContextObject:  # type: ignore
        return _current_context.get()


current_context = CurrentContextProxy()
Context = ContextFactory  # for backward compatibility
