import logging
from copy import deepcopy
from typing import Any

from .context import current_context


class ContextLogRecord(logging.LogRecord):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.context = deepcopy(current_context) or ''


def setup_log_record() -> None:
    logging.setLogRecordFactory(ContextLogRecord)
