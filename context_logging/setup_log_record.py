import logging

from .context import context_info


class ContextInfoLogRecord(logging.LogRecord):
    def getMessage(self) -> str:  # noqa:N802
        message = super().getMessage()
        if not context_info():
            return message
        sorted_info = sorted(context_info().items())
        ctx_info = ', '.join(f'{k}={v}' for k, v in sorted_info)
        return f'{message} ({ctx_info})'


def setup_log_record() -> None:
    logging.setLogRecordFactory(ContextInfoLogRecord)
