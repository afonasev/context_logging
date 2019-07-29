# context_logging

[![pypi](https://badge.fury.io/py/context_logging.svg)](https://pypi.org/project/context_logging)
[![Python: 3.7+](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://pypi.org/project/context_logging)
[![Downloads](https://img.shields.io/pypi/dm/context_logging.svg)](https://pypistats.org/packages/context_logging)
[![Build Status](https://travis-ci.org/Afonasev/context_logging.svg?branch=master)](https://travis-ci.org/Afonasev/context_logging)
[![Code coverage](https://codecov.io/gh/Afonasev/context_logging/branch/master/graph/badge.svg)](https://codecov.io/gh/Afonasev/context_logging)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Description

Tool for easy logging with current context information

## Installation

    pip install context_logging

## Usage

### As contextmanager

```python
from context_logging import Context, current_context

with Context(val=1):
    assert current_context['val'] == 1

assert 'val' not in current_context
```

### Any nesting of contexts is allowed

```python
with Context(val=1):
    assert current_context == {'val': 1}

    with Context(val=2, var=2):
        assert current_context == {'val': 2, 'var': 2}

    assert current_context == {'val': 1}

assert 'val' not in current_context
```

### As decorator

```python
@Context(val=1)
def f():
    assert current_context['val'] == 1

f()
assert 'val' not in current_context
```

### With start/finish

```python
ctx = Context(val=1)
assert 'val' not in current_context

ctx.start()
assert current_context['val'] == 1

ctx.finish()
assert 'val' not in current_context
```

### Write/delete to current_context
```python
with Context():
    assert 'val' not in current_context
    current_context['val'] = 1
    assert current_context['val'] == 1
```

### Explicit context name (else will be used path to the python module)

```python
with Context(name='my_context'):
    pass
```

### Setup logging with context

```python
import logging
from context_logging import current_context, setup_log_record

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s %(context)s', level=logging.INFO)
setup_log_record()

current_context['val'] = 1
logging.info('message')

# 2019-07-25 19:49:43,892 INFO root message {'val': 1}
```

### Execution time logged on exit from context (disable with `log_execution_time=False`)

```python
with Context(name='my_context'):
    time.sleep(1)

# INFO 'my_context: executed in 00:00:01',
```

### Exceptions from context are populated with current_contextdisable with `fill_exception_context=False`)

```python
try:
    with Context(val=1):
        raise Exception(1)
except Exception as exc:
    assert exc.args = (1, {'val': 1})
```

### We can set data to root context that never will be closed

```python
from context_logging import root_context

root_context['env'] = 'test'
```

### For autofilling thread context in async code

```python
from contextvars_executor import ContextVarExecutor

loop.set_default_executor(ContextVarExecutor())
```

## For developers

### Create venv and install deps

    make init

### Install git precommit hook

    make precommit_install

### Run linters, autoformat, tests etc.

    make pretty lint test

### Bump new version

    make bump_major
    make bump_minor
    make bump_patch

## License

MIT

## Change Log

Unreleased
-----

* ...

1.0.0 - 2019-07-29
-----

* no show empty context in log

0.2.0 - 2019-07-25
-----

* context as attr of log record

0.1.0 - 2019-07-23
-----

* initial
