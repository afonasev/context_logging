import logging

from .context import current_context


class ContextInfoLogRecord(logging.LogRecord):
    def getMessage(self) -> str:  # noqa:N802
        message = super().getMessage()

        if not current_context:
            return message

        sorted_info = sorted(current_context.items())

        ctx_info = ', '.join(f'{k}={v}' for k, v in sorted_info)
        return f'{message} ({ctx_info})'


def setup_log_record() -> None:
    logging.setLogRecordFactory(ContextInfoLogRecord)
