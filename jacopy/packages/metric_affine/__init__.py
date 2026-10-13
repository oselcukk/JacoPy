"""Metric-affine geometry (PDF item 11): ``∇``, torsion ``T``,
curvature ``R``, non-metricity ``Q``, connection/torsion/curvature
forms, Ricci, Ricci scalar, Einstein, Bianchi, Cartan structure
equations, Koszul, Schouten decomposition.

On an algebroid ``E`` it also carries E-connections, E-torsion and
E-curvature, the modified/projected torsion and curvature, admissible
connections, the derived algebroid, the E-Koszul formula and the
E-Bianchi / E-Cartan identities; frame-component workflows compute
the concrete coefficients.

``Metric``/``metric`` here are the package's metric CONTEXT; the
central :func:`jacopy.central.objects.metric` builds the ``g`` ATOM
(the name exported by top-level ``jacopy``). The two are bridged by
:func:`as_metric_context` until the ROADMAP 5f metric adapter lands.
"""

from jacopy.packages.metric_affine.bianchi import (
    covariant_curvature_derivative,
    covariant_jacobi_theorems,
    covariant_torsion_derivative,
    prove_bianchi_first,
    prove_bianchi_second,
    prove_ricci_identity_on_functions,
)
from jacopy.packages.metric_affine.e_connection import (
    ECurvatureExpansionDefinition,
    EConnectionScalarActionDefinition,
    ETorsionExpansionDefinition,
    e_connection,
    e_connection_engine,
    prove_e_connection_anchored_leibniz,
    prove_e_curvature_last_slot_conditional,
    prove_e_torsion_second_slot_tensorial,
    prove_pseudo_torsion_first_slot_defect,
)
from jacopy.packages.metric_affine.component_workflow import (
    ComponentInput,
)
from jacopy.packages.metric_affine.metric_affine_expansion import metric_affine_engine
from jacopy.packages.metric_affine.modified import (
    CoframeRecombinationDefinition,
    modified_torsion,
    projected_curvature,
    prove_modified_torsion_tensorial,
    prove_projected_curvature_first_slot,
    prove_projected_curvature_last_slot,
)
from jacopy.packages.metric_affine.frame_components import (
    ConnectionCoefficient,
    ConnectionForm,
    ConnectionFormEvaluationDefinition,
    FrameConnectionCoefficientDefinition,
    FramePairingSplitDefinition,
    connection_coefficient,
    connection_form,
    curvature_component_formula,
    einstein_component,
    prove_cartan_first_evaluated,
    prove_cartan_first_structure,
    prove_cartan_second_structure,
    prove_curvature_components,
    prove_ricci_components,
    prove_ricci_scalar_components,
    ricci_component,
    ricci_scalar,
    prove_connection_form_on_frame,
    prove_torsion_components,
)
from jacopy.packages.metric_affine.metric_koszul import (
    prove_generalized_koszul,
    prove_koszul_formula,
    prove_levi_civita_unique,
)
from jacopy.packages.metric_affine.metric import (
    as_metric_context,
    InverseMetricComponent,
    Metric,
    MetricCompatibilityDefinition,
    MetricInverseContractionDefinition,
    inverse_metric_component,
    MetricValue,
    MetricValueBilinearityDefinition,
    MetricValueSymmetryDefinition,
    NonMetricity,
    NonMetricityExpansionDefinition,
    TorsionFreeDefinition,
    metric,
    nonmetricity,
)
from jacopy.packages.metric_affine.rules import (
    ConnectionDirectionLinearityDefinition,
)
from jacopy.packages.metric_affine.torsion_curvature import (
    Curvature,
    CurvatureExpansionDefinition,
    Torsion,
    TorsionExpansionDefinition,
    curvature,
    prove_connection_difference_tensorial,
    prove_curvature_antisymmetry,
    prove_curvature_tensorial,
    prove_torsion_antisymmetry,
    prove_torsion_tensorial,
    torsion,
)

from jacopy.packages.metric_affine.nonmetricity_forms import (
    NonMetricityForm,
    NonMetricityFormEvaluationDefinition,
    nonmetricity_form,
    prove_nonmetricity_form_cartan,
    prove_nonmetricity_form_components,
    prove_nonmetricity_form_symmetric,
    prove_nonmetricity_form_tensorial,
)
from jacopy.packages.metric_affine.e_cartan import (
    prove_e_cartan_first,
    prove_e_cartan_second,
)

# Facade alignment (independent audit of commit 0b00e1b, item T2-6): the remaining user-path
# constructors, prove_* theorems and package-specific declarations/rules.
from jacopy.packages.metric_affine.admissible import (
    AdmissibilityDeclaration,
    ModifiedTorsionFreeDeclaration,
    modified_bracket,
    prove_admissible_implies_metric_compatible,
    prove_courant_locality_generator,
    prove_metric_compatible_implies_admissible,
    prove_modified_bracket_left_leibniz,
    prove_modified_torsion_symmetric_part_vanishes,
    prove_torsion_free_implies_admissible,
)
from jacopy.packages.metric_affine.derived import (
    d_derived,
    derived_algebroid,
    derived_engine,
    derived_is_projected,
    lie_derived,
    prove_derived_magic_on_forms,
    prove_derived_magic_on_functions,
    prove_projected_d_squared_associator,
    prove_projected_d_squared_on_functions,
)
from jacopy.packages.metric_affine.e_bianchi import (
    anomaly_direction,
    covariant_modified_torsion_derivative,
    projected_modified_bracket,
    prove_e_bianchi_first_identity,
    prove_e_bianchi_second_identity,
)
from jacopy.packages.metric_affine.e_cartan import (
    e_cartan_engine,
    e_cartan_first_sides,
    e_cartan_second_sides,
)
from jacopy.packages.metric_affine.e_koszul import (
    EKoszulDeclaration,
    e_nonmetricity,
    fundamental_theorem_components,
    koszul_correction,
    prove_e_generalized_koszul,
    prove_e_koszul_admissible_implies_compatible,
    prove_e_koszul_admissible_implies_torsion_free,
    prove_e_koszul_formula,
    prove_e_koszul_unique_under_null_locality,
    prove_fundamental_theorem_components,
    prove_koszul_reference_decomposition,
    prove_metric_lie_derivative_identity,
    prove_projectors_agree_on_coboundary_values,
)
from jacopy.packages.metric_affine.metric import (
    inverse_metric_component_named,
)
from jacopy.packages.metric_affine.modified import (
    generalized_ricci_anomaly,
    prove_generalized_ricci_identity,
)
from jacopy.packages.metric_affine.nonmetricity_forms import (
    nonmetricity_form_component_formula,
)

__all__ = [
    "NonMetricityForm",
    "NonMetricityFormEvaluationDefinition",
    "nonmetricity_form",
    "prove_nonmetricity_form_cartan",
    "prove_nonmetricity_form_components",
    "prove_nonmetricity_form_symmetric",
    "prove_nonmetricity_form_tensorial",
    "prove_e_cartan_first",
    "prove_e_cartan_second",
    "ConnectionDirectionLinearityDefinition",
    "metric_affine_engine",
    "Curvature",
    "CurvatureExpansionDefinition",
    "Torsion",
    "TorsionExpansionDefinition",
    "curvature",
    "torsion",
    "prove_connection_difference_tensorial",
    "prove_curvature_antisymmetry",
    "prove_curvature_tensorial",
    "prove_torsion_antisymmetry",
    "prove_torsion_tensorial",
    "Metric",
    "MetricCompatibilityDefinition",
    "MetricValue",
    "MetricValueBilinearityDefinition",
    "MetricValueSymmetryDefinition",
    "NonMetricity",
    "NonMetricityExpansionDefinition",
    "TorsionFreeDefinition",
    "ComponentInput",
    "as_metric_context",
    "metric",
    "nonmetricity",
    "prove_generalized_koszul",
    "prove_koszul_formula",
    "prove_levi_civita_unique",
    "covariant_curvature_derivative",
    "covariant_jacobi_theorems",
    "covariant_torsion_derivative",
    "prove_bianchi_first",
    "prove_bianchi_second",
    "prove_ricci_identity_on_functions",
    "ConnectionCoefficient",
    "ConnectionForm",
    "ConnectionFormEvaluationDefinition",
    "FrameConnectionCoefficientDefinition",
    "FramePairingSplitDefinition",
    "connection_coefficient",
    "connection_form",
    "prove_cartan_first_evaluated",
    "prove_cartan_first_structure",
    "prove_cartan_second_structure",
    "prove_curvature_components",
    "prove_ricci_components",
    "curvature_component_formula",
    "ricci_component",
    "ricci_scalar",
    "einstein_component",
    "prove_ricci_scalar_components",
    "InverseMetricComponent",
    "MetricInverseContractionDefinition",
    "inverse_metric_component",
    "ECurvatureExpansionDefinition",
    "EConnectionScalarActionDefinition",
    "ETorsionExpansionDefinition",
    "e_connection",
    "e_connection_engine",
    "prove_e_connection_anchored_leibniz",
    "prove_e_curvature_last_slot_conditional",
    "prove_e_torsion_second_slot_tensorial",
    "prove_pseudo_torsion_first_slot_defect",
    "CoframeRecombinationDefinition",
    "modified_torsion",
    "projected_curvature",
    "prove_modified_torsion_tensorial",
    "prove_projected_curvature_first_slot",
    "prove_projected_curvature_last_slot",
    "prove_connection_form_on_frame",
    "prove_torsion_components",
    # facade alignment (T2-6)
    "AdmissibilityDeclaration",
    "ModifiedTorsionFreeDeclaration",
    "modified_bracket",
    "prove_admissible_implies_metric_compatible",
    "prove_courant_locality_generator",
    "prove_metric_compatible_implies_admissible",
    "prove_modified_bracket_left_leibniz",
    "prove_modified_torsion_symmetric_part_vanishes",
    "prove_torsion_free_implies_admissible",
    "d_derived",
    "derived_algebroid",
    "derived_engine",
    "derived_is_projected",
    "lie_derived",
    "prove_derived_magic_on_forms",
    "prove_derived_magic_on_functions",
    "prove_projected_d_squared_associator",
    "prove_projected_d_squared_on_functions",
    "anomaly_direction",
    "covariant_modified_torsion_derivative",
    "projected_modified_bracket",
    "prove_e_bianchi_first_identity",
    "prove_e_bianchi_second_identity",
    "e_cartan_engine",
    "e_cartan_first_sides",
    "e_cartan_second_sides",
    "EKoszulDeclaration",
    "e_nonmetricity",
    "fundamental_theorem_components",
    "koszul_correction",
    "prove_e_generalized_koszul",
    "prove_e_koszul_admissible_implies_compatible",
    "prove_e_koszul_admissible_implies_torsion_free",
    "prove_e_koszul_formula",
    "prove_e_koszul_unique_under_null_locality",
    "prove_fundamental_theorem_components",
    "prove_koszul_reference_decomposition",
    "prove_metric_lie_derivative_identity",
    "prove_projectors_agree_on_coboundary_values",
    "inverse_metric_component_named",
    "generalized_ricci_anomaly",
    "prove_generalized_ricci_identity",
    "nonmetricity_form_component_formula",
]
