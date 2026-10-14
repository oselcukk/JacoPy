# jacopy — development convenience targets.
#
# Quick start:
#   make setup      # one-shot: create .venv, install editable + all deps,
#                   # register Jupyter kernel.
#   make test       # run the full test suite inside .venv.
#   make notebooks  # smoke-execute every tutorial notebook.
#   make clean      # remove .venv and caches.

# Override with e.g. `make setup PYTHON=/opt/homebrew/bin/python3.12`.
PYTHON ?= python3
VENV   := .venv
VBIN   := $(VENV)/bin

.PHONY: setup test test-oracle notebooks clean kernel deps test-wheel

# One-shot dev environment.
setup: $(VENV)/.installed kernel
	@echo "✓ Setup complete. Activate with:  source $(VBIN)/activate"
	@echo "  Or open a notebook and pick the 'Python (JacoPy)' kernel."

$(VENV)/bin/python:
	$(PYTHON) -m venv $(VENV)
	$(VBIN)/pip install --upgrade pip

$(VENV)/.installed: $(VENV)/bin/python pyproject.toml
	$(VBIN)/pip install -e ".[dev]"
	@touch $@

deps: $(VENV)/.installed

kernel: $(VENV)/.installed
	$(VBIN)/python -m ipykernel install --user --name=jacopy-v3 \
		--display-name="Python (JacoPy)"

test: $(VENV)/.installed
	$(VBIN)/python -m pytest tests/ -q

# Model oracle (jacopy.oracle) on every closed equation; report in .oracle/.
test-oracle: $(VENV)/.installed
	$(VBIN)/python -m pytest tests/ -q --oracle=warn --oracle-report=.oracle/report.json

notebooks: $(VENV)/.installed
	$(VBIN)/python scripts/run_notebooks.py

clean:
	rm -rf $(VENV) .pytest_cache **/__pycache__ .mypy_cache .ruff_cache

# Build the wheel and run the fast suite from the INSTALLED package in a
# throw-away venv (what CI does on every supported Python).
test-wheel: $(VENV)/.installed
	rm -rf build dist && $(VBIN)/python -m pip install -q build && $(VBIN)/python -m build --wheel --outdir dist
	rm -rf .wheel-test && $(PYTHON) -m venv .wheel-test && .wheel-test/bin/pip install -q dist/*.whl pytest
	rm -rf .wheel-test/tests && cp -R tests .wheel-test/tests && cd .wheel-test && bin/python -m pytest tests -q -p no:cacheprovider

# Documentation: build the HTML site with warnings as errors, then run every
# Python example in docs/. Uses a separate venv (.venv-docs) so the docs
# toolchain never touches .venv. Output: docs/_build/html/index.html.
DOCS_VENV := .venv-docs
.PHONY: docs
docs:
	test -x $(DOCS_VENV)/bin/python || $(PYTHON) -m venv $(DOCS_VENV)
	$(DOCS_VENV)/bin/pip install -q -e . -r docs/requirements.txt
	$(DOCS_VENV)/bin/sphinx-build -W --keep-going -b html docs docs/_build/html
	$(DOCS_VENV)/bin/python docs/check_examples.py
