"""
Vega-Lite JSON specifications for interactive visualizations:
1. US State Choropleth Risk Heat Map (TopoJSON geoshapes)
2. Cohort vs Baseline Comparison Grouped Bar Chart
3. Cost vs HCC Clinical Risk Disparity Scatter / Bubble Chart
"""

from typing import Any, Dict


def get_us_choropleth_vega_spec() -> Dict[str, Any]:
    """Returns Vega-Lite spec for US State Choropleth Risk Map."""
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "width": 750,
        "height": 450,
        "background": "#0f172a",
        "title": {
            "text": "Population Health US Environmental Risk Heat Map",
            "subtitle": "Composite Non-Clinical Exposure Index (AQI PM2.5 + Pollen + Transit Barrier)",
            "color": "#f8fafc",
            "subtitleColor": "#94a3b8"
        },
        "projection": {"type": "albersUsa"},
        "data": {
            "url": "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json",
            "format": {"type": "topojson", "feature": "states"}
        },
        "transform": [
            {
                "lookup": "id",
                "from": {
                    "data": {
                        "values": [
                            {"fips": "12", "state": "FL", "risk": 0.88, "tier": "High Risk"},
                            {"fips": "06", "state": "CA", "risk": 0.84, "tier": "High Risk"},
                            {"fips": "48", "state": "TX", "risk": 0.81, "tier": "High Risk"},
                            {"fips": "39", "state": "OH", "risk": 0.78, "tier": "High Risk"},
                            {"fips": "13", "state": "GA", "risk": 0.68, "tier": "Medium-High"},
                            {"fips": "37", "state": "NC", "risk": 0.64, "tier": "Medium-High"},
                            {"fips": "04", "state": "AZ", "risk": 0.62, "tier": "Medium-High"},
                            {"fips": "26", "state": "MI", "risk": 0.58, "tier": "Medium-High"},
                            {"fips": "36", "state": "NY", "risk": 0.48, "tier": "Moderate"},
                            {"fips": "42", "state": "PA", "risk": 0.45, "tier": "Moderate"},
                            {"fips": "17", "state": "IL", "risk": 0.41, "tier": "Moderate"},
                            {"fips": "50", "state": "VT", "risk": 0.18, "tier": "Low Risk"},
                            {"fips": "33", "state": "NH", "risk": 0.22, "tier": "Low Risk"},
                            {"fips": "27", "state": "MN", "risk": 0.25, "tier": "Low Risk"},
                            {"fips": "08", "state": "CO", "risk": 0.28, "tier": "Low Risk"}
                        ]
                    },
                    "key": "fips",
                    "fields": ["state", "risk", "tier"]
                }
            }
        ],
        "mark": {"type": "geoshape", "stroke": "#334155", "strokeWidth": 1.2},
        "encoding": {
            "color": {
                "field": "risk",
                "type": "quantitative",
                "scale": {
                    "range": ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026", "#800026"],
                    "domain": [0.0, 1.0]
                },
                "legend": {
                    "title": "Environmental Risk Index",
                    "labelColor": "#cbd5e1",
                    "titleColor": "#f8fafc",
                    "orient": "bottom-right"
                }
            },
            "tooltip": [
                {"field": "state", "type": "nominal", "title": "State"},
                {"field": "risk", "type": "quantitative", "title": "Composite Risk", "format": ".2f"},
                {"field": "tier", "type": "nominal", "title": "Risk Tier"}
            ]
        }
    }


def get_cohort_comparison_vega_spec(
    cohort_cost: float = 13900.0,
    baseline_cost: float = 9080.0,
    cohort_hcc: float = 0.93,
    baseline_hcc: float = 1.10
) -> Dict[str, Any]:
    """Returns Vega-Lite spec for Cohort vs Baseline Disparity."""
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "width": 450,
        "height": 260,
        "background": "#1e293b",
        "title": {
            "text": "Florida High-Risk Cohort vs Population Baseline",
            "color": "#f8fafc"
        },
        "data": {
            "values": [
                {"Metric": "Median Claims Cost ($)", "Group": "FL Hotspot Cohort", "Value": cohort_cost},
                {"Metric": "Median Claims Cost ($)", "Group": "Population Baseline", "Value": baseline_cost},
                {"Metric": "Clinical HCC Score (x10k)", "Group": "FL Hotspot Cohort", "Value": cohort_hcc * 10000},
                {"Metric": "Clinical HCC Score (x10k)", "Group": "Population Baseline", "Value": baseline_hcc * 10000}
            ]
        },
        "mark": {"type": "bar", "cornerRadiusEnd": 4},
        "encoding": {
            "x": {"field": "Metric", "type": "nominal", "axis": {"labelColor": "#cbd5e1", "title": None}},
            "y": {"field": "Value", "type": "quantitative", "axis": {"labelColor": "#cbd5e1", "gridColor": "#334155"}},
            "xOffset": {"field": "Group"},
            "color": {
                "field": "Group",
                "type": "nominal",
                "scale": {"range": ["#ef4444", "#38bdf8"]},
                "legend": {"labelColor": "#cbd5e1", "titleColor": "#f8fafc"}
            },
            "tooltip": [
                {"field": "Group", "type": "nominal"},
                {"field": "Metric", "type": "nominal"},
                {"field": "Value", "type": "quantitative"}
            ]
        }
    }


def get_cost_vs_hcc_scatter_spec() -> Dict[str, Any]:
    """Returns Vega-Lite spec for Claims Cost vs HCC Risk Score scatter chart."""
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "width": 450,
        "height": 280,
        "background": "#1e293b",
        "title": {
            "text": "Incurred Cost vs Clinical HCC Risk by Microclimate",
            "color": "#f8fafc"
        },
        "data": {
            "url": "data/synthetic_members.json"
        },
        "transform": [
            {"sample": 500}
        ],
        "mark": {"type": "circle", "opacity": 0.75, "size": 60},
        "encoding": {
            "x": {
                "field": "hcc_score",
                "type": "quantitative",
                "title": "Clinical CMS-HCC Risk Score",
                "axis": {"labelColor": "#cbd5e1", "titleColor": "#f8fafc"}
            },
            "y": {
                "field": "total_cost",
                "type": "quantitative",
                "title": "Annual Total Incurred Claims ($)",
                "scale": {"type": "log"},
                "axis": {"labelColor": "#cbd5e1", "titleColor": "#f8fafc"}
            },
            "color": {
                "field": "state",
                "type": "nominal",
                "scale": {
                    "domain": ["FL", "CA", "TX", "OH", "NY", "VT"],
                    "range": ["#ef4444", "#f97316", "#fbbf24", "#a855f7", "#38bdf8", "#10b981"]
                },
                "legend": {"labelColor": "#cbd5e1", "titleColor": "#f8fafc"}
            },
            "tooltip": [
                {"field": "member_id", "type": "nominal", "title": "Member"},
                {"field": "state", "type": "nominal", "title": "State"},
                {"field": "zip", "type": "nominal", "title": "ZIP"},
                {"field": "hcc_score", "type": "quantitative", "title": "HCC Score"},
                {"field": "total_cost", "type": "quantitative", "title": "Claims Cost ($)", "format": "$,.0f"}
            ]
        }
    }
