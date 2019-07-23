import logging
from unittest.mock import ANY

from context_logging.context import (
    Context,
    current_context,
    logger,
    root_context,
)
from context_logging.setup_log_record import setup_log_record


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
        assert exc.args == ('error', {'data': 1})


def test_log_record(caplog):
    setup_log_record()

    logging.info('test')
    assert caplog.records[0].getMessage() == 'test'

    with Context(data=1):
        logging.info('test')
        assert caplog.records[0].getMessage() == 'test (data=1)'
