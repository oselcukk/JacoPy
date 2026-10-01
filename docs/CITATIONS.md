# Literature citations — verification table and bibliography

Every paper label the code uses ([C1]–[C5], (L), (7.8), Definition 7.1, Lemma 9.1, Uchino Proposition 2.2, …) was checked against the local PDF of the paper (pdftotext text; page images where a sign was unclear). Quotes are kept to one short line; the PDFs themselves are not in git (`.gitignore`), so the page numbers below refer to the local copies listed in the bibliography.

Rules and theorems carry their source as data (`Definition.source`, `Theorem.source`, built with `jacopy.bibliography.cite`); the engine copies it onto each proof step and the ASCII/LaTeX renderers print it as an APA 7 in-text citation, e.g. `(Liu et al., 1997; Uchino, 2002, Section 1, axiom [C5])`. The reference list below is generated from `jacopy/bibliography.py` (test: `tests/test_citations.py`).

`diğer` = rows that are not a paper-number check: wording/over-claim errors (fixed), file-name/style citations, and rules that had no label and were newly given a verified source.

Status legend: DOĞRU (number and content match), YANLIŞ NUMARA (right paper, wrong number — fixed), YANLIŞ MAKALE (number belongs to another paper — fixed), PDF'TE YOK (label does not exist in the paper — fixed/re-labelled), BELİRSİZ (cannot be decided from the text), PDF YOK (ikincil kaynak) (no local PDF; fields/claims only from a secondary source).

## Summary

| lane | scope | DOĞRU | YANLIŞ NUMARA | YANLIŞ MAKALE | PDF'TE YOK | BELİRSİZ | PDF YOK (ikincil kaynak) | diğer | total |
|---|---|---|---|---|---|---|---|---|---|
| A | Uchino (2002), LWX, Roytenberg and other works without a local PDF — generalized/Courant modules | 27 | 0 | 0 | 0 | 0 | 4 | 2 | 33 |
| B | Çatal-Özer, Dereli & Doğan (2022) [B] — Bourbaki modules; "E6 paper" | 30 | 1 | 0 | 1 | 0 | 2 | 0 | 34 |
| C | Dereli & Doğan (2020) [MC], Dereli & Doğan (2023) [ADM], B §4, Math 595 midterm — central, metric-affine, Poisson | 43 | 3 | 1 | 1 | 2 | 2 | 8 | 60 |
| D | Çatal-Özer, Doğan & Yetişmişoğlu (2024) [DD] and (2025) [TW] — Drinfel'd package | 36 | 8 | 2 | 2 | 3 | 2 | 1 | 54 |
| all | | 136 | 12 | 3 | 4 | 5 | 10 | 11 | 181 |

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

## Open questions (owner decisions, 2026-10-01)

- **"E6 paper"** — AÇIK: kaynak bulunacak (Oğuzhan, 2026-10-01). Every mention in the code stays marked as an unidentified source that is not in the repository; its equation numbers (4.10)–(4.15) are unverified and are NOT those of arXiv:2409.11973. No bibliography key until the paper is identified.
- **Watamura et al., arXiv:1408.2649** — cited with the reference fields of the secondary sources (`AsakawaMurakiSasaWatamura2015`); no local PDF, so every section/equation number cited from it (§2.2, §3, (2.6)–(2.7)) is unverified.
- **Kosmann-Schwarzbach 1996 vs 2004** — BELİRSİZ: `brackets/derived.py` and `proof/strategies.py` name "Kosmann-Schwarzbach 1996" for the derived-bracket theorem; no local source lists a 1996 work, only "Derived brackets" (2004, `KosmannSchwarzbach2004`). Left as written until the intended work is confirmed.
- **Course guideline** (`Math 595 -JacoPy.pdf`) has a bibliography key (`Math595Guideline`): the PDF has no title, author or date, so the title is taken from the file name and the year is n.d.

## Lane A — Uchino (2002), LWX, Roytenberg and other works without a local PDF — generalized/Courant modules

| # | label (as in code) | code locations | paper key, PDF page, quote (≤15 words) | status | fix applied |
|---|---|---|---|---|---|
| 1 | LWX definition, axioms [C1]–[C5], D = ½β⁻¹ρ*d | courant_axioms.py:2-12, 190-212, 616-627; standard_courant.py:19, 427-431 | Uchino2002 p.1 §1 "Definition of a Courant algebroid [2]" … [C1]…[C5]; LWX = his ref. [2] | DOĞRU (LWX itself: PDF YOK (ikincil kaynak)) | source on CourantInvarianceDeclaration = (U "Section 1, axiom [C5]", LWX); docstring says the axioms are quoted in U §1 from ref. [2] |
| 2 | [C5] ρ(x)(y,z) = ([x,y]+D(x,y),z) + (y,[x,z]+D(x,z)) | courant_axioms.py:190-235 (rule name kept) | U p.1 "[C5] ρ(x)(y,z) = ([x,y] + D(x,y), z) + (y, [x,z] + D(x,z))" | DOĞRU | `source` added (row 1) |
| 3 | (L) D(fg) = fD(g) + gD(f) | courant_axioms.py:9-12, 135-160 (DLeibnizDefinition), from_axioms strings | U p.2 §2 "(L) D(fg) = fD(g) + gD(f)"; **(L) is Uchino's OWN label** (§1 end: "the Leibniz rule for D, (L) below"); not an LWX axiom | DOĞRU | `source = cite("Uchino2002", "Section 2, Leibniz rule (L)")`; docstring notes the label is Uchino's |
| 4 | skew-symmetric bracket is part of the LWX data | courant_axioms.py:18-20, 335-350 (SkewSwapCompositeDefinition); standard_courant.py:300-321 | U p.1 "a skew-symmetric bracket [ , ] on ΓE" | DOĞRU | source (U "Section 1, definition of a Courant algebroid", LWX) on the rule and on prove_courant_skew_std |
| 5 | Prop 2.1(i) = [C3] [x,fy] = f[x,y] + ρ(x)(f)y − (x,y)Df | courant_axioms.py:689-910 (prove_left_leibniz_c3), 238-262 (C3IdentityDeclaration); standard_courant.py:337-394 | U p.2 "Proposition 2.1. (i) [x, fy] = f[x,y] + ρ(x)(f)y − (x,y)Df" | DOĞRU | Theorem source U "Proposition 2.1(i)"; C3IdentityDeclaration source (Prop 2.1(i), Remark 2.1); notes "uchino.pdf" → "Uchino (2002)" |
| 6 | Prop 2.1(ii) = [C4] ρ∘D = 0 from [C2] + (i) | courant_axioms.py:950-1060 (prove_anchor_annihilates_d); 455-512 (DDZeroDefinition); 516-563 (_dd_zero_theorem) | U p.2 "(ii) ρ ∘ D = 0"; proof "By [C2] we have …" | DOĞRU | sources added (theorem; DDZero rule and record = Prop 2.1(ii) + Prop 2.2) |
| 7 | [C4] "(Df,Dg) = 0" (rule name "cite [C4] theorem … (Da,Db) = 0") | courant_axioms.py:455-480 | U p.1 "[C4] ρ ∘ D = 0, i.e., (Df, Dg) = 0" | DOĞRU | — |
| 8 | Prop 2.2 (Df,y) = ½ρ(y)(f), via ρ(fx)(y,y) | courant_axioms.py:24-25, 392-450 (DPairingUnfoldDefinition), 1065-1267 (prove_d_pairing_formula) | U p.2 "Proposition 2.2. (Df, y) = ½ρ(y)(f)"; proof "ρ(fx)(y,y) = …" | DOĞRU | sources added (rule + theorem) |
| 9 | Remark 1 (Df,x) = ½ρ(x)f normalisation | standard_courant.py:16-17, 64-68, 266-285; poisson_generalized.py:13-15, 650-688 | U p.1 "Remark 1. D = ½β⁻¹ρ*d is equivalent to (Df, x) = ½ρ(x)f" | DOĞRU | source U "Remark 1" on prove_courant_dorfman_relation and prove_theta_d_pairing_value |
| 10 | Remark 2.1 (i) ⇒ (L) | courant_axioms.py:254-256, 1362-1486 | U p.3 "Remark 2.1. Conversely, the Leibniz rule (L) can be derived from Proposition 1(i)." | DOĞRU (paper itself writes "Proposition 1(i)" for 2.1(i)) | source U "Remark 2.1" |
| 11 | Remark 2.2: (A), [C2] ⟺ [x,Df] = D(x,Df); "(A) is loose" | courant_axioms.py:1497-1790 (prove_bracket_with_d) | U p.3 "(A) ρ(x)ρ(y)(f) = ρ(x∘y)(f) + ρ(y)ρ(x)(f) + 2([x,Df] − D(x,Df), y)" | DOĞRU ("loose" defensible: p.3 line "ρ(y)ρ(x)(f) − ρ(y)ρ(x)(f)" is garbled) | source U "Remark 2.2" (+ Roytenberg1999 when classical=True) |
| 12 | "[x,Df] = D((x,Df)) [Roytenberg]" | courant_axioms.py:1503-1504 | U p.3 "a Courant algebroid has the property [x, Df] = D(x, Df) ([4], [5])"; [4] = Roytenberg thesis, [5] = Roytenberg–Weinstein 1998 | PDF YOK (ikincil kaynak) — confirmed via U refs [4],[5] | docstring → "[Roytenberg 1999 / Roytenberg-Weinstein 1998, Uchino refs. [4], [5]]" |
| 13 | Remark 2.3 alternative definition [C'1]–[C'5]; "derived … in a similar way" (no proof) | dorfman_axioms.py:1-30, 66-110, 340-380; standard_courant.py:9-14, 146-238; twisted_courant.py:13-21; poisson_generalized.py:24-40; dialect_bridge.py:7, 20 | U p.3-4 "Alternative definition of a Courant algebroid [4]"; "are also derived from the rest of the axioms and condition (L) in a similar way" | DOĞRU (definition originally Roytenberg [4]: PDF YOK (ikincil kaynak)) | source U "Remark 2.3" on both dorfman_axioms theorems; standard [C'2]/[C'5] theorems cite U "Remark 2.3, axiom [C'2]/[C'5]" |
| 14 | Grabowski–Marmo: [C2] redundant for Lie algebroids | dorfman_axioms.py:128-131, 352-356 | U p.3 Rem 2.2 "Grabowski and Marmo showed that a homomorphism property of ρ … follows" ([3]) | PDF YOK (ikincil kaynak) — confirmed via U Remark 2.2 | docstring "Uchino Remark 2.2 cites their Lie-algebroid result (his ref. [3])" |
| 15 | T(x,y,z) = ⅓Σcyc ([x,y],z) (LWX Jacobi defect) | standard_courant.py:417-420, 437-447 | U p.1 "T(x,y,z) = ⅓(([x,y],z) + ([y,z],x) + ([z,x],y))" | DOĞRU | docstring "(Uchino Section 1, after [C5])" |
| 16 | x∘y := [x,y] + D(x,y), i.e. Courant = Dorfman − D⟨x,y⟩ | standard_courant.py:255-285 | U p.3 Rem 2.2 "where x ∘ y := [x, y] + D(x, y)" | DOĞRU | source (U Remark 1, U Remark 2.2); docstring notes it |
| 17 | MC Def 3.1 E-metric symmetric, non-degenerate | courant_axioms.py:15-17 | MC p.6 "Definition 3.1. A (0,2)-type E-tensor is called an E-metric if it is symmetric and non-degenerate" | DOĞRU | — |
| 18 | [B 4.10] metric invariance | courant_axioms.py:216; dorfman_axioms.py:14 | B p.7 (4.10) "ρE(u)(g(v,w)) = g([u,v]E, w) + g(v, [u,w]E)" | DOĞRU | "[B 4.10]" → "[B Eq. (4.10)]" |
| 19 | [B 4.11] tactic (right-Leibniz from invariance + non-degeneracy) | courant_axioms.py:34-36; dorfman_axioms.py:15, 76, 99 | B p.7 (4.11) "[u,fv]E = f[u,v]E + ρE(u)(f)v"; "follows from the metric invariance property and the non-degeneracy" | DOĞRU (the "two-leg tactic" itself is the code's own name) | "[B 4.11]" → "[B Eq. (4.11)]"; courant_axioms docstring spells out what (4.11) is; source B "Eq. (4.11)" on prove_dorfman_c3_redundant |
| 20 | B (4.2): Dorfman properties (anchor morphism, invariance …) | standard_courant.py (new sources only) | B p.6 (4.2) "proj1(u)(gS(v,w)) = gS([u,v]D, w) + gS(v,[u,w]D)" and "proj1([u,v]D) = [proj1(u), proj1(v)]" | DOĞRU | source B "Eq. (4.2)" added on prove_anchor_morphism_std and prove_dorfman_invariance_std |
| 21 | "Roytenberg (5.2)", "eq (5.2)" — 8-component Roytenberg bracket | roytenberg_courant.py:4-5, 140, 206, 259, 328 | TW PDF p.18 §5 (5.2) "[U+ω, V+η]E = [U,V]A + L̃ωV + K̃ηU + R(ω,η) ⊕ …" "which we refer to as Roytenberg bracket" | DOĞRU, but bare in a module that also cites Watamura → was BELİRSİZ | → "Roytenberg bracket [TW (5.2)]"; sources TW "Eq. (5.2)" on the three identification theorems |
| 22 | "decomposition (5.4)" (twisted Dorfman part) | roytenberg_courant.py:143, 262 | TW §5 (5.4) "[U+ω,V+η]^H_Dor = [U,V]A ⊕ LUη + KVω + H(U,V)" | DOĞRU (bare → BELİRSİZ) | → "TW decomposition (5.4)"; source TW "Eq. (5.4)" |
| 23 | "decomposition (5.5) at p = 1" (twisted tilde-Dorfman part) | roytenberg_courant.py:211 | TW §5 (5.5) "[U+ω,V+η]^R_f̃Dor = L̃ωV + K̃ηU + R(ω,η) ⊕ [ω,η]Z" | DOĞRU (bare → BELİRSİZ) | → "TW decomposition (5.5)"; source TW "Eq. (5.5)" |
| 24 | "eq (7.25)" derived R′-twist vanishes under the Poisson condition | r_twisted.py:910-912, 933-940 | TW PDF p.33 (printed p.31) (7.25) "R′(ω,η) = [Πω,Πη]A − Π[ω,η]′Z"; p.32 "the R′-twist vanishes due to the Nambu-Poisson condition" | DOĞRU (bare → BELİRSİZ) | → "[TW (7.25), arXiv 2409.11973]" + quote; source TW "Eq. (7.25) and the remark after it" |
| 25 | general Ψ-twist [u,v]′ = Ψ⁻¹[Ψu,Ψv] (directive 13j "follow Section 7 of twist paper") | general_twist.py:1-34, 155 | TW PDF p.29 §7 (7.3) "[u,v]Roy′ = Ψ⁻¹[Ψu, Ψv]Roy" | DOĞRU (added reference) | docstring now names TW Eq. (7.3); no theorem source (the transport theorems are not stated in TW) |
| 26 | "(6.11)" symmetric part [u,v]+[v,u] = 𝔻g(u,v) (R-valued) | general_twist.py:584-656 (6 occurrences, incl. one step `rule` string and from_axioms) | B p.12 Def 6.2 (6.11) "[u,v]E + [v,u]E = Dg(u,v)" | DOĞRU (bare → BELİRSİZ) | → "B (6.11)" |
| 27 | "(7.8)" R-valued metric invariance with ℒ^R | general_twist.py:680-760 (6 occurrences, incl. one step `rule` string and from_axioms) | B p.14 (7.8) "L^R_ρE(u)(g(v,w)) = g([u,v]E, w) + g(v, [u,w]E)" | DOĞRU (bare → BELİRSİZ) | → "B (7.8)" |
| 28 | "(7.2) right-Leibniz" (cited-rule example) | _cited_rule.py:4-5 | B p.13 (7.2): invariance ⇒ right-Leibniz computation "ρE(u)(g(fv,w)) = …" | DOĞRU (bare → BELİRSİZ) | → "the right-Leibniz of B Eq. (7.2)" |
| 29 | Watamura et al. 1408.2649 §2.2, (2.6) anchor θ♯ω, (2.7) bracket; §2, §3 (R-flux, d_θR = 0) | poisson_generalized.py:2-19, 108, 138, 149, 306, 345, 364, 397, 416, 640, 906; r_twisted.py:2-3, 22, 401, 505, 680, 753, 763, 888, 895, 912; roytenberg_courant.py:14-16, 167, 211; dialect_bridge.py:7, 20 | no local PDF; TW mentions "Poisson generalized geometry in [95, 104]", only general content | PDF YOK (ikincil kaynak) — labels (2.6)/(2.7)/§2.2/§3 UNVERIFIABLE | docstrings now say "no local PDF; the labels are unverified here"; no `source` added (RFluxClosureDeclaration stays source=None) |
| 30 | Ševera: H = dB B-transform; twisted Courant ⟺ dH = 0; "R-side Ševera theorem" | twisted_courant.py:22-25, 316-320, 361-365; r_twisted.py:30, 432, 680, 851; roytenberg_courant.py:239 | B p.7 after (4.12): "Ševera's classical result [16] … classify all exact Courant algebroids by the third de Rham cohomology" | PDF YOK (ikincil kaynak); "R-side Ševera" is the code's own analogy name | twisted_courant docstring points to Ševera 2017 + B §4 text; no source |
| 31 | "uchino.pdf" file-name citations | courant_axioms.py:3, notes ×5; dorfman_axioms.py:3, notes ×2; standard_courant.py notes; __init__.py:4 | — | (style) | all → "Uchino 2002, arXiv:math/0204010" / "Uchino (2002) …" |
| 32 | "PDF item 14x / PDF 13j / PDF 14g …" (project directive yönerge, not a paper) | all owned modules (≈35 occurrences) | yonerge.txt items 13j, 14a-h | n/a (not a literature citation) | → "project directive item …" / "directive …" (no test asserts these strings) |
| 33 | "[C'1]" Leibniz–Jacobi label for the Watamura double | dialect_bridge.py:7, 20, 285 | U p.3 "[C'1] x∘(y∘z) = (x∘y)∘z + y∘(x∘z)" | DOĞRU | — |

### Notes
- Uchino internal inconsistency (not ours): the proofs on p.2-3 call Prop 2.1 "Proposition 1" and Prop 2.2 "Proposition 2" (e.g. "We apply Proposition 1 (i)", "by [C5] and Proposition 2"). Our code uses the numbered headers 2.1/2.2 — correct.
- Uchino's Courant definition is unnumbered; locators used: "Section 1, axiom [Cn]", "Section 1, definition of a Courant algebroid", "Section 2, Leibniz rule (L)".
- H-twist convention (no citation in code, for information): B Eq. (4.15) writes the twist as ι_U ι_V H, the code (twisted_courant / drinfeld.twist.dorfman_double_h) uses ι_V ι_U H — opposite sign under the usual ι_U ι_V H = H(V,U,·) reading, i.e. H ↔ −H. The code does not cite B (4.15), so no fix; do not add a B (4.15) source without settling the sign convention.
- Watamura (2.6)/(2.7)/§2.2/§3 remain unverifiable (no PDF). The whole 7.B.2b/c structure depends on them (prior audit M8-9).

### Bibliography issues (jacopy/bibliography.py — not edited, owner/lead to fix)
- AsakawaMurakiSasaWatamura2015.secondary says "Çatal-Özer et al. (2025) ref. [56]; Çatal-Özer et al. (2024) ref. [95]" — SWAPPED: TW (2025) ref. **[95]** (drinfeld doubles twitss.txt:2848) and DD (2024) ref. **[56]** (drinfeld_double.txt:3289, with arXiv:1408.2649, IJMPA 30 (2015) 1550097).
- KosmannSchwarzbach2004.secondary says "Çatal-Özer et al. (2025) ref. [90]" — WRONG: TW (2025) ref. [90] is Costa–Petalidou; "Derived brackets" is TW ref. **[67]** (twitss.txt:2780) and DD (2024) ref. **[90]** (drinfeld_double.txt:3376).

### ROADMAP.md fixes I would make (not edited)
- :1347 "| `uchino.pdf` | Uchino, math/0204010 …" → keep the file column but cite as "Uchino (2002), arXiv:math/0204010" in prose.
- :1951 "(1 adım; eq 7.25 p=1 — …)" → "(1 adım; TW (7.25) p=1 — …)"
- :1952-1953 "PDF 14g): `roytenberg_courant.py` — (5.2) Roytenberg'in" → "yönerge 14g): `roytenberg_courant.py` — TW (5.2) Roytenberg'in"
- :2080 "**Uchino hedefleri (2026-07-31, `uchino.pdf` okundu):**" → "**Uchino hedefleri (2026-07-31, Uchino 2002 / math/0204010 okundu):**"
- :2097 "Twisted paper §5.30-5.39 … (5.33-5.37)" → "TW Eqs. (5.30)–(5.39) … (5.33)–(5.37)" (equations, not sections; TW lane to verify the numbers)

### For the owner (Oğuzhan) to decide
1. Watamura 1408.2649: add the PDF to the repo (or accept the labels as unverified); until then no `source` is attached to Watamura-based rules (RFluxClosureDeclaration, the θ-double suite).
2. Should "directive item 14x" strings (the yönerge PDF) get their own bibliography entry (e.g. key `JacoPyDirective2026`) so they can carry structured sources too? Currently they are plain text.
3. Fix the two bibliography secondary-reference numbers above.

## Lane B — Çatal-Özer, Dereli & Doğan (2022) [B] — Bourbaki modules; "E6 paper"

| # | label (as in code) | code locations | paper key, PDF page, quote | status | fix applied |
|---|---|---|---|---|---|
| 1 | R-valued E-metric (symmetric, C∞-bilinear, non-degenerate), "Def 6.2" | gen/bourbaki_structure.py:67 (BMetric), 154-199 | B p5 §3: "R-valued E-metric is defined as a symmetric, non-degenerate, C∞-bilinear map"; p14 Def 6.2 uses it | DOĞRU | `source` §3 on bilinearity + symmetry rules |
| 2 | (6.8) 𝔻(f·r) = f𝔻r + 𝕃_df r | gen/bourbaki_structure.py:10, 89, 213, 487 | B p13 (6.8) "D(f r) = f Dr + Ldf r" | DOĞRU | `source` Eq. (6.8); 𝕃 linearity: "Section 6, text after Eq. (6.8)" |
| 3 | (6.11) symmetric part [u,v]+[v,u] = 𝔻g(u,v) | gen/bourbaki_structure.py:25, 701-813; gen/bourbaki_exact.py:261-275, 620; gen/bourbaki_severa.py:292-296, 477, 725 | B p14 Def 6.2 (6.11) "[u, v]E + [v, u]E = Dg(u, v)" | DOĞRU | `source` Definition 6.2, Eq. (6.11) on both declarations |
| 4 | Corollary 6.1, L(df,u,v) = 𝕃_df g(u,v) | gen/bourbaki_structure.py:16, 423-490 | B p14 Cor 6.1 (6.12) "L(ω, u, v) = Lω (g(u, v))" | DOĞRU | Theorem source=Corollary 6.1, Eq. (6.12); notes .pdf→arXiv |
| 5 | Prop 6.1 / "(7.9) route" for left-Leibniz (M8-8) | gen/bourbaki_structure.py:831-841 | B p12-13 Prop 6.1 (2⟹1) proves left-Leibniz; p16 (7.9) "as the left-Leibniz rule is also satisfied" = uses it | YANLIŞ NUMARA (only "(7.9)") | notes → "Proposition 6.1 (2 ⟹ 1) route; Eq. (7.9) USES the left-Leibniz rule…"; source=(Prop 6.1 (2⟹1), Cor 6.1); same source on LeftLeibnizTheoremRule (severa) |
| 6 | (7.2) right-Leibniz from R-valued invariance | gen/bourbaki_structure.py:20, 548-670; gen/bourbaki_severa.py:18, 121-155, 603 | B p15 (7.2) + "the metric invariance property (7.1) implies the right-Leibniz rule" | DOĞRU | source "Section 7, discussion around Eq. (7.2)" on Theorem + RightLeibnizTheoremRule |
| 7 | "B 4.11" tactic | gen/bourbaki_structure.py:20, 557, 657; tests/test_generalized_bourbaki_structure.py:3, 40 | B p8 (4.11) first line "[u, f v]E = f [u, v]E + ρE (u)(f )v" + "follows from the metric invariance" | DOĞRU (format) | "B 4.11" → "B (4.11)" (docstrings, one statement string, test comments) |
| 8 | (7.3) derivation law with anchor symbol | gen/bourbaki_structure.py:12, 125, 284-298, 580, 653 | B p15 (7.3) "D(f r) = f Dr + VD (f )r"; anchor symbol: Def 7.1 "ρD(R) LR = ρE" / (7.5) | DOĞRU | source=(Eq. (7.3), Definition 7.1) |
| 9 | (7.8) metric invariance, Def 7.1 | gen/bourbaki_structure.py:21, 332-348; gen/bourbaki_exact.py:404, 466, 605-619, 660-664; gen/bourbaki_severa.py:131, 512, 570; gen/bourbaki_precalculus.py:30, 571 | B p16 Def 7.1 (7.8) "LR ρE (u) (g(v, w)) = g([u, v]E , w) + g(v, [u, w]E )" | DOĞRU | source Definition 7.1, Eq. (7.8) |
| 10 | Def 7.1 almost-metric-Bourbaki data | gen/bourbaki_structure.py:125, 373; gen/bourbaki_exact.py:404; gen/bourbaki_severa.py:131, 150 | B p15 Def 7.1 "octet … almost-metric-Bourbaki algebroid" | DOĞRU | — |
| 11 | (8.3) 𝔻 = χ∘d, 𝕃 = χ∘l | gen/bourbaki_exact.py:7, 299-306; gen/bourbaki_severa.py:269-276, 640, 726 | B p17 (8.3) "D = χd, Lω η = χ(ω ∧ η)" (higher Courant); Def 8.1 "D = χd, L = χl" | DOĞRU | source=(Eq. (8.3), Definition 8.1) |
| 12 | (8.5) exactness ρχ = 0, ρφ = id; Def 8.1 | gen/bourbaki_exact.py:6, 121-140, 228, 516; tests/test_generalized_bourbaki_exact.py:105 | B p17 Def 8.1 (8.5) "0 → Z → E → T(M) → 0"; splitting "ρE φ = idT(M)" | DOĞRU | SplitAnchorDefinition source=(Def 8.1 Eq. (8.5), §8 splitting) |
| 13 | (9.7) definition of ℒ^Z | gen/bourbaki_exact.py:8, 169-205, 568; gen/bourbaki_severa.py:14 | B p18 (9.7) "χLZ V z = [φ(V ), χ(z)]E" | DOĞRU | LieZDefinitionRule source=(Eq. (9.7), Lemma 9.1) |
| 14 | (9.9) definition of ι | gen/bourbaki_exact.py:9, 318-322 | B p18 (9.9) "ιV z := g(χ(z), φ(V ))" | DOĞRU | source Eq. (9.9) |
| 15 | Lemma 9.1 [u,χz] ∈ im χ | gen/bourbaki_exact.py:15-18, 169-205, 225-250, 514-560 | B p18 Lemma 9.1 "[u, χ(z)]E and [χ(z), u)]E are in the image of χ" | DOĞRU (wording fixed) | Code said "Lemma 9.1 only gives ρ(…) = 0"; the paper's lemma concludes im χ (exactness is its hypothesis). Docstrings reworded: the MECHANIZED lemma proves ρ(…) = 0, the paper uses ker ρ = im χ. Theorem sources added |
| 16 | g-isotropy of χ: g(χz,u) = ι_ρ(u) z | gen/bourbaki_exact.py:349 (IsotropyDeclaration) | B p19 Prop 9.1 proof "g-isotropy of χ implies g(χ(z), u) = ιρE (u) z" | DOĞRU | source "Proposition 9.1, proof (g-isotropy of χ)" |
| 17 | ℒ^R in a ρχ = 0 direction vanishes | gen/bourbaki_exact.py:404 rule | B p19 Prop 9.1 proof "By exactness and the R-linearity of LR, the left-hand side … vanishes" | DOĞRU | source Prop 9.1 proof |
| 18 | Prop 9.1 (9.11) ⟹ (9.15) form, instance (χz,φU,φV) | gen/bourbaki_exact.py:20-25, 640-680 | B p19 (9.11), proof "u = χ(z), v = φ(U ), w = φ(V )" | DOĞRU | source Proposition 9.1, Eq. (9.11); notes → arXiv |
| 19 | Prop 9.1 (9.12) ⟹ (9.14), isotropic χ, (φU,φV,χz) | gen/bourbaki_exact.py:26-28, 685-725 | B p19 (9.12) "Furthermore if the map χ is g-isotropic" | DOĞRU | source Proposition 9.1, Eq. (9.12) |
| 20 | Def 9.1 quintet: ι C∞-bilinear, d symbol l, ℒ^R ℝ-bilinear, ℒ^Z laws (1)-(2) | gen/bourbaki_precalculus.py:6-20, 172, 260-300, 336; tests/test_generalized_bourbaki.py:2, 74 | B p19-20 Def 9.1 "LR : … is an R-bilinear map"; "LZ f V z = f LZ V z + ldf ιV z" | DOĞRU | `source` Definition 9.1 on 6 rules ("l C∞-bilinearity": Def 9.1 + symbol map Eq. (6.10)) |
| 21 | (9.14) | gen/bourbaki_precalculus.py:19, 377-392, 595-596, 657-664 | B p20 (9.14) "LR U ιV z = ι[U,V ] z + ιV LZ U z" | DOĞRU | Axiom914Declaration source Definition 9.1, Eq. (9.14) |
| 22 | (9.15) | gen/bourbaki_precalculus.py:20, 411, 633, 665 | B p20 (9.15) "ιU (LZ V z − dιV z) = −ιV (LZ U z − dιU z)" | DOĞRU | — (hand-built cite step; no rule object) |
| 23 | Thm 9.1, (9.17)/(9.18), checks 1-2 | gen/bourbaki_precalculus.py:22-31, 481-680 | B p20 Thm 9.1; (9.17) "[U + z, V + y]S := [U, V ] + LZ U y − LZ V z + dιV z"; (9.18) "gS … := ιU y + ιV z" | DOĞRU | Theorem sources "Theorem 9.1 … proof check 1/2"; notes → arXiv |
| 24 | Def 9.2 remark: Cartan calculus is a pre-calculus; (2.10) | gen/bourbaki_precalculus.py:31-35, 690-746 | B p20 "The usual Cartan calculus (ι, d, L) is a Bourbaki pre-calculus"; p5 (2.10) "Lf V ω = f LV ω + df ∧ ιV ω" | DOĞRU | — (provers return chains, no Theorem) |
| 25 | Thm 9.2 (9.19)-(9.21) and 4 legs | gen/bourbaki_severa.py:2-22, 455-680 | B p21-22 Thm 9.2 + proof "[χ(z), φ(V )]E = χ(−LZ V z + dιV z)", "[χ(z), χ(y)]E = 0", (9.21) | DOĞRU | sources "Theorem 9.2, proof" / "Theorem 9.2, Eq. (9.21) and proof" on 5 theorems |
| 26 | Cor 9.1 (isotropic φ ⟹ F = 0, H a 2-form; Δ+Δ = χ dF) | gen/bourbaki_severa.py:22-26, 356 (PhiIsotropyDeclaration), 700-760 | B p22 Cor 9.1 "if there is a g-isotropic splitting φ, then F = 0"; proof "H(U, V ) + H(V, U ) = dg(φ(U ), φ(V ))" | DOĞRU | source Corollary 9.1 (theorem + declaration) |
| 27 | §6-7, §8-9, §9 section cites | gen/bourbaki_structure.py:3; gen/bourbaki_exact.py:3; gen/bourbaki_severa.py:3-5 | B p11 §6, p13 §7, p16 §8 "Exact Bourbaki Algebroids", p17 §9 "Bourbaki Pre-Calculus" | DOĞRU | "primary paper §…" now names authors + arXiv |
| 28 | BC1–BC9 "Bourbaki pre-calculus axiom sheet" (M8-3) | tests/test_algebroid_calculus.py:8-13 (+ BC5-BC9 in test docstrings 118-232, not owned) | B p17 fn 13 "We lied; we will never define a calculus in this paper"; no "BC" label; no Theorem 9.3 | PDF'TE YOK (labels); BC4 content DOĞRU (Def 9.1 law 2) | module docstring rewritten: project-internal numbering from literatur2.pdf, not in the paper |
| 29 | MC Prop 4.2 (unique projector; proof fixes (0,ω)) | gen/exact_locality_projector.py:3, 47, 230, 262-281, 393, 461, 516; tests/test_exact_locality_projector.py:1 | MC p24 Prop 4.2 "there is a unique locality projector P given by the projection onto ker(ρ)" | DOĞRU | source=MC "Proposition 4.2, proof" on the ker ρ theorem only (other three theorems are the code's own finding: no source) |
| 30 | MC Def 3.10 locality projector | gen/exact_locality_projector.py:29, 147 | MC p12 Def 3.10 "L̂ := P ◦ L ∈ [L̃] … such that im(L̂) ⊂ ker(ρ)" | DOĞRU | ProjectorAbsorbsExactFormsDefinition source=(MC Def 3.10, MC Prop 4.1 Eq. (4.3)) |
| 31 | MC Prop 4.1 L(Df,u,v) = g(u,v)·Df | gen/exact_locality_projector.py:147-148 | MC p22 (4.3) "L(Ω, u, v) := g(u, v)g −1 (Ω)" | DOĞRU (formula dropped g⁻¹) | docstring → "g(u, v)·g⁻¹(Df) [MC Prop 4.1, Eq. (4.3)]" |
| 32 | "the admissible-paper Def 3.8" | gen/exact_locality_projector.py:30 | ADM p8 Def 3.8 item 2 "P restricted to ker ρ = id" | DOĞRU | → "[ADM Def 3.8] (DereliDogan2023, …)" |
| 33 | Watamura (2.6) anchor ρ(U+ω) = θ♯ω; "Watamura components" | gen/frame_evaluation.py:21, 265, 295, 314 | AsakawaMurakiSasaWatamura2015, arXiv:1408.2649 — no PDF | PDF YOK (ikincil kaynak) | bare "(2.6)" → "[Watamura (2.6)]"; module note + notes string "arXiv:1408.2649 — no PDF, unverified"; no `source` (unverified) |
| 34 | "E6 paper" (4.10)-(4.15): twist Ψ_Π, (4.11) inverse, (4.13) components, (4.14) ⊛ = ½Π₃∘ι_{Π₃} | gen/exceptional_rotation.py:4, 21, 58, 203-213, 233, 257-266; gen/exceptional_double.py:5, 65, 116-117, 344-345, 405; gen/frame_evaluation.py:309-420 | unidentified; not in the repository. Cross-check: TW (4.13) "Kf U ω = f KU ω", DD (4.13) symmetric part — neither is ⊛ | PDF YOK (unidentified source) | Module "Citation note" in all 3 files; every "E6 paper"/bare (4.1x) now says unidentified source, not in the repository, unverified, not TW numbers; runtime `notes`/statement strings updated; no `source` |

### Notes
- Bare (6.x)–(9.x) in the four bourbaki_* modules are all B numbers (modules cite only B); each module docstring now states the paper (authors + arXiv) and that bare numbers are its.
- Paper-internal slips (not code errors, for information): Prop 9.1 says "U, V ∈ C∞(M,R)" (should be X(M)); its proof calls the invariance "(7.9)" and the symmetric part "(7.8)" (the definitions are (7.8) and (7.7)). The code uses the definitional labels (7.8)/(6.11), which is right.
- `notes` strings "pre-metric-bourbaki.pdf …" → "arXiv:2210.00548 …" everywhere in my files (12 strings).
- `_cited_zero_proof` (bourbaki_exact) and `_zero_theorem` (bourbaki_severa) got an optional `source=None` kwarg (pure pass-through to Theorem; no behaviour change).
- Sources propagate: e.g. prove_right_leibniz chain → Def 7.1 (7.8), Eq. (7.3), §3 R-valued metric (checked with chain_sources).
- No rule `name` was changed. No test asserted text that changed.

### ROADMAP.md fixes (not edited)
- ROADMAP.md:282-284 "arXiv:2210.00548'in L1-L3, C1-C2, B1-B4, BC1-BC9 aksiyomlarının + Thm 9.1-9.3 (Ševera sınıflandırması)" → "literatur2.pdf'in kendi (makalede bulunmayan) L/C/B/BC1–BC9 numaralandırması; makalede yalnız Def 9.1 (pre-calculus), Thm 9.1, Thm 9.2, Cor 9.1 var — Theorem 9.3 ve 'Bourbaki calculus' (BC9: d²=0) yok (2210.00548 dipnot 13)".
- ROADMAP.md:294 "3.F'nin (Bourbaki calculus BC1-BC9) doğrudan hedef listesi" → "3.F'nin (literatur2 BC1–BC9 proje-içi numaralandırması; 2210.00548 Def 9.1 ile yalnız BC4 içeriği örtüşür) hedef listesi".
- ROADMAP.md:1669 (and any "E6 paper" line) → append "(kimliği belirsiz kaynak; repoda yok; numaralar doğrulanmadı; 2409.11973 numaraları değildir)".
- Any ROADMAP mention of "Prop 6.1 / (7.9)" for left-Leibniz → "Prop 6.1 (2 ⟹ 1)".

### For the owner (Oğuzhan) to decide
1. "E6 paper": identity unknown. Please supply authors/arXiv id + PDF so a bibliography key can be added; until then the numbers stay unverified and no `source` is attached.
2. Watamura (arXiv:1408.2649) has a key but no PDF: I attached no `source` (unverified locator). Add the PDF to allow `cite("AsakawaMurakiSasaWatamura2015", "Eq. (2.6)")`.
3. BC5–BC9 labels inside individual test docstrings in tests/test_algebroid_calculus.py (lines ~118-232) were left alone (only the module docstring is owned); rename or keep as internal labels?
4. exact_locality_projector: the three "finding" theorems (non-uniqueness family, B-field, witness) have no `source` because the paper does not claim them; say if you want MC Def 3.10 / ADM Def 3.8 attached as "checked against" sources.

## Lane C — Dereli & Doğan (2020) [MC], Dereli & Doğan (2023) [ADM], B §4, Math 595 midterm — central, metric-affine, Poisson

| # | label (as in code) | code locations | paper key, PDF page, quote (≤15 words) | status | fix applied |
|---|---|---|---|---|---|
| 1 | MC Def 3.1 (E-metric symmetric, (0,2)-tensor) | context.py:332,335,752; rules.py:244,320 | MC p6 "A (0, 2)-type E-tensor is called an E-metric if it is symmetric and non-degenerate" | DOĞRU | `source` on MetricBilinearity/MetricSymmetry |
| 2 | "MC Def before 3.2" (anchored bundle, ρ bundle morphism) | context.py:10 | MC p7 "ρ : E → T(M) is a vector bundle morphism over idM"; also B p6 Def 3.1 | DOĞRU (vague locator) | locator → "MC Section 3, paragraph before Definition 3.2; B Definition 3.1"; `source` on AnchorLinearity |
| 3 | MC Def 3.2 (linear E-connection) | e_connection.py:3,61 | MC p7 Def 3.2, Eq. (3.2) "∇u(fv) = ρ(u)(f)v + f∇uv" | DOĞRU | `source` on EConnectionScalarAction, Connection* rules |
| 4 | MC Def 3.3 (E-non-metricity) in e_connection header "Def 3.2-3.3, Prop 3.1-3.3" | e_connection.py:3; tests/test_e_connection.py:2 | MC p7 Def 3.3 Q := ∇g, not used in e_connection.py | YANLIŞ NUMARA (range too wide) | header → "MC Definition 3.2, Eqs. (3.8)–(3.9); … (3.19) + proof of Proposition 3.3" |
| 5 | "MC Prop 3.3" for R⁰ last-slot tensoriality ⇔ anchor morphism (M8-8) | e_connection.py:33,288; tests/test_e_connection.py:6,112,134 | MC p10 (3.19) "ρ([u,v]E) = [ρ(u),ρ(v)]"; p11 Prop 3.3 proof uses (3.19) | YANLIŞ NUMARA (partly: the content is (3.19) + the proof of Prop 3.3) | → "MC (3.19) + Proposition 3.3" |
| 6 | MC §3 / "MC Prop 3.1-3.3 territory" | e_connection.py:24,207 | MC p8 (3.8)/(3.9) define T⁰, R⁰ | BELİRSİZ | → "MC Section 3, Eqs. (3.8)–(3.9)" / "MC Definition 3.2, Eqs. (3.8)–(3.9), (3.19)" |
| 7 | MC Def 3.5 (coboundary D, Df(u)=ρ(u)f; L C∞-multilinear) | context.py:18,183,231,237; rules.py:17,20,166,192; modified.py:91,111,172; tests/test_algebroid_context.py:133, test_algebroid_locality.py:2,69 | MC p8 "D … coboundary map defined by (Df)(u) := ρ(u)(f)"; "L … C∞(M,R)-multilinear map" | DOĞRU | `source` on CoboundaryPairing, LocalityMultilinearity |
| 8 | B §4 for D_E := ρ*d | context.py:20 | B p8 (Def 4.2) "where DE := ρ∗E d"; also B p6 after Def 3.1 | DOĞRU | — (B Section 3 remark added as 2nd source of CoboundaryPairing) |
| 9 | B Def 4.1 (bracket ℝ-bilinear) | context.py:22,114; rules.py:12,120 | B p7 "[·,·]E : X(E)×X(E) → X(E) is an R-bilinear map" | DOĞRU | `source` on BracketBilinearity |
| 10 | B 4.4 / MC 3.10 right-Leibniz | declarations.py:14 | B p7 (4.4) "[u, fv]E = f[u,v]E + ρE(u)(f)v"; MC p8 (3.10) | DOĞRU | prefix "(4.4)"/"(3.10)"; `source` on RightLeibnizDeclaration |
| 11 | MC 3.11 left-Leibniz | declarations.py:16 | MC p8 (3.11) "[fu,v]E = −ρ(v)(f)u + f[u,v]E + L(Df,u,v)" | DOĞRU | `source` on LeftLeibnizDeclaration |
| 12 | B 4.5 / MC 3.19 anchor morphism | declarations.py:20 | B p7 (4.5) "ρE([u,v]E) = [ρE(u), ρE(v)]"; MC p10 (3.19) | DOĞRU | `source` on AnchorMorphismDeclaration (brief said "B (4.6)": wrong, it is (4.5)) |
| 13 | B 4.6 Leibniz-Jacobi | declarations.py:22 | B p7 (4.6) "[u,[v,w]E]E = [[u,v]E,w]E + [v,[u,w]E]E" | DOĞRU | `source` on JacobiDeclaration (+ MC (3.20)) |
| 14 | antisymmetry declaration (no label in code) | declarations.py:188 | MC p17 Def 3.15 "called an almost-Lie … if [·,·]E is anti-symmetric" | — (new) | `source` = MC Definition 3.15 |
| 15 | C1 [B 4.10] metric invariance | declarations.py:234 | B p8 (4.10) "ρE(u)(g(v,w)) = g([u,v]E,w) + g(v,[u,w]E)" | DOĞRU | `source` B Def 4.3, Eq. (4.10). MC (4.2) is NOT cited: it prints g(u,[v,w]), a typo |
| 16 | C2 [B Def 4.2-4.3] symmetric part | declarations.py:266; context.py:425,544 | B p8 (4.7)/(4.9) "[u,v]E + [v,u]E = g−1 DE g(u,v)"; MC p21 (4.1) | DOĞRU | `source` (B 4.7, B 4.9, MC 4.1) |
| 17 | [B 4.11] (metric algebroids satisfy right/left Leibniz) | theorems.py:5,469,694,701 + notes; context.py:544,546; e_koszul.py:420; tests/test_algebroid_metric.py:56,325,358 | B p8 (4.11) "[fu,v]E = f[u,v]E − ρE(v)(f)u + g(u,v)g−1DEf" | DOĞRU | written "(4.11)"; Theorem `source`s |
| 18 | "B Thm 4.1" / "Bourbaki Thm 4.1 route" (M8-5/M2-4) | theorems.py:18,398 (runtime notes); tests/test_algebroid_theorems.py:4 | B p7 "Leibniz-Jacobi identity (4.6) and the right-Leibniz rule (4.4) together imply…"; B has no Theorem 4.x | PDF'TE YOK | → "B Section 4, remark after Definition 4.1, via (4.4)+(4.6)"; Theorem `source` |
| 19 | MC §3: (ρ∘L)(Df,u,v)=0 | theorems.py:855,1011 (notes); locality.py:20; tests/test_algebroid_projector.py:3 | MC p12 "For a local pre-Leibniz algebroid, one has (ρ ◦ L)(Df, u, v) = 0" | DOĞRU (vague) | → "MC Section 3, remark before Definition 3.10"; Theorem `source` |
| 20 | MC Def 3.9 regular | context.py:502; locality.py:5,81 (runtime error string) | MC p11 "said to be regular if ρ is of locally constant rank" | DOĞRU | — |
| 21 | MC Def 3.10 locality projector | locality.py:2,45,50,57,97; tests/test_algebroid_projector.py:2 | MC p12 "P ◦ L ∈ [L̃] … such that im(L̂) ⊂ ker(ρ)" | DOĞRU | `source` on Absorption/Kernel rules |
| 22 | MC Def 3.6 locally equivalent | locality.py:120 | MC p9 "locally equivalent if L(Df,u,v) = L̃(Df,u,v)" | DOĞRU | 2nd source of Absorption |
| 23 | "admissible-connections paper Def 3.8" (𝒫\|ker ρ = id) | locality.py:52,153; tests/test_metric_affine_admissible.py:3,106 | ADM p8 Def 3.8 "P\|ker(ρ) = idker(ρ)" | DOĞRU | `source` on Idempotence (condition 2), Kernel (condition 1). Note: ADM Def 3.8 has no explicit absorption clause; on pre-Leibniz it follows from row 19 + condition 2 |
| 24 | MC Cor 3.3 (C∞-multilinear E-curvature) | locality.py:9; modified.py:516,618 | MC p12 Cor 3.3 (3.24) "is C∞(M,R)-multilinear for any L" | DOĞRU | — |
| 25 | MC Prop 3.2 for ᴸT bilinearity | modified.py:3,589; tests/test_modified_torsion_curvature.py:2 | MC p10 Cor 3.2 (3.16) "ᴸT(∇)(u,v) := T(0)(∇)(u,v) + L(ea, ∇Xa u, v) is C∞-bilinear" | YANLIŞ NUMARA (Prop 3.2 is the N-bracket parent; the ᴸT statement is Cor 3.2) | → "MC Corollary 3.2" |
| 26 | MC Def 3.7, Def 3.11, Prop 3.3-3.4 | modified.py:3,483,516,647 | MC p10 Def 3.7; p12 Def 3.11; p11 Props 3.3, 3.4 | DOĞRU | — |
| 27 | coframe recombination Df = Σρ(e_s)(f)e^s (no label) | modified.py:350 | MC p10 proof of Cor 3.2 "ρ(Xa)(f)ea = (Df)(Xa)ea = Df" | — (new) | `source` = MC proof of Corollary 3.2 |
| 28 | ADM (3.36) / Prop 3.8 generalized Ricci identity | modified.py:678,718; e_bianchi.py:19; tests/test_modified_torsion_curvature.py:161 | ADM p13 (3.36) "∇²u,v w − ∇²v,u w = R(∇)(u,v)w − ∇T(∇)(u,v)w + ∇(1−P)L…w" | DOĞRU | — |
| 29 | ADM Prop 3.7 / (3.35) (M8-1≡M7-3) | e_bianchi.py:2,23,103; tests/test_metric_affine_e_bianchi.py:2,42 | ADM p13 (3.35) prints "+ ∇(1−P)L(…)w + [[u,v]∇E, w]∇E + cycl." | DOĞRU (structure); paper's printed signs are wrong | sign note added to the docstring, no code change |
| 30 | ADM Def 3.3 / Def 3.4 (anti-commutable / admissible) | admissible.py:6,13,111 | ADM p6 Def 3.4 "admissible if … [u,v]E + [v,u]E = L(ea,∇Xa u,v) + L(ea,∇Xa v,u)" | DOĞRU | `source` on AdmissibilityDeclaration (overrides the inherited C2 source!), AdmissibilityMetricPairCollection |
| 31 | ADM Prop 3.3 / Cor 3.2 / Prop 3.2 dull part | admissible.py:22,27,32,429,456,682; tests/test_metric_affine_admissible.py:41,72,96 | ADM p8 Prop 3.3 "an E-torsion-free linear E-connection ∇ has to be admissible"; Cor 3.2 (3.18); p7 Prop 3.2 | DOĞRU | — |
| 32 | ADM eq (3.12) modified bracket | admissible.py:99 | ADM p7 (3.12) "[u,v]∇E := [u,v]E − L(ea, ∇Xa u, v)" | DOĞRU | `source` on DerivedBracketBridge ((3.12) or (3.22)) |
| 33 | ᴸT = 0 declaration (no label) | admissible.py:172 | ADM p6 (3.11); MC p10 Def 3.7 (3.16) | — (new) | `source` (ADM 3.11, MC Def 3.7) |
| 34 | MC Prop 4.1 (ᵍL = g(u,v)g⁻¹Ω) | admissible.py:222,227,482; tests/test_metric_affine_admissible.py:145,149 | MC p22 (4.3) "gL(Ω,u,v) := g(u,v)g−1(Ω)" | DOĞRU | `source` on CourantLocality |
| 35 | "Bourbaki eq (4.8)" | admissible.py:482; tests/…admissible.py:149 "B eq 4.8" | B p8 (4.8) "g−1DE g(fu,v) = f g−1DE g(u,v) + g−1ρ∗E(df ∧ g(u,v))" | DOĞRU | → "B (4.8)" |
| 36 | ADM Prop 3.5 (admissible ⇔ metric-compatible on almost-Courant) | admissible.py:222,517,551; tests/…admissible.py:145,160,205 | ADM p11 Prop 3.5 "admissible if and only if it is E-metric-g-compatible" | DOĞRU | — |
| 37 | Q = 0 collection (no label) | admissible.py:268 | MC p7 Def 3.3 (3.6) "Q(∇,g) := ∇g"; p8 (3.7) | — (new) | `source` MC Def 3.3, Eqs. (3.6)–(3.7) |
| 38 | MC Prop 3.7-3.8, eq (3.36), Def 3.14 | e_koszul.py:2,6,27,79,110,355 | MC p15 (3.34); p16 (3.36) "K(∇,g,L)(u,v,w) := −g(L(ea,∇Xa v,w),u) …"; p17 Def 3.14 | DOĞRU | `source` on EKoszulDeclaration |
| 39 | ADM Prop 3.12 / 3.13 / 3.14 | e_koszul.py:3,29,363,386,415,459,496; tests/test_metric_affine_e_koszul.py | ADM p19 Prop 3.12 "E-Levi-Civita if and only if it is admissible and E-Koszul"; p20 (3.57); p21 (3.60) | DOĞRU (3.13 is used in an "identity form" with an E-Koszul reference, which the code says) | — |
| 40 | MC Prop 3.10, Thm 3.2, (3.44), (3.37), (3.8) | e_koszul.py:532,534,569,575,634,639,653,700-752 | MC p17 Prop 3.10 "almost-Lie … local almost-Leibniz … with any L ∈ [0]"; p19 Thm 3.2 (3.44) | DOĞRU; bare "(3.44)"/"(3.37)" in runtime rule strings BELİRSİZ (module mixes MC/ADM) | rule strings → "MC (3.44)", "MC (3.37)"; `source` on NullLocality = MC Thm 3.2 |
| 41 | MC Prop 4.2 fragment | e_koszul.py:615; tests/…derived.py:237 | MC p24 Prop 4.2 "there is a unique locality projector P" | DOĞRU | — |
| 42 | ADM Defs 3.14-3.16, eqs (3.41)-(3.43) | derived.py:3,21,238; tests/test_metric_affine_derived.py:2,58 | ADM p14 (3.41)/(3.42), (3.43) "d̂(∇)²f = 0"; p15 Def 3.15; p16 Def 3.16 | DOĞRU | — |
| 43 | ADM eqs (3.44)-(3.45) (d̂² on 1-forms = associator) | derived.py:333; tests/…derived.py:185,219 | ADM p15 (3.44) "d̂(∇)²Ω(u,v,w) = Ω(Assoc…)" (page image checked) | DOĞRU (structure); NEW FINDING: printed overall sign is wrong (see note 2) | sign note added to the docstring, no code change |
| 44 | MC Prop 3.1 pattern | torsion_curvature.py:377 | MC p7 Prop 3.1 proof, difference E-tensor (3.4) | DOĞRU | — |
| 45 | TM torsion/curvature/non-metricity/connection (no label) | torsion_curvature.py:213,239; metric.py:190,207,542,582,621; metric_affine/rules.py:34,84 | MC p5 (2.9) "T(∇)(U,V) := ∇UV − ∇VU − [U,V]"; (2.12); p4 (2.3), (2.7) | — (new) | `source`s MC (2.3)/(2.7)/(2.9)/(2.12), Section 2 |
| 46 | "MC's tool" for the Derivator | operators.py:11 | MC has no derivator (grep: 0 hits); DD p21 (4.39) "DΦ(u,v) := Φ[u,v]E − [Φu,v]E − [u,Φv]E"; Midterm Q3 | YANLIŞ MAKALE | → "[DD (4.39)] and Midterm Q3"; `source` on DerivatorExpansion |
| 47 | Predator (no label) | operators.py:15,583 | DD p24 footnote 5 "PΦ(u,v) := Φ([u,v]E) − [Φ(u),Φ(v)]E′" (TW (6.9)/(A.6) has the opposite sign) | — (new) | `source` DD footnote 5; sign note in docstring |
| 48 | Jacobiator (no label) | operators.py:310 | TW p13 (3.20) "JE(u,v,w) := [u,[v,w]E]E − [[u,v]E,w]E − [v,[u,w]E]E" | — (new) | `source` TW (3.20) |
| 49 | 2409.11973 App A (A.5)/(A.7)/(A.8), (A.6) | defect_formulas.py:3,11,17,27,75; tests/test_algebroid_defect_formulas.py:2 | TW p46 (A.5), (A.6) "PρE(u,v) := [ρE(u),ρE(v)]Lie − ρE([u,v]E)"; p47 (A.7),(A.8) | DOĞRU | — |
| 50 | B Def 7.1 (7.8), B Def 8.1 (8.5) | context.py:512-516 | B p16 (7.8) "LR ρE(u)(g(v,w)) = g([u,v]E,w) + g(v,[u,w]E)"; p17 (8.5) | DOĞRU | written "B Definition 7.1, Eq. (7.8)" etc. |
| 51 | "[C5] [Uchino]" courant-invariance | context.py:514 | Uchino p1 "[C5] ρ(x)(y,z) = ([x,y] + D(x,y), z) + (y, [x,z] + D(x,z))" | DOĞRU | → "Uchino Section 1, axiom [C5]; original LWX 1997" |
| 52 | "in-repo metric-connection.pdf / pre-metric-bourbaki.pdf" (M8-10) | context.py:5-7; algebroid/__init__.py:6 | the PDFs are untracked local copies | YANLIŞ (wording) | → arXiv numbers and bibliography keys |
| 53 | DD §6 eq (6.8) higher Koszul bracket | nambu.py:4; tests/test_poisson_nambu.py:3 | DD p32 (6.8) "[ω,η]Z = LΠω η + KΠη ω =: [ω,η]Kos" | DOĞRU | — |
| 54 | "drinfeld eq (6.9)" R-twist vanishes iff Nambu-Poisson | nambu.py:521 | DD p32 (6.9) defines R; p34 "Π is a bracket morphism is … equivalent to … Nambu-Poisson" | BELİRSİZ (the equivalence is the remark after (6.13), citing their ref. [122]) | locator made precise |
| 55 | Midterm Q2 definitions ({f,g}, π♯, Koszul bracket, ι_{Xf}ω = df, dω = 0, π = ω⁻¹) | poisson/core.py, koszul.py, symplectic.py:1 | Midterm p1 "ιXf ω = df, {f,g} := π(df,dg)"; "[ω,η]T∗M = Lπ♯(ω)η − Lπ♯(η)ω − d(π(ω,η))" | DOĞRU | `source`s on PoissonBracket, SharpEvaluation, KoszulBracket, SymplecticHamiltonian, SymplecticClosed, SharpFlatIdentity; Theorem `source` Q2(h) on poisson_jacobi |
| 56 | Midterm Q3 ι̃_ω V := ι_V ω | tilde.py:162 | Midterm p2 "introduce ι̃ω V := ιV ω" | DOĞRU | `source` on TildeInteriorAct |
| 57 | 2409.11973 §7, "Eq. (7.3)" Ψ-transport | research/axiom_suite.py:11,105 | TW p29 (7.3) "[u,v]Roy′ = Ψ−1[Ψu,Ψv]Roy" | DOĞRU; bare "Eq. (7.3)" BELİRSİZ | → "[TW (7.3), arXiv:2409.11973]" |
| 58 | Kosmann-Schwarzbach 1996 (derived brackets) | brackets/derived.py:16 | no PDF; the bibliography only has KosmannSchwarzbach2004 ("Derived brackets", LMP 69) | PDF YOK (ikincil kaynak) | not changed (see open question 1) |
| 59 | "C∞-module analysis of MC §3" | tests/test_algebroid_operators.py:82 | MC p8 "one needs to know how the C∞(M,R)-module structure is affected by the bracket" | DOĞRU (loose) | — |
| 60 | "PDF item N" / "definition policy §N" / "Roytenberg — item 12" | calculus/*, tangent/engine.py, poisson/*, packages/__init__.py, brackets/__init__.py | course guide (yönerge) / internal policy, not literature | PDF YOK (ikincil kaynak) | — |

### 2. Notes
1. **M8-1 ≡ M7-3** (ADM (3.35)) is documented in the `e_bianchi.py` module docstring. The math is unchanged. I also corrected the "[ADM]'s [[u,v]^∇,w]^∇ extra term" phrase to say the paper prints the opposite sign.
2. **New finding (same kind as M8-1): ADM (3.44)'s printed sign is wrong.** I checked the page image (p15). The paper prints `d̂²Ω(u,v,w) = Ω(Assoc)` with `Assoc = [u,[v,w]] − [[u,v],w] − [v,[u,w]]` (3.45). For an admissible ∇ (b̂ anti-symmetric), Assoc = −(b̂(b̂(u,v),w) − b̂(b̂(u,w),v) + b̂(b̂(v,w),u)). That bracketed combination is what the code proves, and it follows from the Palais formula (3.42). At ρ = 0: d(dα)(u,v,w) = α([[u,v],w] − [[u,w],v] + [[v,w],u]). TW (A.5) `d²μ = … − μ(J)` with J from TW (3.20) agrees with the code. I documented this in the `derived.py` docstring with no code change.
3. **AdmissibilityDeclaration inherits from SymmetricPartDeclaration.** Without an explicit override it would have inherited the B (4.7) source. I added `source = ADM Definition 3.4` on the subclass. No other subclass of a sourced rule exists (grep).
4. ProofSteps built from rule or theorem objects now copy the source: `step_c1` (`c1.source`), `step_am` (`am.source`), `step_c2` (`t_c2.source`) and `step_rl` (`t_rl.source`) in algebroid/theorems.py.
5. `Theorem(source=…)` was added in algebroid/theorems.py to anchor_morphism, right_leibniz (B (4.11) first identity), symmetric_part_swap (C2 source), left_leibniz (B (4.11) second identity + MC Prop 4.1) and locality_anchor_annihilation. In poisson/showcase.py it was added to poisson_jacobi (Midterm Q2(h)).
6. The brief listed "anchor morphism (MC (3.19) / B (4.6))". In B it is **(4.5)**; (4.6) is Leibniz-Jacobi.
7. MC (4.2) (metric-algebroid invariance) prints `g(u,[v,w])`, an apparent typo. For C1 only B (4.10) is cited.
8. Smoke check: `chain_sources` of `prove_left_leibniz_from_metric` lists B Def 4.2/4.3 (4.7)/(4.9), MC Def 4.1 (4.1), MC Def 3.1, B (4.11), B Def 4.3 (4.10). APA reference block renders.

### 4. ROADMAP.md fixes (not in the worktree; list only)
- ROADMAP:370 "[B Thm 4.1]" (and "Bourbaki §4.1") → "[B Section 4, remark after Definition 4.1, via (4.4)+(4.6)]".
- ROADMAP:730 "[MC Def 3.2, 3.16, 3.24]" → "[MC Definition 3.2, Eqs. (3.16), (3.24)]".
- ROADMAP:876-882 (E-Bianchi, ADM Prop 3.7): add "ADM (3.35) prints the (1−𝒫)Λ and [[u,v]^∇,w]^∇ blocks with +; definitions (3.12)/(3.13)/(3.20) give −; code sign is right (point-model counterexample)".
- ROADMAP lines on 4.F.6b (d̂² on 1-forms, ADM (3.44)-(3.45)): add "ADM (3.44) printed overall sign is opposite to (3.42)+(3.45) for admissible ∇; code follows the Palais formula, agrees with TW (A.5)".
- Every ROADMAP line that says "MC Prop 3.3" for R⁰ last-slot tensoriality → "MC (3.19) + Proposition 3.3"; "MC Prop 3.2" for ᴸT bilinearity → "MC Corollary 3.2".
- "in-repo *.pdf" wording → arXiv numbers / bibliography keys.

### 5. For the owner (Oğuzhan) to decide
1. brackets/derived.py cites "Kosmann-Schwarzbach 1996" (derived brackets / Loday). The bibliography has only `KosmannSchwarzbach2004` ("Derived brackets", LMP 69, math/0312524). Should a 1996 key be added (Ann. Inst. Fourier 46, "From Poisson algebras to Gerstenhaber algebras"; no local PDF), or should the text be re-pointed to 2004? I left it unchanged.
2. Should the two paper sign errors (ADM (3.35), ADM (3.44)) get a regression test like the M8-1 acceptance test (paper-signed RHS honestly rejected)? Not done here (no logic changes).
3. Midterm Q2(b) states `{f,g} = ω(X_f, X_g)`. Under the code's first-slot interior convention this is refused; the code proves `ω(X_g, X_f)`, as documented in symplectic.py. So PoissonOmegaBridgeDeclaration got no Midterm source on purpose.

## Lane D — Çatal-Özer, Doğan & Yetişmişoğlu (2024) [DD] and (2025) [TW] — Drinfel'd package

| # | label (as in code) | code locations | paper, page, quote | status | fix applied |
|---|---|---|---|---|---|
| 1 | §4, (4.14), (4.32)-(4.34), (4.4)-(4.5) | d/calculus_conditions.py:3-4 | DD p15 (4.4)-(4.5); p18 (4.14) "LVω + KVω = dιVω"; p20 (4.32)-(4.34) | DOĞRU | DD prefix |
| 2 | 𝒦_V := −ℒ_V + dι_V [eq (4.14)] | d/calculus_conditions.py:9, :59 | DD p18 (4.14) (explicit form (4.18) "KVω = −LVω + dιVω") | DOĞRU | DD prefix, + "(4.18)" |
| 3 | prototype [App A] | d/calculus_conditions.py:13 | DD p49 "A Cartan calculus" | DOĞRU | "DD App A" |
| 4 | 𝒦-composition laws [eqs (4.4)-(4.5)] | d/calculus_conditions.py:20-21; t/test_drinfeld_calculus.py:2 | DD p15 (4.4) lines 2-3; (4.5) = C∞-linearity | DOĞRU (kısmen; içerik (4.4)'te) | "DD (4.4) 2nd/3rd lines; (4.5) companion" |
| 5 | 𝒦_U𝒦_V = −𝒦_Uℒ_V [drinfeld eq (4.5)] | d/calculus_conditions.py:152 | DD p15 (4.4) "KU KV ω = −KU LV ω" | YANLIŞ NUMARA | → DD (4.4), third line |
| 6 | 𝒦_{[U,V]} = 𝒦_V𝒦_U + ℒ_U𝒦_V [drinfeld eq (4.5)] | d/calculus_conditions.py:171 | DD p15 (4.4) "K[U,V]A ω = KV KU ω + LU KV ω" | YANLIŞ NUMARA | → DD (4.4), second line |
| 7 | (4.11), (4.17) doubled bracket | d/double.py:3, :7, :76, :434 | DD p16 (4.11) Dorfman-like; p18 (4.17) | DOĞRU | DD prefix |
| 8 | ℒ̃_ω V = [π♯ω,V] + π♯ι_V dω (poisson_double, unlabelled) | d/double.py:82 | DD p22 (4.41) "L̃ω V = [Πω,V]Lie + ΠιV dω" | DOĞRU | added [DD (4.41)], d̃ [DD (6.7)] |
| 9 | LWX anchor = sum of anchors [eq (4.19)] | d/double.py:278 | DD p18 (4.19) is the METRIC gE; anchor p16 (4.8) "ρE = ρA ⊕ ρZ", p36 (6.25) "ρE(U+ω) = idTM U + Πω" | YANLIŞ NUMARA | → DD (4.8), explicit DD (6.25) |
| 10 | ℒ̃_ω W = [Πω,W] + Π(ι_W dω) [drinfeld eq (6.6)] | d/double.py:422 | DD p32 (6.6) "L̃ω V = [Πω,V]Lie − ΠKV ω" + fn 8 "KV = −ιV d" | DOĞRU (eşdeğer) | DD (6.6) + fn 8 + "as in DD (4.41)" |
| 11 | Nambu double [eq (4.17) with (6.6)-(6.7)] | d/double.py:434-435 | DD p18 (4.17), p32 (6.6)-(6.7) | DOĞRU | DD prefix |
| 12 | Nambu anchor [eq (D.4)] | d/double.py:483; t/test_drinfeld_double.py:190 | DD p51 (D.4) "= f L̃ω V + ρZ(ω)(f)V" | DOĞRU | DD prefix, + DD (6.25) |
| 13 | g_Z = ι_{Πω}η + ι_{Πη}ω [eq (6.17)] (M8-2) | d/double.py:530-541; d/tilde_calculus.py:854-861 | DD p34 (6.17) "DZ = ½d, gZ(ω,η) = 2(ιΠω η + ιΠη ω)"; "factors ½ and 2 … crucial" | BELİRSİZ (içerik farklı: g_Z yarısı, D_Z=d; çarpım aynı) | math unchanged; docstrings document ½/2 convention + in-repo inconsistency |
| 14 | (D.1)-(D.4) right-Leibniz anomalies | d/double.py:581-583; t/test_drinfeld_double.py:190 | DD p51 (D.1)-(D.4) | DOĞRU | DD prefix |
| 15 | (4.36)-(4.38) Poisson bialgebroid | d/poisson_bialgebroid.py:3,14,16,20,85,372,411; t/test_drinfeld_bialgebroid.py:2,27,34,43 | DD p21 (4.36)-(4.38) | DOĞRU | DD prefix |
| 16 | d̃ = −π♯d [paper §6, Π = π] | d/poisson_bialgebroid.py:9 | DD p32 (6.7) "d̃ = −Πd" | DOĞRU (kesinleştirildi) | → [DD (6.7)] |
| 17 | g_Z = 2(π(ω,η)+π(η,ω)) at p=1 | d/poisson_bialgebroid.py:20-24 | DD p34 (6.17) factor 2 | DOĞRU (paper normalisation) | note on in-repo ½ convention |
| 18 | 𝒦̃_η V = [V,π♯η] − π♯ℒ_Vη [paper eq (4.41)] | d/poisson_bialgebroid.py:~55 | DD p22 (4.41) is L̃; 𝒦̃ is p32 (6.6) line 2 "K̃η U = [U,Πη]Lie − ΠLU η" | YANLIŞ NUMARA | → DD (6.6), second line |
| 19 | ℒ̃_ω V = [π♯ω,V] + π♯ι_V dω [paper eq (6.6)] | d/poisson_bialgebroid.py:~64 | verbatim DD p22 (4.41); (6.6) equivalent via fn 8 | YANLIŞ NUMARA (eşdeğer; #18 ile yer değiştirmiş) | → DD (4.41) verbatim, ≡ DD (6.6) |
| 20 | App D, (D.5)-(D.13); (C.1)-(C.3)/(4.34) | d/tilde_calculus.py:2-26; t/test_drinfeld_tilde_calculus.py:1-8 | DD p50 (C.1)-(C.3); p51-53 (D.5)-(D.13) "The first condition (C.1) reads" | DOĞRU | DD prefix |
| 21 | ι̃_η U := ι_U η; d̃ = −Πd [eq (6.7)] | d/tilde_calculus.py:53, :58 | DD p32 (6.7) "ι̃ω V = ιV ω, d̃ = −Πd" | DOĞRU | DD prefix |
| 22 | 𝒦̃ := −ℒ̃ + d̃ι̃ [the (4.14) pattern on tilde side] | d/tilde_calculus.py:63 | DD p18 (4.16) "L̃ω V + K̃ω V = d̃ι̃" | DOĞRU (kesin numara (4.16)) | → DD (4.16), counterpart of DD (4.14) |
| 23 | NambuMorphismDeclaration [drinfeld eq (6.9)] | d/tilde_calculus.py:73-83 | DD p32 (6.9) "R(ω,η) = [Πω,Πη]Lie − Π[ω,η]Kos" | DOĞRU | DD prefix; `source = cite(DD, "Eq. (6.9)")`; FI-instance ProofStep/Theorem copy it |
| 24 | "(the (4.13) ↔ ⊛ bridge)" | d/tilde_calculus.py:325; d/multivector_interior.py:183, :265; t/test_multivector_interior_forms.py:4; t/test_drinfeld_examples.py:139 | DD p17 (4.13) is symmetric part "[u,v]E+[v,u]E = DE gE"; TW p16 (4.13) linearity; E6 paper not in repo | PDF YOK (ikincil kaynak) — E6 paper | labelled "E6-paper (4.13), unverified, NOT DD/TW (4.13)" |
| 25 | (D.9)…(D.13) with (4.36)/(4.37)/(4.38)/(4.40) | d/tilde_calculus.py:~690-915; t/test_drinfeld_tilde_calculus.py:36,68,87,146 | DD p51-53 (D.8)-(D.13); p21 (4.36)-(4.40) | DOĞRU | DD prefix; (D.10) note on 𝔻_Z = d convention |
| 26 | App D (D.14)-(D.19) / (4.44)-(4.50), Claim 6 | d/metric_invariance.py:2-37, :98-247; t/test_drinfeld_metric_invariance.py:2,34,48,71 | DD p53 (D.14)-(D.17); p54 (D.19) "proves our Claim 6"; p23-24 (4.44)-(4.50) | DOĞRU | DD prefix |
| 27 | (D.18) ℒ_{Πω}ι_Wη = ι_Wℒ_{Πω}η + ι_{ℒ̃_ωW}η − ι_{Π(ι_W dω)}η (M8-7) | d/metric_invariance.py:21, :188-202 | DD p53 (D.18) "2(ιV LΠω η + …) = 2LΠω ιW η" (V/W mixed) | BELİRSİZ (baskı V/W karışık; kod doğru Cartan özdeşliği) | caveat added to docstring |
| 28 | g_E "[the (5.22) components that survive on TM ⊕ Λᵖ]" (M8-2) | d/metric_invariance.py:217-226, :32-34 | DD has no (5.22); DD p34 (6.20) "gE = 0 ⊕ (ι̃ωV+ι̃ηU) ⊕ 2(…) ⊕ (ιUη+ιVω)"; TW p21 (5.22) | YANLIŞ MAKALE (pakette önek yok; içerik DD (6.20)) | → DD (6.20) (≡ TW (5.22)); documented code g_E = ½·Σ components |
| 29 | locality "(5.8)/(3.17)" | d/abstract_double.py:19, :122-127; t/test_drinfeld_abstract_double.py:27 | TW p12 (3.17) "[fu,v]E = f[u,v]E − ρE(v)(f)u + LE(f,u,v)"; p19 (5.8) LE decomposition; DD (3.17)/(5.8) unrelated | DOĞRU (TW; önek yoktu) | TW prefix; note: right-Leibniz⟺locality is the code's derivation |
| 30 | "paper eqs (4.18)-(4.20)" bracket morphism | d/bracket_morphism.py:2-27, :72, :98, :150; t/test_drinfeld_bracket_morphism.py:2,25,32,45 | TW p16 (4.18) ϕ map, (4.19) "[ϕ(u),ϕ(v)]E′ − ϕ([u,v]E) = 0", (4.20) | DOĞRU (TW; önek yoktu) | TW prefix + "= DD (4.51)-(4.52)" |
| 31 | "(4.20)-dual" ℒ̃_ωV + Π𝒦_Vω = [Πω,V] | d/bracket_morphism.py:14, :98; t/…bracket_morphism.py:32 | not in TW; DD p24 (4.52) line 2 "ϕA(L̃ω V) + ϕZ(KV ω) = [ϕZ(ω), ϕA(V)]" | DOĞRU (DD'de) | added DD (4.52) second line |
| 32 | Roytenberg bracket (5.2), (5.4)/(5.5) | d/roytenberg.py:3, :12, :76; t/test_drinfeld_roytenberg.py:2 | TW p18 (5.2) 8 components; (5.4),(5.5) | DOĞRU | TW prefix |
| 33 | twisted linearity (5.6)-(5.7) | d/roytenberg.py:17, :108; d/examples.py:604,649; t/…roytenberg.py:70; t/…examples.py:194,209 | TW p19 (5.6) "H(U,fV) = fH(U,V)", (5.7) symbols | DOĞRU | TW prefix |
| 34 | H-closure (5.13) defect; docstring "= −ι_Wι_Vι_U dH" (M4-7) | d/roytenberg.py:21-31, :155-190, :224, :262; t/…roytenberg.py:2,82,92 | TW p20 (5.13) "… = −LU H(V,W) + KW H(U,V) + LV H(U,W)"; RHS ιιιdH is code's theorem | DOĞRU (numara); modül docstring işareti yanlıştı | sign → "+ι_Wι_Vι_U dH" (as proved), TW prefix |
| 35 | (5.14) vs untwisted (D.8) | d/roytenberg.py:312-314; t/…roytenberg.py:124-126 | TW p20 (5.14) "… − H(U, R(η,μ))"; (D.8) is DD p52 | DOĞRU (D.8 → DD) | DD/TW prefixes |
| 36 | (5.16) reduces to (D.10) | d/roytenberg.py:32-34 | TW p20 (5.16) "− dH gH(R(ω,η),W)"; (D.10) DD p52 | DOĞRU | DD/TW prefixes |
| 37 | (5.9), (5.12) | d/roytenberg.py:345, :554; t/…roytenberg.py:136,188 | TW p19 (5.9); p20 (5.12) "JA(U,V,W) = −K̃H(V,W)U + L̃H(U,V)W + K̃H(U,W)V" | DOĞRU | TW prefix |
| 38 | (7.26) anomaly −Π(df∧g_Z) | d/roytenberg.py:19, :494-497; t/…roytenberg.py:179 | TW p33 (7.26) "− Π(σd(f, ιΠωη + ιΠηω))" (= code g_Z, ½ of DD) | DOĞRU | TW prefix + normalisation note |
| 39 | master eqs (3.11)-(3.15); (3.14) {μ,φ}=0 ⟺ dH=0 | d/roytenberg.py:362-389; t/…roytenberg.py:165 | TW p11 (3.11)-(3.15); bosonic readings not printed in TW | DOĞRU (numaralar) / okuma kodun | TW prefix; "readings are ours" |
| 40 | (3.11) ⟺ H-twisted FI [Πω,Πη] = Π[ω,η]_Kos + ΠH(Πω,Πη) (M4-1) | d/roytenberg.py:371-386, :391-397 (r_twist_h), :405-407 (TwistedFIDeclaration), :474-476; t/…roytenberg.py:168-171 | TW p11 (3.11) "½{µ,µ} + {γ,ϕ} = 0" bi-degree (1,3); p26 (6.10) "PρA(U,V) = ρZ H(U,V)"; twisted FI = TW p33 (7.25) R′ with H | YANLIŞ NUMARA (yanlış sektör) | comment/docstrings/test docstring corrected (V-M4 KARAR); code untouched; `TwistedFIDeclaration.source = cite(TW, "Eq. (7.25)")` |
| 41 | (3.12) quasi-Poisson face of ψ; (3.15) [π,ψ]_SN | d/roytenberg.py:571-601, :697, :736; t/…roytenberg.py:213,232,241 | TW p11 (3.12) "½{γ,γ} + {µ,ψ} = 0", (3.15) "{γ,ψ} = 0"; bi-degree (3,1) consistent | BELİRSİZ (okuma makalede yok; sektör tutarlı) | TW prefix only |
| 42 | twist §7, (7.3), (7.11), (7.12), (7.13), (7.14)/(7.16), (7.18), (7.24)-(7.25) | d/twist.py:3-12, :70-103, :323-432, :624, :702, :910-1029; d/endomorphism.py:3-4, :19; t/test_drinfeld_twist.py:1,58,69,176,230 | TW p29 (7.3) "[u,v]Roy′ = Ψ−1[Ψu,Ψv]Roy"; p31 (7.11)-(7.18); p32-33 (7.24)-(7.25) | DOĞRU | TW prefix |
| 43 | "Ševera remnant (7.20)" (M8-7) | d/twist.py:29-31, :462-463 | TW p32 (7.19) "H′(U,V) = H(U,V) + LU BV + KV BU + …"; (7.20) = tilde changes | YANLIŞ NUMARA | → TW (7.19) (H′); (7.20) context noted |
| 44 | FULL Ševera (7.19)-(7.20) | d/twist.py:643; t/…twist.py:135 | TW p32 (7.19)-(7.20) | DOĞRU | TW prefix |
| 45 | (7.26) R′ linearity | d/twist.py:511-561; t/…twist.py:101 | TW p33 (7.26), "C∞M-linear in the second entry" | DOĞRU | TW prefix |
| 46 | "General 2×2 Ψ composition (7.7)-(7.10)", "(7.7) instance: B-transforms compose additively" (M8-7) | d/twist.py:1127-1130, :1166-1170; t/…twist.py:301-304, :331 | TW p30 (7.7) components of ONE Ψ; no composition law in TW | PDF'TE YOK (bileşim kodun kendi sonucu) | relabelled "code's own result", TW (7.7) role explained |
| 47 | §8, (8.15)-(8.16), (8.1), (8.17)-(8.28), (5.21) | d/examples.py:3-16, :70, :87, :238, :691-799; t/test_drinfeld_examples.py:2,24,54,192,221,235,236,255 | TW p34 (8.1); p39 (8.15) "[U+f+ω, V+g+η]E = …", (8.16) "gE = ιUη + ιVω + fg"; p39-41 (8.17)-(8.28); p21 (5.21) | DOĞRU | TW prefix |
| 48 | exceptional pairing ⟨e₁,e₂⟩ for (8.1) | d/examples.py:22-24 | TW p34 prints no pairing for (8.1) | PDF'TE YOK | marked "the code's; TW does not print one" |
| 49 | H-twist of "A = TM ⊕ Λ⁵" [eq (8.2)] (M8-7) | d/examples.py:25-27 | TW p34 "For the decomposition A = TM ⊕ Λ²T*M, Z = Λ⁵T*M … H-twist" (8.2) | YANLIŞ NUMARA (yanlış ayrışım) | → A = TM ⊕ Λ²T*M, Z = Λ⁵T*M; (8.3) A = TM ⊕ Λ⁵T*M, Z = Λ²T*M |
| 50 | Atiyah (8.10)-(8.14): "(5.13) H-closure IS Bianchi d^∇F = 0" (M4-2) | d/examples.py:29-37; t/test_drinfeld_examples.py:76-82 | TW p38-39 (8.10)-(8.14); line 2145 "(5.13) then follows from the Bianchi identity for the curvature" | DOĞRU (makale ifadesi) / mekanik bağ YOK | docstrings: "name-level reference only, no mechanical link"; test body untouched |
| 51 | (Π₃⊛Π₃)(ω₅) [E6 paper eq (4.14)]; Ψ_Π [E6 (4.10)-(4.12)]; Ψ_Π⁻¹ [eq (4.11)] | d/examples.py:565, :806, :811, :829; t/…examples.py:176, :273-274 | no E6 PDF; TW (4.14) is Jacobi compat. | PDF YOK (ikincil kaynak) | marked unverified; bare "[eq (4.11)]" → "E6 paper" |
| 52 | "[2409.11973 / E6 paper eqs (4.13)-(4.14)]" (M8-4) | d/../central/objects/multivector_interior.py:3 | TW p16 (4.13) "LU(fω) = fLUω + ρA(U)(f)ω", (4.14) Jacobi compat. | YANLIŞ MAKALE | 2409 attribution removed; E6 paper flagged unidentified |
| 53 | block_matrix "covers every twist of [2409.11973 §7]" (M8-6) | jacopy/research/block_matrix.py:14-24 | TW p29 (7.4) general Ψ; p31 (7.11) "Ψm = (m 0; 0 m̃)" — not unipotent | YANLIŞ (aşırı iddia) | narrowed to unipotent Ψ_B/Ψ_Π (same-side products); Ψ_m, general Ψ excluded |
| 54 | Primary sources | d/__init__.py:3-17 | DD/TW title pages | DOĞRU | DD/TW alias legend added |

### Notes
- M8-2: math NOT changed. Docstrings (double.py prove_nambu_double_symmetric_part_form, tilde_calculus.g_z_pairing and (D.10),
  poisson_bialgebroid module, metric_invariance.double_metric, roytenberg (7.26) note) now state: code g_Z = ½·g_Z^DD with D_Z = d,
  so D_Z g_Z equals DD (6.17); poisson_bialgebroid uses the paper's 2 (harmless at p = 1, both vanish).
- M4-7 (bonus, in-file): roytenberg module docstring said defect(5.13) = −ιιι dH; the proved node is defect − ιιιdH → 0, i.e. "+". Fixed docstring.
- M4-1: the master-equation comment now says (3.11) is the (1,3) A-sector (TW (6.10)); the twisted-Poisson FI's paper source is
  TW (7.25) with H; the declaration's master-equation link is name-level. Test `test_twisted_fi_kills_r_twist_h` docstring updated, body untouched.

### ROADMAP.md fixes (not in worktree — proposals only)
- ~1648-1650 "(5.13) H-closure = Bianchi d^∇F=0 — Faz 4 prove_bianchi_second citation'la süite bağlandı" → "(5.13) ↔ Bianchi: yalnız isim düzeyinde atıf (TW §8.3); mekanik bağ yok (V-M4 M4-2)".
- 1601-1602/1610 "master denklem bağı (3.11) ⟺ H-twisted FI" → "twisted FI = TW (7.25) R′=0 (H'li); (3.11) (1,3) A-sektörü, bağ isimsel (M4-1)".
- 1693-1694 "(eski not 4.51-53 yanlış hatırlamaymış)" → "TW (4.18)-(4.20) = DD (4.51)-(4.52); ikisi de doğru".
- 1667 "exceptional Courant (7.2-7.13)" → "DD (7.2)-(7.13) [arXiv:2312.06584]" (2409'un değil).
- 1669 / 3217-3218 E6 paper: add "künye bilinmiyor, repo'da yok; 2409.11973 değil".
- 1739-1740 "ana teoremin mekanik yüzü tamam" — not citation; flag (M4-3).
- Any "covers every twist" for block_matrix → "unipotent Ψ_B/Ψ_Π twists only".

### Owner decisions (Oğuzhan)
1. g_Z normalisation: keep code convention (½·DD, D_Z = d) and the documented inconsistency with poisson_bialgebroid, or unify? (No math changed here.)
2. Identify the "E6 paper" (authors/arXiv) and add a bibliography key + PDF; until then all E6 (4.10)-(4.15) labels stay unverified.
3. No bibliography key missing for this lane (DD/TW suffice).

