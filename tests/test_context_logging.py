import logging
import random
import time
from threading import Thread
from typing import List
from unittest.mock import ANY

from context_logging.context import (
    Context,
    ctx_stack,
    current_context,
    root_context,
)
from context_logging.log_record import setup_log_record
from context_logging.logger import logger


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
    ctx = Context(data='data')
    assert current_context == {}

    ctx.start()
    assert current_context == {'data': 'data'}

    ctx.finish()
    assert current_context == {}


def test_default_name():
    assert 'test_context_logging.py' in Context().name


def test_execution_time(mocker):
    mocker.spy(logger, 'info')
    ctx = Context()

    with ctx:
        pass

    logger.info.assert_called_once_with(  # type: ignore
        '%s: executed in %s', ctx.name, ANY
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


@Context()
def _func(n, errors):
    try:
        time.sleep(random.randint(0, 1))  # noqa:S311
        assert current_context['data'] == 'inner'

        current_context['data'] = n
        assert current_context['data'] == n

        for _ in range(3):
            time.sleep(random.randint(0, 1))  # noqa:S311
            assert current_context['data'] == n

    except Exception:
        logging.exception('Error')
        for ctx in ctx_stack.get():
            logging.info('Thread %s, context %s', n, ctx.info)
        errors.append(1)


def test_multithreading_context():
    errors: List[int] = []

    with Context(data='root'):
        with Context(data='inner'):
            threads = []
            for i in range(1):
                t = Thread(target=lambda i=i: _func(i, errors), daemon=True)
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

    assert not errors
