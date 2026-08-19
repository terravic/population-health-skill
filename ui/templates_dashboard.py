"""
Surface 1: Executive Overview & National Heat Map Dashboard.
Renders Looker-style multi-tile dashboard:
- KPI Summary Row (Baseline Cost $9,080, Avg Clinical HCC 1.10, Unpriced Risk Gap +$6,400/mbr)
- US National Risk Heat Map image
- Regional Hot-Spots summary
- Quick Action buttons for Florida, California drill-downs, and Actuarial Enrichment.
"""

from typing import Any, Dict, List
from ui.a2ui_catalog import (
    begin_rendering,
    surface_update,
    data_model_update,
    make_text,
    make_column,
    make_row,
    make_card,
    make_button,
    make_image,
    make_icon,
    make_divider,
    format_a2ui_payload
)


def get_executive_dashboard_surface(
    total_lives: int = 50000,
    baseline_cost: float = 9080.0,
    baseline_hcc: float = 1.10,
    unpriced_gap: str = "+$6,400/mbr",
    map_image_url: str = "assets/us_risk_heatmap.png"
) -> List[Dict[str, Any]]:
    """Builds A2UI v0.8 message array for Surface 1 (Executive Dashboard)."""
    surface_id = "executive-dashboard"
    root_id = "dash_root"

    components = [
        # Root Column Layout
        make_column(
            "dash_root",
            [
                "header_card",
                "kpi_card",
                "map_container_card",
                "hotspots_card",
                "action_card"
            ],
            alignment="start"
        ),

        # Header Card
        make_card("header_card", "header_col", elevation=1),
        make_column("header_col", ["header_title", "header_subtitle"]),
        make_text("header_title", "Population Health — National Executive Overview", usage_hint="h2"),
        make_text(
            "header_subtitle",
            "Interactive Non-Clinical Environmental Risk Intelligence & Actuarial Liability Dashboard",
            usage_hint="caption"
        ),

        # KPI Container Card
        make_card("kpi_card", "kpi_row", elevation=2),
        make_row("kpi_row", ["kpi_lives", "kpi_cost", "kpi_hcc", "kpi_liability"], distribution="spaceEvenly"),

        # KPI 1: Monitored Lives
        make_column("kpi_lives", ["kpi_lives_title", "kpi_lives_val"]),
        make_text("kpi_lives_title", "Monitored Population", usage_hint="caption"),
        make_text("kpi_lives_val", f"{total_lives:,} Lives", usage_hint="h3"),

        # KPI 2: Baseline Cost
        make_column("kpi_cost", ["kpi_cost_title", "kpi_cost_val"]),
        make_text("kpi_cost_title", "Baseline Median Cost", usage_hint="caption"),
        make_text("kpi_cost_val", f"${baseline_cost:,.0f}", usage_hint="h3"),

        # KPI 3: Avg Clinical HCC
        make_column("kpi_hcc", ["kpi_hcc_title", "kpi_hcc_val"]),
        make_text("kpi_hcc_title", "Avg Clinical HCC Risk", usage_hint="caption"),
        make_text("kpi_hcc_val", f"{baseline_hcc:.2f}", usage_hint="h3"),

        # KPI 4: Unpriced Liability Gap
        make_column("kpi_liability", ["kpi_liab_title", "kpi_liab_val"]),
        make_text("kpi_liab_title", "Unpriced Risk Gap", usage_hint="caption"),
        make_text("kpi_liab_val", unpriced_gap, usage_hint="h3"),

        # Map Visual Card
        make_card("map_container_card", "map_inner_col", elevation=2),
        make_column("map_inner_col", ["map_title", "map_image", "map_caption"]),
        make_text("map_title", "USA Environmental Risk Heat Map (Continuous Exposure Index)", usage_hint="h3"),
        make_image(
            "map_image",
            url=map_image_url,
            alt_text="US National Risk Heat Map (Red/Orange Gradient)",
            fit="contain",
            usage_hint="largeFeature"
        ),
        make_text(
            "map_caption",
            "High unpriced environmental liability identified in Gulf Coast, Central Valley CA, and Florida Coast ZIPs.",
            usage_hint="caption"
        ),

        # Top Regional Hot-Spots Summary Card
        make_card("hotspots_card", "hotspots_col", elevation=1),
        make_column("hotspots_col", ["hotspots_title", "hotspot_1", "hotspot_2", "hotspot_3"]),
        make_text("hotspots_title", "Identified High-Liability Regional Corridors", usage_hint="h3"),
        make_text(
            "hotspot_1",
            "🔴 Florida Coast (FL): High particulate pollution & storm exposure (Risk: 0.88 | Unpriced Cost: +$4,820/mbr)",
            usage_hint="body"
        ),
        make_text(
            "hotspot_2",
            "🔴 Central Valley (CA): Agricultural dust & PM2.5 particulate burden (Risk: 0.84 | Unpriced Cost: +$3,720/mbr)",
            usage_hint="body"
        ),
        make_text(
            "hotspot_3",
            "🔴 Gulf Coast (TX): Industrial emissions & transit access barriers (Risk: 0.81 | Unpriced Cost: +$3,320/mbr)",
            usage_hint="body"
        ),

        # Interactive Actions Card
        make_card("action_card", "action_inner_col", elevation=1),
        make_column("action_inner_col", ["action_prompt", "action_row"]),
        make_text("action_prompt", "Cohort Drill-Down & Actuarial Actions:", usage_hint="caption"),
        make_row("action_row", ["btn_fl", "btn_ca", "btn_enrich"], distribution="start"),

        # Action 1: Florida Drilldown
        make_button(
            "btn_fl",
            "btn_fl_txt",
            action_name="get_cohort_stats",
            action_context={"state": "FL", "age_min": 40, "age_max": 50},
            primary=True
        ),
        make_text("btn_fl_txt", "Drilldown: Florida Hot Spot (Age 40-50)", usage_hint="body"),

        # Action 2: California Drilldown
        make_button(
            "btn_ca",
            "btn_ca_txt",
            action_name="get_cohort_stats",
            action_context={"state": "CA", "age_min": 40, "age_max": 50},
            primary=False
        ),
        make_text("btn_ca_txt", "Drilldown: California Hot Spot (Age 40-50)", usage_hint="body"),

        # Action 3: Actuarial Enrichment
        make_button(
            "btn_enrich",
            "btn_enrich_txt",
            action_name="run_actuarial_enrichment",
            action_context={"target": "non_clinical_proxies"},
            primary=False
        ),
        make_text("btn_enrich_txt", "Run Actuarial Enrichment (PQA/PEA)", usage_hint="body")
    ]

    messages = [
        begin_rendering(surface_id, root_id),
        surface_update(surface_id, components),
        data_model_update(surface_id, path="/", contents=[])
    ]
    return messages


def render_dashboard_a2ui() -> str:
    """Returns the formatted <a2ui-json> string for the Executive Dashboard."""
    return format_a2ui_payload(get_executive_dashboard_surface())
