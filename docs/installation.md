# Installation

JacoPy is a pure-Python package with no required dependencies. This page
explains how to install it and which optional extras exist.

## Requirements

JacoPy needs Python 3.10 or newer. It is tested on Python 3.10, 3.11,
3.12, 3.13 and 3.14 on Linux, and it runs on any operating system with
a supported Python.

## Install from PyPI

```console
$ python -m pip install jacopy
```

To include an optional extra, name it in brackets:

```console
$ python -m pip install "jacopy[oracle]"
```

To upgrade to the latest release:

```console
$ python -m pip install --upgrade jacopy
```

Check the installation:

```console
$ python -c "import jacopy; print(jacopy.__version__)"
0.1.0
```

The development version can be installed directly from the repository:

```console
$ python -m pip install "git+https://github.com/oselcukk/JacoPy"
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

For an editable checkout and the test suite, see the [development guide](development/index.md).
