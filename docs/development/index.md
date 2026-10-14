# Development

These pages are for people who work on JacoPy itself: how to contribute,
how the test suite is organized, how literature citations are checked,
and what changed between versions.

## Development install

For a checkout you can edit, clone the repository and install it in
editable mode inside a virtual environment:

```console
$ git clone https://github.com/oselcukk/JacoPy.git
$ cd JacoPy
$ python3 -m venv .venv
$ source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
$ python -m pip install -e ".[dev]"
$ python -m pytest tests -q        # the fast test suite
```

`make setup` does the same on Linux and macOS and also registers a
Jupyter kernel for the example notebooks in `examples/`. The test
suites and their options are described in
[Testing](testing.md); how to propose a change is described
in [Contributing](contributing.md).

```{toctree}
:maxdepth: 1

contributing
testing
citations
changelog
```
