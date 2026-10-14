"""Sphinx configuration for the JacoPy documentation.

Build locally (from the repository root):

    pip install -e . -r docs/requirements.txt
    sphinx-build -W --keep-going -b html docs docs/_build/html

or ``make docs``.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent
ROOT = DOCS.parent
sys.path.insert(0, str(ROOT))

import jacopy  # noqa: E402

# -- Project information -----------------------------------------------------

project = "JacoPy"
author = "Oğuzhan Selçuk"
copyright = "2025–2026, Oğuzhan Selçuk"
release = jacopy.__version__
version = release

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    # viewcode is off: source listings are browsed on GitHub.
    "sphinx_copybutton",
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # Internal notes that predate the public site (moved or replaced by
    # the explanation and development sections).
    "ARCHITECTURE.md",
    "TESTING.md",
    "CITATIONS.md",
]

nitpicky = False
language = "en"

# -- MyST --------------------------------------------------------------------

myst_enable_extensions = ["dollarmath", "amsmath", "colon_fence", "deflist"]
myst_heading_anchors = 3
myst_dmath_double_inline = True

# -- Autodoc / autosummary / napoleon ----------------------------------------

autosummary_generate = True
autosummary_imported_members = False
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_preserve_defaults = True

napoleon_numpy_docstring = True
napoleon_google_docstring = True
napoleon_use_rtype = False


def _autosummary_filename_map() -> dict[str, str]:
    """Give a distinct file name to entries that differ only in case.

    ``jacopy.Metric`` and ``jacopy.metric`` (and similar pairs) would
    otherwise overwrite each other on case-insensitive file systems.
    """
    names: set[str] = set()
    for page in (DOCS / "reference" / "api").glob("*.md"):
        for line in page.read_text(encoding="utf-8").splitlines():
            match = re.fullmatch(r"\s+(jacopy(?:\.\w+)+)\s*", line)
            if match:
                names.add(match.group(1))
    seen: dict[str, str] = {}
    mapping: dict[str, str] = {}
    for name in sorted(names):
        key = name.lower()
        if key in seen:
            # The capitalised spelling (a class) gets the suffix.
            other = seen[key]
            upper = name if name < other else other
            mapping[upper] = upper + "-class"
        else:
            seen[key] = name
    return mapping


autosummary_filename_map = _autosummary_filename_map()

# -- Intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sympy": ("https://docs.sympy.org/latest", None),
}
intersphinx_timeout = 15

# -- Copy button -------------------------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_exclude = ".linenos, .gp, .go"

# -- MathJax -----------------------------------------------------------------

mathjax3_config = {
    "tex": {
        "macros": {
            "Lie": r"\mathcal{L}",
        },
    },
}

# -- HTML output -------------------------------------------------------------

html_theme = "furo"
html_title = f"JacoPy {release}"
html_short_title = "JacoPy"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = False
html_copy_source = False
html_baseurl = "https://oselcukk.github.io/JacoPy/"
html_theme_options = {
    "source_repository": "https://github.com/oselcukk/JacoPy/",
    "source_branch": "main",
    "source_directory": "docs/",
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-brand-primary": "#1f4e79",
        "color-brand-content": "#1f4e79",
        "font-stack": (
            "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, "
            "sans-serif"
        ),
    },
    "dark_css_variables": {
        "color-brand-primary": "#8cb4e0",
        "color-brand-content": "#8cb4e0",
    },
}

# -- Warning suppressions ----------------------------------------------------
# Targeted suppressions for warnings caused by library docstrings, which the
# documentation build does not edit. Each entry names the reason.

suppress_warnings: list[str] = []

# docs/installation.md is written in a separate change; until it exists the
# landing-page toctree entry would fail the -W build. Inactive once present.
if not (DOCS / "installation.md").exists():
    suppress_warnings.append("toc.not_readable")

# Docstrings that are not valid reStructuredText (unbalanced inline literals,
# indented formula blocks without a separating blank line). They are shown
# verbatim as a literal block instead of being parsed; the library source is
# not edited by the documentation build.
VERBATIM_DOCSTRINGS = {
    "jacopy.brackets.GradedBracket.graded_jacobi_obstruction",
    "jacopy.packages.generalized.prove_general_twist_jacobi",
    "jacopy.packages.generalized.prove_rotated_vector_decomposition",
    "jacopy.packages.generalized.prove_standard_metric_invariance",
    "jacopy.packages.metric_affine.curvature_component_formula",
    "jacopy.packages.metric_affine.prove_e_bianchi_second_identity",
    "jacopy.packages.metric_affine.prove_metric_lie_derivative_identity",
}


def _verbatim_docstring(app, what, name, obj, options, lines):
    if name in VERBATIM_DOCSTRINGS and lines:
        body = ["   " + line if line.strip() else "" for line in lines]
        lines[:] = ["::", "", *body, ""]


# Course materials are cited in the code but are not listed in the public
# documentation: rule attributes whose citation points to them are not shown.
DOC_EXCLUDED_CITATION_KEYS = {"Math595Guideline", "Math595Midterm2026"}


def _skip_course_citations(app, what, name, obj, skip, options):
    if getattr(obj, "key", None) in DOC_EXCLUDED_CITATION_KEYS:
        return True
    return None


def setup(app):
    app.connect("autodoc-process-docstring", _verbatim_docstring)
    app.connect("autodoc-skip-member", _skip_course_citations)


# Keep the build deterministic: autodoc imports never trigger the model oracle.
os.environ.setdefault("JACOPY_ORACLE", "off")
