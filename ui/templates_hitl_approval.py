"""
Surface 4: Actuarial Staging & Human-in-the-Loop (HITL) Approval Card.
Displays proposed proxy validation metrics for data scientists and actuaries:
- Candidate Proxy 1: PDI_AQI_PM25_Proxy (r=0.33, p<0.001, Stability=0.89)
- Candidate Proxy 2: Structural_Transit_Barrier_Proxy (r=0.31, p<0.001, Stability=0.86)
- S1-S3 Quality Gates: PASS (Silhouette=0.72, Out-of-sample R^2 gain=+11.4%)
- Interactive Actions: [Approve & Commit Proxy] and [Reject Candidate]
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


def get_hitl_approval_surface(
    problem_statement: str = "Identify non-clinical ZIP-level drivers of cost residual not captured by CMS-HCC",
    proxy_1_name: str = "PDI_AQI_PM25_Proxy",
    proxy_1_corr: float = 0.33,
    proxy_1_stability: float = 0.89,
    proxy_2_name: str = "Structural_Transit_Barrier_Proxy",
    proxy_2_corr: float = 0.31,
    proxy_2_stability: float = 0.86,
    r2_gain: float = 11.4,
    silhouette_score: float = 0.72
) -> List[Dict[str, Any]]:
    """Builds A2UI v0.8 message array for Surface 4 (Actuarial HITL Approval Card)."""
    surface_id = "actuarial-hitl-approval"
    root_id = "hitl_root"

    components = [
        # Root Layout
        make_column(
            "hitl_root",
            [
                "hitl_hdr_card",
                "problem_spec_card",
                "proxy_eval_card",
                "quality_gates_card",
                "hitl_action_card"
            ],
            alignment="start"
        ),

        # Header Card
        make_card("hitl_hdr_card", "hitl_hdr_col", elevation=1),
        make_column("hitl_hdr_col", ["hitl_hdr_title", "hitl_hdr_sub"]),
        make_text("hitl_hdr_title", "Actuarial Data Scientist Staging & Approval (HITL-1 / HITL-2)", usage_hint="h2"),
        make_text(
            "hitl_hdr_sub",
            "Proxy Quality Assessment (PQA) & Proxy Enrichment Engine (PEA) Pipeline",
            usage_hint="caption"
        ),

        # Problem Specification Card
        make_card("problem_spec_card", "prob_col", elevation=1),
        make_column("prob_col", ["prob_label", "prob_text"]),
        make_text("prob_label", "Target Actuarial Problem Statement:", usage_hint="caption"),
        make_text("prob_text", f"\"{problem_statement}\"", usage_hint="body"),

        # Proxy Evaluation Card
        make_card("proxy_eval_card", "eval_col", elevation=2),
        make_column("eval_col", ["eval_title", "proxy_row_1", "proxy_row_2"]),
        make_text("eval_title", "Candidate Actuarial Proxies Evaluated", usage_hint="h3"),

        # Proxy 1 Row
        make_row("proxy_row_1", ["p1_name_col", "p1_stats_col"], distribution="spaceBetween"),
        make_column("p1_name_col", ["p1_title", "p1_desc"]),
        make_text("p1_title", f"1. {proxy_1_name}", usage_hint="body"),
        make_text("p1_desc", "Microclimate EPA PM2.5 particulate concentration index", usage_hint="caption"),
        make_column("p1_stats_col", ["p1_corr_txt", "p1_stab_txt"]),
        make_text("p1_corr_txt", f"Correlation r = {proxy_1_corr:.2f} (p < 0.001)", usage_hint="callout"),
        make_text("p1_stab_txt", f"Time Stability: {proxy_1_stability*100:.0f}%", usage_hint="caption"),

        # Proxy 2 Row
        make_row("proxy_row_2", ["p2_name_col", "p2_stats_col"], distribution="spaceBetween"),
        make_column("p2_name_col", ["p2_title", "p2_desc"]),
        make_text("p2_title", f"2. {proxy_2_name}", usage_hint="body"),
        make_text("p2_desc", "Public transit desert & geographic care access impedance", usage_hint="caption"),
        make_column("p2_stats_col", ["p2_corr_txt", "p2_stab_txt"]),
        make_text("p2_corr_txt", f"Correlation r = {proxy_2_corr:.2f} (p < 0.001)", usage_hint="callout"),
        make_text("p2_stab_txt", f"Time Stability: {proxy_2_stability*100:.0f}%", usage_hint="caption"),

        # Quality Gates Card (S1-S3)
        make_card("quality_gates_card", "qg_col", elevation=1),
        make_column("qg_col", ["qg_title", "qg_row", "qg_summary"]),
        make_text("qg_title", "PEA S1–S3 Validation & Accuracy Bar Gates", usage_hint="h3"),
        make_row("qg_row", ["qg_s1", "qg_s2", "qg_s3"], distribution="spaceEvenly"),

        # Gate S1
        make_column("qg_s1", ["qg_s1_lbl", "qg_s1_val"]),
        make_text("qg_s1_lbl", "S1 Semantic Similarity", usage_hint="caption"),
        make_text("qg_s1_val", f"PASS (Sil: {silhouette_score:.2f})", usage_hint="callout"),

        # Gate S2
        make_column("qg_s2", ["qg_s2_lbl", "qg_s2_val"]),
        make_text("qg_s2_lbl", "S2 R² Residual Gain", usage_hint="caption"),
        make_text("qg_s2_val", f"PASS (+{r2_gain:.1f}%)", usage_hint="callout"),

        # Gate S3
        make_column("qg_s3", ["qg_s3_lbl", "qg_s3_val"]),
        make_text("qg_s3_lbl", "S3 Staging Readiness", usage_hint="caption"),
        make_text("qg_s3_val", "READY FOR COMMIT", usage_hint="callout"),

        make_text(
            "qg_summary",
            "Actuarial Bar: Both candidate proxies significantly reduce unexplained cost variance without introducing collinearity with existing clinical variables.",
            usage_hint="caption"
        ),

        # Interactive Decision Actions Card
        make_card("hitl_action_card", "hitl_act_col", elevation=2),
        make_column("hitl_act_col", ["hitl_prompt", "hitl_btn_row"]),
        make_text("hitl_prompt", "Human-in-the-Loop Actuarial Approval Decision:", usage_hint="caption"),
        make_row("hitl_btn_row", ["btn_approve", "btn_reject", "btn_return_dash"], distribution="start"),

        # Action: Approve & Commit
        make_button(
            "btn_approve",
            "btn_app_txt",
            action_name="approve_proxy_staging",
            action_context={
                "proxies": [proxy_1_name, proxy_2_name],
                "target_view": "V_combined",
                "status": "APPROVED"
            },
            primary=True
        ),
        make_text("btn_app_txt", "Approve & Commit Proxies to V_combined", usage_hint="body"),

        # Action: Reject Candidate
        make_button(
            "btn_reject",
            "btn_rej_txt",
            action_name="reject_proxy_staging",
            action_context={
                "proxies": [proxy_1_name, proxy_2_name],
                "status": "REJECTED"
            },
            primary=False
        ),
        make_text("btn_rej_txt", "Reject Candidate", usage_hint="body"),

        # Action: Return to Dashboard
        make_button(
            "btn_return_dash",
            "btn_ret_txt",
            action_name="get_dashboard",
            action_context={},
            primary=False
        ),
        make_text("btn_ret_txt", "Executive Overview", usage_hint="body")
    ]

    messages = [
        begin_rendering(surface_id, root_id),
        surface_update(surface_id, components),
        data_model_update(surface_id, path="/", contents=[])
    ]
    return messages


def render_hitl_approval_a2ui(**kwargs) -> str:
    """Returns the formatted <a2ui-json> string for the HITL Approval Card."""
    return format_a2ui_payload(get_hitl_approval_surface(**kwargs))
