"""Generalized geometry (project directive item 14; Phase 7).

Courant algebroid axiomatics + the Uchino redundancy theorems
(Uchino 2002, arXiv:math/0204010); the standard, H-twisted and
general-twist Dorfman/Courant brackets and their property suites; the
Roytenberg-Courant family; Bourbaki (pre)calculus, Ševera and
exact (pre-)Bourbaki structures; the Poisson-generalized / R-twisted
(θ, R-flux) brackets; the exceptional double and its rotation; and
the Nambu ↔ Poisson dialect bridge."""

from jacopy.packages.generalized.courant_axioms import (
    C3IdentityDeclaration,
    CourantD,
    CourantInvarianceDeclaration,
    DDZeroDefinition,
    DLeibnizDefinition,
    DNumericHomogeneityDeclaration,
    DPairingUnfoldDefinition,
    SkewSwapCompositeDefinition,
    courant_context,
    courant_engine,
    prove_anchor_annihilates_d,
    prove_bracket_with_d,
    prove_d_numeric_homogeneity,
    prove_d_pairing_formula,
    prove_left_leibniz_c3,
    prove_leibniz_from_c3,
)
from jacopy.packages.generalized.dorfman_axioms import (
    dorfman_axiom_context,
    prove_dorfman_c2_redundant,
    prove_dorfman_c3_redundant,
)
from jacopy.packages.generalized.twisted_courant import (
    courant_bracket_h,
    prove_severa_twist_is_courant,
    prove_twisted_anchor_morphism,
    prove_twisted_courant_dorfman_relation,
    prove_twisted_invariance,
    prove_twisted_jacobi_dh_defect,
    prove_twisted_right_leibniz,
    prove_twisted_symmetric_part,
)
from jacopy.packages.generalized.poisson_generalized import (
    d_operator_theta,
    poisson_base,
    prove_theta_anchor_morphism,
    prove_theta_courant_skew,
    prove_theta_right_leibniz,
    prove_theta_symmetric_part,
    prove_theta_d_pairing_value,
    prove_theta_invariance,
    prove_theta_jacobi,
    theta_anchor,
    theta_courant,
    theta_dorfman,
)
from jacopy.packages.generalized.r_twisted import (
    prove_derived_r_vanishes_under_poisson,
    prove_r_twisted_anchor_morphism,
    prove_r_twisted_jacobi,
    prove_r_twisted_jacobi_defect_is_dtheta_r,
    lichnerowicz_d,
    prove_r_twisted_courant_relation,
    prove_r_twisted_right_leibniz,
    prove_r_twisted_symmetric_part,
    r_term,
    r_twisted_theta_dorfman,
)
from jacopy.packages.generalized.roytenberg_courant import (
    prove_full_roytenberg_symmetric_part,
    prove_roytenberg_h_is_twisted_dorfman,
    prove_roytenberg_is_theta_double_under_poisson,
    prove_roytenberg_reduces_to_dorfman,
)
from jacopy.packages.generalized.frame_evaluation import (
    prove_anchor_components,
    prove_basis_pairing_components,
    prove_dorfman_form_components,
    prove_dorfman_vector_components,
    prove_theta_koszul_components,
)
from jacopy.packages.generalized.bourbaki_precalculus import (
    BourbakiPreCalculus,
    bourbaki_engine,
    prove_cartan_satisfies_914,
    prove_cartan_satisfies_915,
    prove_standard_metric_invariance,
    prove_standard_symmetric_part,
    standard_bracket,
    standard_metric,
)
from jacopy.packages.generalized.bourbaki_structure import (
    bourbaki_structure_context,
    bourbaki_structure_engine,
    prove_left_leibniz_bourbaki,
    prove_locality_is_symbol,
    prove_right_leibniz_from_r_invariance,
)
from jacopy.packages.generalized.bourbaki_exact import (
    exact_bourbaki_context,
    exact_bourbaki_engine,
    prove_911,
    prove_912,
    prove_lemma_91,
)
from jacopy.packages.generalized.bourbaki_severa import (
    prove_chi_chi_bracket_vanishes,
    prove_chi_phi_bracket,
    prove_delta_first_slot_anomaly,
    prove_delta_lands_in_chi,
    prove_delta_tensorial_second_slot,
    prove_h_antisymmetric_for_isotropic_phi,
)
from jacopy.packages.generalized.exceptional_rotation import (
    exceptional_rotation_engine,
    pi_block,
    prove_rotated_form_decomposition,
    prove_rotated_vector_decomposition,
    rotated_exceptional_bracket,
)
from jacopy.packages.generalized.exceptional_double import (
    exceptional_double,
    exceptional_r_twist,
    exceptional_r_twist_components,
    exceptional_z_bracket,
    prove_exceptional_r_twist_bidegree_split,
    prove_exceptional_r_twist_symmetric_part,
    prove_r22_reduces_to_lifted_cross_term,
    prove_r25_is_lie_tilde_equivariance_defect,
    prove_rotated_is_exceptional_double_plus_r,
)
from jacopy.packages.generalized.exact_locality_projector import (
    b_field_projector,
    linear_projector,
    prove_b_field_projector_is_a_locality_projector,
    prove_linear_projector_is_a_locality_projector,
    prove_projector_differs_from_pr2_on_a_frame,
    prove_projector_fixes_locally_exact_forms,
)
from jacopy.packages.generalized.dialect_bridge import (
    prove_koszul_dialects_agree,
    prove_theta_form_jacobi_by_citation,
)
from jacopy.packages.generalized.frame_evaluation import (
    prove_boxtimes_components_are_413,
)
from jacopy.packages.generalized.general_twist import (
    PsiInvSec,
    PsiSec,
    prove_general_twist_bilinearity,
    prove_general_twist_invariance,
    prove_general_twist_jacobi,
    prove_general_twist_right_leibniz,
    prove_general_twist_symmetric_part,
    twisted_anchor,
    twisted_bracket,
    twisted_d,
    twisted_metric,
)
from jacopy.packages.generalized.standard_courant import (
    courant_bracket_std,
    courant_jacobiator_std,
    courant_t_scalar_std,
    d_operator_std,
    prove_anchor_morphism_std,
    prove_courant_c3_lwx_std,
    prove_courant_dorfman_relation,
    prove_courant_jacobi_dt_std,
    prove_courant_skew_std,
    prove_dorfman_invariance_std,
)

# Facade alignment (DENETİM 0B00E1B-FULL T2-6): the remaining user-path
# constructors, prove_* theorems and package-specific declarations/rules.
from jacopy.packages.generalized.bourbaki_severa import (
    severa_engine,
)
from jacopy.packages.generalized.dialect_bridge import (
    bridge_engine,
)
from jacopy.packages.generalized.exact_locality_projector import (
    locally_exact_form,
)
from jacopy.packages.generalized.exceptional_double import (
    exceptional_lie_tilde,
    pi_hat,
    transported_form_pairing,
)
from jacopy.packages.generalized.frame_evaluation import (
    basis_pairing,
)
from jacopy.packages.generalized.general_twist import (
    general_twist_engine,
)
from jacopy.packages.generalized.r_twisted import (
    RFluxClosureDeclaration,
    lichnerowicz_calculus,
)

__all__ = [
    "C3IdentityDeclaration",
    "CourantD",
    "CourantInvarianceDeclaration",
    "DDZeroDefinition",
    "DLeibnizDefinition",
    "DNumericHomogeneityDeclaration",
    "DPairingUnfoldDefinition",
    "SkewSwapCompositeDefinition",
    "BourbakiPreCalculus",
    "bourbaki_engine",
    "bourbaki_structure_context",
    "bourbaki_structure_engine",
    "courant_bracket_h",
    "courant_bracket_std",
    "courant_context",
    "courant_engine",
    "courant_jacobiator_std",
    "courant_t_scalar_std",
    "d_operator_std",
    "d_operator_theta",
    "dorfman_axiom_context",
    "exact_bourbaki_context",
    "exact_bourbaki_engine",
    "poisson_base",
    "PsiInvSec",
    "PsiSec",
    "pi_block",
    "prove_911",
    "prove_chi_chi_bracket_vanishes",
    "prove_chi_phi_bracket",
    "prove_delta_first_slot_anomaly",
    "prove_delta_lands_in_chi",
    "prove_delta_tensorial_second_slot",
    "prove_h_antisymmetric_for_isotropic_phi",
    "prove_912",
    "prove_anchor_components",
    "prove_anchor_morphism_std",
    "prove_basis_pairing_components",
    "prove_cartan_satisfies_914",
    "prove_cartan_satisfies_915",
    "prove_dorfman_form_components",
    "prove_dorfman_vector_components",
    "prove_theta_koszul_components",
    "prove_courant_c3_lwx_std",
    "prove_courant_dorfman_relation",
    "prove_courant_jacobi_dt_std",
    "prove_courant_skew_std",
    "prove_dorfman_invariance_std",
    "prove_anchor_annihilates_d",
    "prove_bracket_with_d",
    "prove_d_numeric_homogeneity",
    "prove_d_pairing_formula",
    "prove_derived_r_vanishes_under_poisson",
    "prove_dorfman_c2_redundant",
    "prove_dorfman_c3_redundant",
    "prove_full_roytenberg_symmetric_part",
    "prove_left_leibniz_bourbaki",
    "prove_lemma_91",
    "prove_left_leibniz_c3",
    "prove_locality_is_symbol",
    "prove_r_twisted_anchor_morphism",
    "prove_r_twisted_jacobi",
    "prove_r_twisted_jacobi_defect_is_dtheta_r",
    "lichnerowicz_d",
    "prove_rotated_form_decomposition",
    "prove_rotated_vector_decomposition",
    "exceptional_double",
    "exceptional_r_twist",
    "exceptional_r_twist_components",
    "exceptional_z_bracket",
    "prove_exceptional_r_twist_bidegree_split",
    "prove_exceptional_r_twist_symmetric_part",
    "prove_r22_reduces_to_lifted_cross_term",
    "prove_r25_is_lie_tilde_equivariance_defect",
    "prove_rotated_is_exceptional_double_plus_r",
    "prove_koszul_dialects_agree",
    "b_field_projector",
    "prove_b_field_projector_is_a_locality_projector",
    "linear_projector",
    "prove_linear_projector_is_a_locality_projector",
    "prove_projector_differs_from_pr2_on_a_frame",
    "prove_projector_fixes_locally_exact_forms",
    "prove_theta_form_jacobi_by_citation",
    "prove_boxtimes_components_are_413",
    "prove_right_leibniz_from_r_invariance",
    "prove_roytenberg_h_is_twisted_dorfman",
    "prove_roytenberg_is_theta_double_under_poisson",
    "prove_roytenberg_reduces_to_dorfman",
    "prove_r_twisted_courant_relation",
    "prove_r_twisted_right_leibniz",
    "prove_r_twisted_symmetric_part",
    "prove_severa_twist_is_courant",
    "prove_standard_metric_invariance",
    "prove_standard_symmetric_part",
    "standard_bracket",
    "standard_metric",
    "prove_twisted_anchor_morphism",
    "prove_twisted_courant_dorfman_relation",
    "prove_twisted_invariance",
    "prove_twisted_jacobi_dh_defect",
    "prove_twisted_right_leibniz",
    "prove_general_twist_bilinearity",
    "prove_general_twist_invariance",
    "prove_general_twist_jacobi",
    "prove_general_twist_right_leibniz",
    "prove_general_twist_symmetric_part",
    "prove_theta_anchor_morphism",
    "prove_theta_courant_skew",
    "prove_theta_right_leibniz",
    "prove_theta_symmetric_part",
    "prove_theta_d_pairing_value",
    "prove_theta_invariance",
    "prove_theta_jacobi",
    "prove_twisted_symmetric_part",
    "rotated_exceptional_bracket",
    "exceptional_rotation_engine",
    "twisted_anchor",
    "twisted_bracket",
    "twisted_d",
    "twisted_metric",
    "r_term",
    "r_twisted_theta_dorfman",
    "theta_anchor",
    "theta_courant",
    "theta_dorfman",
    "prove_leibniz_from_c3",
    # facade alignment (T2-6)
    "severa_engine",
    "bridge_engine",
    "locally_exact_form",
    "exceptional_lie_tilde",
    "pi_hat",
    "transported_form_pairing",
    "basis_pairing",
    "general_twist_engine",
    "RFluxClosureDeclaration",
    "lichnerowicz_calculus",
]
