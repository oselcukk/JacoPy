# Contributing to JacoPy

Thank you for your interest in JacoPy. Bug reports, mathematical
corrections, new rules and documentation improvements are all welcome.
This guide explains how to propose a change.

## Ways to contribute

- **Report a bug.** Open an issue with the bug report form. Include a
  short script that reproduces the problem, the output you see, the
  output you expected, and your JacoPy and Python versions.
- **Report a mathematical problem.** If an identity closes that should
  not, or a step cites the wrong source, open a bug report and include
  the identity, the proof chain (`jacopy.print_chain(chain)`), and the
  reference you are comparing with.
- **Propose a feature.** Open an issue with the feature request form
  and describe the mathematics you want to express, with a reference
  where possible.
- **Ask a question.** Use
  [GitHub Discussions](https://github.com/oselcukk/JacoPy/discussions)
  rather than the issue tracker.

## Development setup

```console
$ git clone https://github.com/oselcukk/JacoPy.git
$ cd JacoPy
$ python3 -m venv .venv
$ source .venv/bin/activate
$ python -m pip install -e ".[dev]"
```

`make setup` does the same and also registers a Jupyter kernel for the
example notebooks.

## Making a change

1. Fork the repository and create a branch from `main` with a short,
   descriptive name (for example `fix/wedge-sign` or `docs/cartan-howto`).
2. Keep each pull request to one topic. Large changes are easier to
   review when they are discussed in an issue first.
3. Add or update tests for every change in behavior. A bug fix comes
   with a test that fails before the fix.
4. Run the fast test suite and make sure it passes:

   ```console
   $ python -m pytest tests -q
   ```

   For changes to the proof engine or to rules, also run the suite
   under the model oracle (`python -m pytest tests -q --oracle=strict`,
   which needs the `oracle` extra). The test groups are described in
   `docs/development/testing.md`.
5. Update the documentation and add an entry under `[Unreleased]` in
   `CHANGELOG.md`.
6. Open a pull request and fill in the template.

## Code and documentation conventions

- JacoPy is pure Python and supports Python 3.10 and newer. Do not add
  a required dependency; optional dependencies are declared as extras
  in `pyproject.toml`.
- New public functions and classes get NumPy-style docstrings.
- Every new rewrite rule is a `Definition` (or a proved `Theorem`) and
  records its literature source with `jacopy.bibliography.cite`. State
  sign and grading conventions explicitly; see
  `docs/development/citations.md` for how citations are checked.
- Code, comments, docstrings and documentation are written in English.
- Code shown in the documentation must run against the current
  repository, and printed output must be copied from an actual run.

## Use of AI tools

You may use AI assistants when preparing a contribution, but you are
responsible for every line you submit: you must understand it, have
tested it, and be able to explain it in review. Say in the pull request
template whether and how AI tools were used.

## Code of Conduct

Everyone who takes part in the project is expected to follow the
[Code of Conduct](https://github.com/oselcukk/JacoPy/blob/main/CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed
under the [BSD 3-Clause License](https://github.com/oselcukk/JacoPy/blob/main/LICENSE) that covers the project.
