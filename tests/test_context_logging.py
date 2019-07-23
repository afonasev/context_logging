import logging
from unittest.mock import ANY

from context_logging.context import (
    ROOT,
    Context,
    context_info,
    current_context,
    logger,
    root_context,
)
from context_logging.setup_log_record import setup_log_record


def test_root_context():
    assert root_context().name == ROOT


def test_current_context():
    assert current_context() is root_context()

    outer_context = Context()
    with outer_context:
        assert current_context() is outer_context

        inner_context = Context()
        with inner_context:
            assert current_context() is inner_context


def test_context_info():
    assert context_info() == {}

    with Context(data='outer', outer=''):
        assert context_info() == {'data': 'outer', 'outer': ''}

        with Context(data='inner', inner=''):
            assert context_info() == {
                'data': 'inner',
                'outer': '',
                'inner': '',
            }

        assert context_info() == {'data': 'outer', 'outer': ''}

    assert context_info() == {}


def test_writing_to_context_info():
    assert context_info() == {}

    with Context():
        assert context_info() == {}

        context_info()['test'] = 'test'
        assert context_info() == {'test': 'test'}

    assert context_info() == {}


def test_context_as_decorator():
    @Context(data='data')
    def wrapped():
        assert context_info() == {'data': 'data'}

    assert context_info() == {}
    wrapped()
    assert context_info() == {}


def test_context_with_start_finish():
    ctx = Context(data='data')
    assert context_info() == {}

    ctx.start()
    assert context_info() == {'data': 'data'}

    ctx.finish()
    assert context_info() == {}


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
        assert exc.args == ('error', {'data': 1})


def test_log_record(caplog):
    setup_log_record()

    logging.info('test')
    assert caplog.records[0].getMessage() == 'test'

    with Context(data=1):
        logging.info('test')
        assert caplog.records[0].getMessage() == 'test (data=1)'
