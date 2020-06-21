# context_logging

[![pypi](https://badge.fury.io/py/context-logging.svg)](https://pypi.org/project/context_logging)
[![Python: 3.7+](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://pypi.org/project/context_logging)
[![Downloads](https://img.shields.io/pypi/dm/context_logging.svg)](https://pypistats.org/packages/context_logging)
![CI Status](https://github.com/afonasev/context_logging/workflows/ci/badge.svg?branch=master)
[![Code coverage](https://codecov.io/gh/Afonasev/context_logging/branch/master/graph/badge.svg)](https://codecov.io/gh/Afonasev/context_logging)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Description

Tool for easy logging with current context information.

```python
from context_logging import current_context

logging.info('before context')
# 2019-07-25 19:49:43 INFO before context

with Context('my_context'):
    current_context['var'] = 1
    logging.info('in context')
    # 2019-07-25 19:49:43 INFO in context {'var': 1}

# 2019-07-25 19:49:43 INFO 'my_context: executed in 00:00:01 {'var': 1}'

logging.info('after context')
# 2019-07-25 19:49:43 INFO after context
```

## Installation

    pip install context_logging

## Usage

### Setup logging with context

```python
import logging
from context_logging import current_context, setup_log_record

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s %(context)s',
    level=logging.INFO,
)
setup_log_record()

current_context['var'] = 1
logging.info('message')

# 2019-07-25 19:49:43,892 INFO root message {'var': 1}
```

### As contextmanager

```python
from context_logging import Context, current_context

with Context(var=1):
    assert current_context['var'] == 1

assert 'var' not in current_context
```

### Any nesting of contexts is allowed

```python
with Context(var=1):
    assert current_context == {'var': 1}

    with Context(val=2, var=2):
        assert current_context == {'val': 2, 'var': 2}

    assert current_context == {'var': 1}

assert 'var' not in current_context
```

### As decorator

```python
@Context(var=1)
def f():
    assert current_context['var'] == 1

f()
assert 'var' not in current_context
```

### With start/finish [DEPRECATED]

```python
ctx = Context(var=1)
assert 'var' not in current_context

ctx.start()
assert current_context['var'] == 1

ctx.finish()
assert 'var' not in current_context
```

### Add/remove values from current_context
```python
with Context():
    assert 'var' not in current_context
    current_context['var'] = 1
    assert current_context['var'] == 1
```

### Explicit context name (else will be used path to the python module)

```python
with Context('my_context'):
    pass
```

### Execution time logged on exit from context (it can be disabled with `log_execution_time=False` argument)

```python
with Context('my_context'):
    time.sleep(1)

# INFO 'my_context: executed in 00:00:01',
```

Default value for log_execution_time param can be changed with env

    export CONTEXT_LOGGING_LOG_EXECUTION_TIME_DEFAULT=0

### Exceptions from context are populated with current_context (it can be disabled with `fill_exception_context=False` argument)

```python
try:
    with Context(var=1):
        raise Exception(1)
except Exception as exc:
    assert exc.args = (1, {'var': 1})
```

Default value for fill_exception_context param can be changed with env

    export CONTEXT_LOGGING_FILL_EXEPTIONS_DEFAULT=0

### We can set data to root context that never will be closed

```python
from context_logging import root_context

root_context['env'] = 'test'
```

### If you want to pass context to other threads use [ContextVarExecutor](https://github.com/hellysmile/contextvars_executor)

```python
from context_logging import ContextVarExecutor

with ContextVarExecutor() as executor:
    executor.submit(...)

# OR

loop.set_default_executor(ContextVarExecutor())  # for asyncio loop
```

## For developers

### Create venv and install deps

    make init

### Install git precommit hook

    make precommit_hook

### Run linters, autoformat, tests etc.

    make pretty lint test

### Bump new version

    make bump_major
    make bump_minor
    make bump_patch
