"""Greek letter NAMES spelled in ASCII render as LaTeX commands
(display-polish 2026-10-02): ``forms("omega")`` → ``\\omega``,
``Pi`` → ``\\Pi``, ``omega_1`` → ``\\omega_1``. Before, they came out
as the bare words ``omega`` / ``Pi``. Display only."""

from __future__ import annotations

import pytest

import jacopy
from jacopy.central.objects import forms, vector_fields
from jacopy.display import latex_name, to_ascii, to_latex


class TestGreekNames:
    def test_forms_named_omega(self):
        (omega,) = forms("omega", degree=1)
        assert to_latex(omega) == r"\omega"
        # the ASCII renderer prints the name as the user wrote it
        assert to_ascii(omega) == "omega"

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("omega", r"\omega"),
            ("omega_1", r"\omega_1"),
            ("omega_12", r"\omega_{12}"),
            ("alpha_ij", r"\alpha_{ij}"),
            ("x_alpha", r"x_{\alpha}"),
            ("Pi", r"\Pi"),
            ("pi", r"\pi"),
            ("Omega", r"\Omega"),
            ("theta", r"\theta"),
            ("eta", r"\eta"),
            ("mu", r"\mu"),
            ("varphi", r"\varphi"),
            ("pi(alpha)", r"\pi(\alpha)"),
            ("K_X_omega", r"K_{X_{\omega}}"),
        ],
    )
    def test_ascii_greek_names_become_commands(self, name, expected):
        assert latex_name(name) == expected

    @pytest.mark.parametrize("name", ["omegax", "betaX", "Pinv", "zetas", "Alpha", "Eta", "Mu"])
    def test_longer_identifiers_and_latin_looking_capitals_unchanged(self, name):
        # whole words only; Alpha/Eta/Mu look like Latin A/H/M and have no command
        assert latex_name(name) == name

    def test_unicode_and_existing_commands_not_doubled(self):
        assert latex_name("ω") == r"\omega"
        assert latex_name("ω₂") == r"\omega_{2}"
        assert latex_name(r"\omega") == r"\omega"
        assert latex_name("Π₃") == r"\Pi_{3}"

    def test_operator_expression_with_omega(self):
        X, Y = vector_fields("X Y")
        (omega,) = forms("omega", degree=1)
        lhs = jacopy.pairing(jacopy.lie_derivative(X)(omega), Y)
        assert to_latex(lhs) == r"\langle \mathcal{L}_{X}\!\left(\omega\right),\, Y \rangle"
