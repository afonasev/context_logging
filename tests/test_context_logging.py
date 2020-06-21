import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import ANY

import pytest

from context_logging import ContextVarExecutor
from context_logging.context import (
    Context,
    ContextObject,
    current_context,
    root_context,
)
from context_logging.log_record import setup_log_record
from context_logging.logger import logger


def test_context_object_finish(caplog):
    context = ContextObject(
        name='name',
        log_execution_time=True,
        fill_exception_context=True,
        context_data={},
    )
    context.start()
    context.finish()
    assert 'name: executed in' in caplog.records[-1].message


def test_root_context():
    assert root_context == {}
    current_context['val'] = 1
    assert root_context == {'val': 1}
    root_context.clear()


def test_current_context():
    assert current_context == {}

    with Context(data='outer', outer=''):
        assert current_context == {'data': 'outer', 'outer': ''}

        with Context(data='inner', inner=''):
            assert current_context == {
                'data': 'inner',
                'outer': '',
                'inner': '',
            }

        assert current_context == {'data': 'outer', 'outer': ''}

    assert current_context == {}


def test_writing_to_context_info():
    assert current_context == {}

    with Context():
        assert current_context == {}

        current_context['test'] = 'test'
        assert current_context == {'test': 'test'}

    assert current_context == {}


def test_context_as_decorator():
    @Context(data='data')
    def wrapped():
        assert current_context == {'data': 'data'}

    assert current_context == {}
    wrapped()
    assert current_context == {}


def test_context_with_start_finish():
    context = Context(data='data')
    assert current_context == {}

    context.start()
    assert current_context == {'data': 'data'}

    context.finish()
    assert current_context == {}


def test_default_name():
    assert 'test_context_logging.py' in Context().name


def test_execution_time(mocker):
    mocker.spy(logger, 'info')
    context = Context()

    with context:
        pass

    logger.info.assert_called_once_with(  # type: ignore
        '%s: executed in %s', context.name, ANY
    )


def test_fill_exception_context():
    try:
        with Context(data=1):
            raise Exception('error')
    except Exception as exc:
        assert exc.args == ('error', {'data': 1})  # noqa:PT017


def test_fill_exception_last_context():
    try:
        with Context(data=1):
            with Context(data=2):
                raise Exception('error')
    except Exception as exc:
        assert exc.args == ('error', {'data': 2})  # noqa:PT017


def test_log_record(caplog):
    setup_log_record()

    logging.info('test')
    assert caplog.records[-1].context == ''

    with Context(data=1):
        logging.info('test')
        assert caplog.records[-1].context == {'data': 1}


def sync_task():
    assert current_context['data'] == 1
    current_context['data'] = 2


async def async_task():
    sync_task()


@pytest.mark.asyncio
async def test_context_passing_to_asyncio_task_with_context_leaking():
    with Context(data=1):
        await asyncio.create_task(async_task())
        assert current_context['data'] == 2


@pytest.mark.asyncio
async def test_context_passing_to_asyncio_task_with_separate_context():
    with Context(data=1):
        wrapped_task = Context()(async_task)
        await asyncio.create_task(wrapped_task())  # type: ignore
        assert current_context['data'] == 1


def test_context_passing_to_thread_without_context_var_executor():
    with Context(data=1):
        with ThreadPoolExecutor() as executor:
            with pytest.raises(KeyError):
                executor.submit(sync_task).result()


def test_context_passing_to_thread_with_context_leaking():
    with Context(data=1):
        with ContextVarExecutor() as executor:
            executor.submit(sync_task).result()

        assert current_context['data'] == 2


def test_context_passing_to_thread_with_separate_context():
    with Context(data=1):
        with ContextVarExecutor() as executor:
            wrapped_task = Context()(sync_task)
            executor.submit(wrapped_task).result()

        assert current_context['data'] == 1


@Context()
def not_safe_long_task(n):
    time.sleep(0.1)
    assert current_context['data'] == 'start'

    current_context['data'] = n
    assert current_context['data'] == n

    for _ in range(3):
        time.sleep(0.1)
        assert current_context['data'] == n


def test_multithreading_context_leaking():
    with Context(data='start'):
        with ContextVarExecutor() as executor:
            for _ in executor.map(not_safe_long_task, range(5)):
                pass

        assert current_context['data'] == 'start'
