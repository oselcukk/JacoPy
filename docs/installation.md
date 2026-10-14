# Installation

JacoPy is a pure-Python package with no required dependencies. This page
explains how to install it, which optional extras exist, and how to set
up a development checkout.

## Requirements

JacoPy needs Python 3.10 or newer. It is tested on Python 3.10, 3.11,
3.12, 3.13 and 3.14 on Linux, and it runs on any operating system with
a supported Python.

## Install from GitHub

JacoPy is not yet on PyPI; a release there is planned. Until then,
install the current version directly from the repository:

```console
$ python -m pip install "git+https://github.com/oselcukk/JacoPy"
```

To include an optional extra, name it after the package:

```console
$ python -m pip install "jacopy[oracle] @ git+https://github.com/oselcukk/JacoPy"
```

Check the installation:

```console
$ python -c "import jacopy; print(jacopy.__version__)"
0.1.0a1
```

## Optional extras

| Extra | Installs | Used for |
|---|---|---|
| `oracle` | sympy | the model oracle (`jacopy.oracle`, `pytest --oracle=...`) |
| `rich` | rich | colored proof trees in the terminal (plain text without it) |
| `test` | pytest | the test suite |
| `dev` | all of the above and ipykernel | development |

SymPy is used only by the model oracle, which checks closed identities
numerically in random coordinate models. The proof engine itself does
not import it.

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
[Testing](development/testing.md); how to propose a change is described
in [Contributing](development/contributing.md).
