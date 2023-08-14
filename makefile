BIN = .venv/bin/
CODE = context_logging

.PHONY: init
init:
	python3 -m venv .venv
	poetry install

.PHONY: test
test:
	$(BIN)pytest --verbosity=2 --showlocals --strict-markers --log-level=DEBUG --cov=$(CODE) $(args)

.PHONY: lint
lint:
	$(BIN)flake8 --jobs 4 --statistics --show-source $(CODE) tests
	$(BIN)pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(BIN)mypy $(CODE) tests
	$(BIN)black --skip-string-normalization --line-length=79 --check $(CODE) tests
	$(BIN)pytest --dead-fixtures --dup-fixtures

.PHONY: pretty
pretty:
	$(BIN)isort --apply --recursive $(CODE) tests
	$(BIN)black --skip-string-normalization --line-length=79 $(CODE) tests
	$(BIN)unify --in-place --recursive $(CODE) tests

.PHONY: precommit_hook
precommit_hook:
	echo '#!/bin/sh\nmake lint test\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

.PHONY: bump_major
bump_major:
	$(BIN)bumpversion major

.PHONY: bump_minor
bump_minor:
	$(BIN)bumpversion minor

.PHONY: bump_patch
bump_patch:
	$(BIN)bumpversion patch

.PHONY: ci
ci: lint test
ci: $(BIN)codecov
