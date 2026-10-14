# Literature citations

JacoPy's rules and theorems cite the works they are drawn from. This
page describes how those citations are attached to the code, how each
label was checked, and which questions remain open. The bibliography
for readers is on the [bibliography page](../reference/bibliography.md).

Rules and theorems carry their source as data (`Definition.source`,
`Theorem.source`, built with `jacopy.bibliography.cite`); the engine
copies it onto each proof step, and the ASCII and LaTeX renderers print
it as an APA 7 in-text citation, for example
`(Liu et al., 1997; Uchino, 2002, Section 1, axiom [C5])`. The reference
list below is generated from `jacopy/bibliography.py` (test:
`tests/test_citations.py`).

## How labels were checked

Every label the code uses ([C1]-[C5], (L), (7.8), Definition 7.1,
Lemma 9.1, Uchino Proposition 2.2, and so on) was compared with the text
of the cited work. Quotes are kept to one short line. Each label was
given one of these statuses:

* **verified**: the number and the content match the work;
* **number corrected**: JacoPy cited the right work under the wrong
  number; the label in JacoPy was corrected;
* **work corrected**: JacoPy attributed the number to the wrong work;
  the label in JacoPy was corrected;
* **label not found**: the label JacoPy used does not occur in the work;
  JacoPy's label was corrected or replaced;
* **ambiguous**: the status cannot be decided from the text;
* **secondary source only**: the work was not consulted directly; its
  fields and the cited claims come from a secondary source;
* **other**: not a number check (wording or over-claims in JacoPy's own
  descriptions, which were corrected; file-name or style citations; and
  rules that had no label and were given a verified source).

| scope | verified | number corrected | work corrected | label not found | ambiguous | secondary source only | other | total |
|---|---|---|---|---|---|---|---|---|
| Uchino (2002), LWX, Roytenberg and other works consulted through secondary sources: generalized and Courant modules | 27 | 0 | 0 | 0 | 0 | 4 | 2 | 33 |
| Çatal-Özer, Dereli & Doğan (2022) [B]: Bourbaki modules | 30 | 1 | 0 | 1 | 0 | 2 | 0 | 34 |
| Dereli & Doğan (2020) [MC], Dereli & Doğan (2023) [ADM], B §4 and other sources: central, metric-affine, Poisson | 43 | 3 | 1 | 1 | 2 | 2 | 8 | 60 |
| Çatal-Özer, Doğan & Yetişmişoğlu (2024) [DD] and (2025) [TW]: Drinfel'd package | 36 | 8 | 2 | 2 | 3 | 2 | 1 | 54 |
| all | 136 | 12 | 3 | 4 | 5 | 10 | 11 | 181 |

## References (APA 7)

Generated from `jacopy/bibliography.py`. Fields come from the title page
of the work or, for works consulted through a secondary source, from the
reference list named in the entry's `secondary` field. A bracketed gap
marks a field that no source gives.

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

Roytenberg, D. (1999). *Courant algebroids, derived brackets and even symplectic supermanifolds* [Doctoral dissertation, University of California, Berkeley]. arXiv. https://doi.org/10.48550/arXiv.math/9910078

Ševera, P. (2017). *Letters to Alan Weinstein about Courant algebroids* (arXiv:1707.00265). arXiv. https://doi.org/10.48550/arXiv.1707.00265

Uchino, K. (2002). *Remarks on the definition of a Courant algebroid* (arXiv:math/0204010). arXiv. https://doi.org/10.48550/arXiv.math/0204010

<!-- references:end -->

## Sources of the reference fields

| key | alias | fields taken from | missing fields | caveat |
|---|---|---|---|---|
| `AsakawaMurakiSasaWatamura2015` | Watamura | Çatal-Özer et al. (2024) ref. [56]; Çatal-Özer et al. (2025) ref. [95] | issue, doi | secondary source only: equation numbers cited from it are unverified |
| `CatalOzerDereliDogan2022` | B | title page (arXiv v1, 2 Oct 2022) | — | — |
| `CatalOzerDoganYetismisoglu2024` | DD | title page (journal version) | — | — |
| `CatalOzerDoganYetismisoglu2025` | TW | title page (journal version) | — | — |
| `DereliDogan2020` | MC | title page (arXiv v1, 10 Jun 2020) | — | — |
| `DereliDogan2023` | ADM | title page (journal version) | — | — |
| `GrabowskiMarmo2001` | Grabowski-Marmo | Uchino (2002) ref. [3] | issue, doi | — |
| `KosmannSchwarzbach2004` | Kosmann-Schwarzbach | Çatal-Özer et al. (2025) ref. [67]; Çatal-Özer et al. (2024) ref. [90] | issue, last page, doi | ambiguous: the code cites "Kosmann-Schwarzbach 1996" (derived brackets); the sources consulted list only this 2004 work |
| `LiuWeinsteinXu1997` | LWX | Uchino (2002) ref. [2]; Dereli & Doğan (2023) ref. [28] | issue, doi | — |
| `Roytenberg1999` | Roytenberg | Uchino (2002) ref. [4]; Dereli & Doğan (2020) ref. [20] | — | — |
| `Severa2017` | Ševera | Çatal-Özer et al. (2022) ref. [16] | — | — |
| `Uchino2002` | Uchino | title page (arXiv v4, 27 Apr 2002) | — | — |

## Open questions

- **Watamura et al., arXiv:1408.2649.** Cited with the reference fields
  of the secondary sources (`AsakawaMurakiSasaWatamura2015`). The work
  was not consulted directly, so every section or equation number cited
  from it (§2.2, §3, (2.6)-(2.7)) is unverified.
- **Kosmann-Schwarzbach 1996 or 2004.** `brackets/derived.py` and
  `proof/strategies.py` name "Kosmann-Schwarzbach 1996" for the
  derived-bracket theorem, but the sources consulted list only
  "Derived brackets" (2004, `KosmannSchwarzbach2004`). The citation is
  left as written until the intended work is confirmed.
