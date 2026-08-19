"""
Surface 2: Cohort Comparison Card.
Displays side-by-side metric comparison tiles for the selected cohort vs. population baseline:
- Median Cost ($13,900 vs $9,080 | +53.1%)
- Mean Clinical HCC (0.93 vs 1.10 | -15.5% Paradox)
- COPD Prevalence (14.2% vs 8.2% | +73.2%)
- Environmental Risk Index (0.88 vs 0.42 | +109.5%)
- Primary Action: [Generate Intervention]
"""

from typing import Any, Dict, List, Optional
from ui.a2ui_catalog import (
    begin_rendering,
    surface_update,
    data_model_update,
    make_text,
    make_column,
    make_row,
    make_card,
    make_button,
    make_icon,
    make_divider,
    format_a2ui_payload
)


def get_cohort_comparison_surface(
    cohort_title: str = "Florida High-Risk Corridor (Age 40–50)",
    cohort_zips: str = "33010, 33142 (Miami-Dade / Hialeah)",
    cohort_n: int = 261,
    cohort_cost: float = 13900.0,
    baseline_cost: float = 9080.0,
    cohort_hcc: float = 0.93,
    baseline_hcc: float = 1.10,
    cohort_copd: float = 0.142,
    baseline_copd: float = 0.082,
    cohort_risk: float = 0.88,
    baseline_risk: float = 0.42,
    state: str = "FL",
    age_min: int = 40,
    age_max: int = 50
) -> List[Dict[str, Any]]:
    """Builds A2UI v0.8 message array for Surface 2 (Cohort Comparison Card)."""
    surface_id = "cohort-comparison"
    root_id = "cohort_root"

    cost_delta = ((cohort_cost - baseline_cost) / baseline_cost) * 100
    hcc_delta = ((cohort_hcc - baseline_hcc) / baseline_hcc) * 100
    copd_delta = ((cohort_copd - baseline_copd) / baseline_copd) * 100
    risk_delta = ((cohort_risk - baseline_risk) / baseline_risk) * 100

    components = [
        # Root Layout
        make_column(
            "cohort_root",
            [
                "cohort_header_card",
                "metrics_grid_card",
                "paradox_insight_card",
                "cohort_action_card"
            ],
            alignment="start"
        ),

        # Header Card
        make_card("cohort_header_card", "c_hdr_col", elevation=1),
        make_column("c_hdr_col", ["c_hdr_title", "c_hdr_sub"]),
        make_text("c_hdr_title", f"Cohort Deep-Dive: {cohort_title}", usage_hint="h2"),
        make_text(
            "c_hdr_sub",
            f"Target Population: N={cohort_n:,} Members | Filtered ZIPs: {cohort_zips} | State: {state}",
            usage_hint="caption"
        ),

        # Metrics Grid Card (Side-by-side comparison)
        make_card("metrics_grid_card", "metrics_grid_col", elevation=2),
        make_column("metrics_grid_col", ["m_row_title", "m_row_1", "m_row_2"]),
        make_text("m_row_title", "Actuarial & Clinical Disparity Breakdown", usage_hint="h3"),

        # Row 1: Cost & HCC
        make_row("m_row_1", ["tile_cost", "tile_hcc"], distribution="spaceEvenly"),

        # Tile 1: Cost Disparity
        make_column("tile_cost", ["cost_label", "cost_comp_val", "cost_delta_badge"]),
        make_text("cost_label", "Median Incurred Claims Cost", usage_hint="caption"),
        make_text("cost_comp_val", f"${cohort_cost:,.0f} vs ${baseline_cost:,.0f}", usage_hint="h3"),
        make_text("cost_delta_badge", f"▲ +{cost_delta:.1f}% (+${cohort_cost - baseline_cost:,.0f}/mbr)", usage_hint="callout"),

        # Tile 2: Clinical HCC Score
        make_column("tile_hcc", ["hcc_label", "hcc_comp_val", "hcc_delta_badge"]),
        make_text("hcc_label", "Average Clinical HCC Risk Score", usage_hint="caption"),
        make_text("hcc_comp_val", f"{cohort_hcc:.2f} vs {baseline_hcc:.2f}", usage_hint="h3"),
        make_text("hcc_delta_badge", f"▼ {hcc_delta:.1f}% (Unpriced Risk Paradox)", usage_hint="callout"),

        # Row 2: COPD Prevalence & Environmental Risk
        make_row("m_row_2", ["tile_copd", "tile_env"], distribution="spaceEvenly"),

        # Tile 3: COPD Prevalence
        make_column("tile_copd", ["copd_label", "copd_comp_val", "copd_delta_badge"]),
        make_text("copd_label", "COPD / Chronic Respiratory Rate", usage_hint="caption"),
        make_text("copd_comp_val", f"{cohort_copd*100:.1f}% vs {baseline_copd*100:.1f}%", usage_hint="h3"),
        make_text("copd_delta_badge", f"▲ +{copd_delta:.1f}% Relative Prevalence", usage_hint="callout"),

        # Tile 4: Environmental Risk Index
        make_column("tile_env", ["env_label", "env_comp_val", "env_delta_badge"]),
        make_text("env_label", "Composite Environmental Risk Index", usage_hint="caption"),
        make_text("env_comp_val", f"{cohort_risk:.2f} vs {baseline_risk:.2f}", usage_hint="h3"),
        make_text("env_delta_badge", f"▲ +{risk_delta:.1f}% Above Normal Baseline", usage_hint="callout"),

        # Paradox Insight Callout Card
        make_card("paradox_insight_card", "paradox_col", elevation=1),
        make_column("paradox_col", ["p_title", "p_body_1", "p_body_2"]),
        make_text("p_title", "Actuarial Paradox Detected", usage_hint="h3"),
        make_text(
            "p_body_1",
            "Members in this cohort exhibit 53.1% higher median medical costs despite having a 15.5% lower CMS-HCC clinical risk score.",
            usage_hint="body"
        ),
        make_text(
            "p_body_2",
            "Root Cause: High microclimate particulate exposure (AQI PM2.5 > 135) combined with structural transit barriers causes frequent unmanaged respiratory exacerbations and avoidable emergency room utilization.",
            usage_hint="body"
        ),

        # Cohort Action Card
        make_card("cohort_action_card", "c_act_col", elevation=1),
        make_column("c_act_col", ["c_act_prompt", "c_act_btn_row"]),
        make_text("c_act_prompt", "Next Best Clinical & Underwriting Actions:", usage_hint="caption"),
        make_row("c_act_btn_row", ["btn_gen_intervention", "btn_back_dash"], distribution="start"),

        # Button 1: Generate Intervention (Primary)
        make_button(
            "btn_gen_intervention",
            "btn_gen_txt",
            action_name="generate_intervention",
            action_context={
                "cohort_id": f"{state}_{age_min}_{age_max}",
                "state": state,
                "age_min": age_min,
                "age_max": age_max,
                "cohort_cost": cohort_cost,
                "unpriced_liability": cohort_cost - baseline_cost
            },
            primary=True
        ),
        make_text("btn_gen_txt", "Generate Tailored Interventions (PIE Engine)", usage_hint="body"),

        # Button 2: Back to Dashboard
        make_button(
            "btn_back_dash",
            "btn_back_txt",
            action_name="get_dashboard",
            action_context={},
            primary=False
        ),
        make_text("btn_back_txt", "Back to National Overview", usage_hint="body")
    ]

    messages = [
        begin_rendering(surface_id, root_id),
        surface_update(surface_id, components),
        data_model_update(surface_id, path="/", contents=[])
    ]
    return messages


def render_cohort_a2ui(**kwargs) -> str:
    """Returns the formatted <a2ui-json> string for the Cohort Comparison Card."""
    return format_a2ui_payload(get_cohort_comparison_surface(**kwargs))
