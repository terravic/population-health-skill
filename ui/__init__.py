"""
UI Package for Population Health Skill.
"""

from ui.a2ui_catalog import (
    begin_rendering,
    surface_update,
    data_model_update,
    format_a2ui_payload
)
from ui.templates_dashboard import (
    get_executive_dashboard_surface,
    render_dashboard_a2ui
)
from ui.templates_cohort import (
    get_cohort_comparison_surface,
    render_cohort_a2ui
)
from ui.templates_interventions import (
    get_actionable_interventions_surface,
    render_interventions_a2ui
)
from ui.templates_hitl_approval import (
    get_hitl_approval_surface,
    render_hitl_approval_a2ui
)
from ui.vega_specs import (
    get_us_choropleth_vega_spec,
    get_cohort_comparison_vega_spec,
    get_cost_vs_hcc_scatter_spec
)

__all__ = [
    "begin_rendering",
    "surface_update",
    "data_model_update",
    "format_a2ui_payload",
    "get_executive_dashboard_surface",
    "render_dashboard_a2ui",
    "get_cohort_comparison_surface",
    "render_cohort_a2ui",
    "get_actionable_interventions_surface",
    "render_interventions_a2ui",
    "get_hitl_approval_surface",
    "render_hitl_approval_a2ui",
    "get_us_choropleth_vega_spec",
    "get_cohort_comparison_vega_spec",
    "get_cost_vs_hcc_scatter_spec"
]
