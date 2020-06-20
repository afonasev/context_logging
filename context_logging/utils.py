from datetime import timedelta
from inspect import getframeinfo, stack


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
