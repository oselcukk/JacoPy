# Literature citations — verification and bibliography

Every paper label the code uses ([C1]–[C5], (L), (7.8), Definition 7.1, Lemma 9.1, Uchino Proposition 2.2, …) was checked against the local PDF of the paper (pdftotext text; page images where a sign was unclear). Quotes are kept to one short line; the PDFs themselves are not in git (`.gitignore`), so the page numbers below refer to the local copies listed in the bibliography.

Rules and theorems carry their source as data (`Definition.source`, `Theorem.source`, built with `jacopy.bibliography.cite`); the engine copies it onto each proof step and the ASCII/LaTeX renderers print it as an APA 7 in-text citation, e.g. `(Liu et al., 1997; Uchino, 2002, Section 1, axiom [C5])`. The reference list below is generated from `jacopy/bibliography.py` (test: `tests/test_citations.py`).

## Summary

Every label was given one of these statuses:

* **verified** — number and content match the paper;
* **wrong number** — right paper, wrong number (fixed);
* **wrong paper** — the number belongs to another paper (fixed);
* **not in the paper** — the label does not exist in the paper (fixed or re-labelled);
* **ambiguous** — cannot be decided from the text;
* **secondary source only** — no local PDF; fields and claims come from a secondary source;
* **other** — not a paper-number check: wording or over-claim errors (fixed), file-name or style citations, and rules that had no label and were given a verified source.

| scope | verified | wrong number | wrong paper | not in the paper | ambiguous | secondary source only | other | total |
|---|---|---|---|---|---|---|---|---|
| Uchino (2002), LWX, Roytenberg and other works without a local PDF — generalized/Courant modules | 27 | 0 | 0 | 0 | 0 | 4 | 2 | 33 |
| Çatal-Özer, Dereli & Doğan (2022) [B] — Bourbaki modules | 30 | 1 | 0 | 1 | 0 | 2 | 0 | 34 |
| Dereli & Doğan (2020) [MC], Dereli & Doğan (2023) [ADM], B §4, Math 595 midterm — central, metric-affine, Poisson | 43 | 3 | 1 | 1 | 2 | 2 | 8 | 60 |
| Çatal-Özer, Doğan & Yetişmişoğlu (2024) [DD] and (2025) [TW] — Drinfel'd package | 36 | 8 | 2 | 2 | 3 | 2 | 1 | 54 |
| all | 136 | 12 | 3 | 4 | 5 | 10 | 11 | 181 |

## References (APA 7)

Generated from `jacopy/bibliography.py`. Fields come from the local PDF's title page, or, for works without a local PDF, from the reference list named in the entry's `secondary` field; a bracketed gap marks a field no source gives.

<!-- references:begin -->
Asakawa, T., Muraki, H., Sasa, S., & Watamura, S. (2015). Poisson-generalized geometry and R-flux. *International Journal of Modern Physics A*, *30*, Article 1550097. [issue, DOI not in source] arXiv:1408.2649

Çatal-Özer, A., Dereli, T., & Doğan, K. (2022). *Pre-metric-Bourbaki algebroids: Cartan calculus for M-theory* (arXiv:2210.00548). arXiv. https://doi.org/10.48550/arXiv.2210.00548

Çatal-Özer, A., Doğan, K., & Yetişmişoğlu, C. (2024). Drinfel’d double of bialgebroids for string and M theories: Dual calculus framework. *Journal of High Energy Physics*, *2024*(7), Article 030. https://doi.org/10.1007/JHEP07(2024)030

Çatal-Özer, A., Doğan, K., & Yetişmişoğlu, C. (2025). Drinfel’d doubles, twists and all that… in stringy geometry and M theory. *Journal of High Energy Physics*, *2025*(1), Article 192. https://doi.org/10.1007/JHEP01(2025)192

Dereli, T., & Doğan, K. (2020). *Metric-connection geometries on pre-Leibniz algebroids: A search for geometrical structure in string models* (arXiv:2006.05957). arXiv. https://doi.org/10.48550/arXiv.2006.05957

Dereli, T., & Doğan, K. (2023). ‘Anti-commutable’ local pre-Leibniz algebroids and admissible connections. *Journal of Geometry and Physics*, *186*, Article 104752. https://doi.org/10.1016/j.geomphys.2023.104752

Grabowski, J., & Marmo, G. (2001). Non-antisymmetric versions of Nambu-Poisson and algebroid brackets. *Journal of Physics A: Mathematical and General*, *34*, 3803–3809. [issue, DOI not in source]

Kosmann-Schwarzbach, Y. (2004). Derived brackets. *Letters in Mathematical Physics*, *69*, 61. [issue, last page, DOI not in source] arXiv:math/0312524

Liu, Z.-J., Weinstein, A., & Xu, P. (1997). Manin triples for Lie bialgebroids. *Journal of Differential Geometry*, *45*, 547–574. [issue, DOI not in source] arXiv:dg-ga/9508013

*Math 595 – JacoPy* [Unpublished course project guidelines]. (n.d.).

*Math 595 midterm, Spring 2026* [Unpublished course examination, Gebze Technical University]. (2026).

Roytenberg, D. (1999). *Courant algebroids, derived brackets and even symplectic supermanifolds* [Doctoral dissertation, University of California, Berkeley]. arXiv. https://doi.org/10.48550/arXiv.math/9910078

Ševera, P. (2017). *Letters to Alan Weinstein about Courant algebroids* (arXiv:1707.00265). arXiv. https://doi.org/10.48550/arXiv.1707.00265

Uchino, K. (2002). *Remarks on the definition of a Courant algebroid* (arXiv:math/0204010). arXiv. https://doi.org/10.48550/arXiv.math/0204010
<!-- references:end -->

| key | alias | local PDF | fields taken from | missing fields | caveat |
|---|---|---|---|---|---|
| `AsakawaMurakiSasaWatamura2015` | Watamura | —  | Çatal-Özer et al. (2024) ref. [56]; Çatal-Özer et al. (2025) ref. [95] (no local PDF) | issue, doi | no local PDF: equation numbers cited from it are unverified |
| `CatalOzerDereliDogan2022` | B | pre-metric-bourbaki.pdf (arXiv v1, 2 Oct 2022) | PDF title page | — | — |
| `CatalOzerDoganYetismisoglu2024` | DD | drinfeld double.pdf (journal version) | PDF title page | — | — |
| `CatalOzerDoganYetismisoglu2025` | TW | drinfeld doubles twitss.pdf (journal version) | PDF title page | — | — |
| `DereliDogan2020` | MC | metric-connection.pdf (arXiv v1, 10 Jun 2020) | PDF title page | — | — |
| `DereliDogan2023` | ADM | admissible.pdf (journal version) | PDF title page | — | — |
| `GrabowskiMarmo2001` | Grabowski-Marmo | —  | Uchino (2002) ref. [3] (no local PDF) | issue, doi | — |
| `KosmannSchwarzbach2004` | Kosmann-Schwarzbach | —  | Çatal-Özer et al. (2025) ref. [67]; Çatal-Özer et al. (2024) ref. [90] (no local PDF) | issue, last page, doi | AMBIGUOUS: the code cites 'Kosmann-Schwarzbach 1996' (derived brackets); no local source lists a 1996 work, only this 2004 one |
| `LiuWeinsteinXu1997` | LWX | —  | Uchino (2002) ref. [2]; Dereli & Doğan (2023) ref. [28] (no local PDF) | issue, doi | — |
| `Math595Guideline` | Guideline | Math 595 -JacoPy.pdf  | PDF title page | author, date, title (taken from the file name) | — |
| `Math595Midterm2026` | Midterm | Math 595 - Midterm Spring 2026 GTU.pdf  | PDF title page | author | — |
| `Roytenberg1999` | Roytenberg | —  | Uchino (2002) ref. [4]; Dereli & Doğan (2020) ref. [20] (no local PDF) | — | — |
| `Severa2017` | Ševera | —  | Çatal-Özer et al. (2022) ref. [16] (no local PDF) | — | — |
| `Uchino2002` | Uchino | uchino.pdf (arXiv v4, 27 Apr 2002) | PDF title page | — | — |

## Open questions

- **Watamura et al., arXiv:1408.2649** — cited with the reference fields of the secondary sources (`AsakawaMurakiSasaWatamura2015`); there is no local PDF, so every section or equation number cited from it (§2.2, §3, (2.6)–(2.7)) is unverified.
- **Kosmann-Schwarzbach 1996 vs 2004** — ambiguous: `brackets/derived.py` and `proof/strategies.py` name "Kosmann-Schwarzbach 1996" for the derived-bracket theorem, but no local source lists a 1996 work, only "Derived brackets" (2004, `KosmannSchwarzbach2004`). Left as written until the intended work is confirmed.
- **Course guideline** (`Math 595 -JacoPy.pdf`) has a bibliography key (`Math595Guideline`): the PDF has no title, author or date, so the title is taken from the file name and the year is n.d.
