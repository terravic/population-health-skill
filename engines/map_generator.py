#!/usr/bin/env python3
"""
Map Generator & Asset Provider for Population Health Skill.
Generates:
1. assets/us_risk_heatmap.png: High-resolution Geographic US Risk Heat Map using real state boundary polygons
2. assets/regional_hotspots.png: 4-panel regional zoom chart (FL, CA, TX, OH)
"""

import json
import math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.colors as mcolors
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(ASSETS_DIR, exist_ok=True)

STATE_NAME_TO_CODE = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC', 'Florida': 'FL',
    'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN',
    'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
    'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND',
    'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
    'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI',
    'Wyoming': 'WY', 'Puerto Rico': 'PR'
}

DEFAULT_STATE_RISKS = {
    "FL": 0.88, "CA": 0.84, "TX": 0.81, "OH": 0.78,
    "GA": 0.68, "NC": 0.64, "AZ": 0.62, "MI": 0.58, "LA": 0.65, "MS": 0.63, "AL": 0.62,
    "SC": 0.60, "TN": 0.59, "KY": 0.57, "WV": 0.61, "AR": 0.60, "NV": 0.59, "NM": 0.58,
    "IN": 0.58, "MO": 0.56, "OK": 0.57,
    "NY": 0.48, "PA": 0.45, "IL": 0.41, "VA": 0.46, "MD": 0.44, "NJ": 0.47, "DE": 0.42,
    "DC": 0.45, "WI": 0.43, "KS": 0.42, "CT": 0.40, "OR": 0.40, "MA": 0.39, "UT": 0.39,
    "RI": 0.38, "IA": 0.38, "WA": 0.38, "NE": 0.37, "SD": 0.36, "ND": 0.35,
    "CO": 0.28, "ID": 0.27, "ME": 0.26, "MN": 0.25, "MT": 0.24, "NH": 0.22, "WY": 0.22,
    "HI": 0.21, "AK": 0.19, "VT": 0.18, "PR": 0.30
}

# Explicit label offsets for small northeastern states to avoid overlap
STATE_LABEL_CUSTOM = {
    "RI": (-70.5, 41.6),
    "DE": (-74.5, 38.8),
    "NJ": (-73.8, 40.0),
    "MD": (-75.5, 38.3),
    "DC": (-76.0, 37.6),
    "CT": (-72.0, 41.2),
    "MA": (-71.0, 42.6),
    "VT": (-72.7, 44.2),
    "NH": (-71.3, 43.6),
    "FL": (-81.6, 27.8),
    "MI": (-84.5, 43.5),
    "LA": (-92.0, 30.8),
    "CA": (-119.5, 36.8),
    "TX": (-99.0, 31.2)
}

# Color ramp: Yellow -> Orange -> Red -> Deep Crimson
COLOR_RAMP = [
    (0.00, "#ffffb2"),  # Low Risk (0.00 - 0.34)
    (0.35, "#fecc5c"),  # Moderate (0.35 - 0.54)
    (0.55, "#fd8d3c"),  # Medium-High (0.55 - 0.74)
    (0.75, "#f03b20"),  # High Risk (0.75 - 0.87)
    (0.88, "#bd0026"),  # Very High (0.88 - 0.94)
    (1.00, "#800026")   # Extreme Hotspots (0.95 - 1.00)
]
CMAP = mcolors.LinearSegmentedColormap.from_list("population_health_geo_risk", [(pos, col) for pos, col in COLOR_RAMP])


def get_state_risk_data():
    """Load or fallback state risk scores from synthetic_geo_pdi.json."""
    geo_path = os.path.join(DATA_DIR, "synthetic_geo_pdi.json")
    if os.path.exists(geo_path):
        try:
            with open(geo_path) as f:
                data = json.load(f)
            st_map = {}
            for item in data:
                st = item["state"]
                r = item["composite_environmental_risk"]
                st_map.setdefault(st, []).append(r)
            return {st: float(np.mean(vals)) for st, vals in st_map.items()}
        except Exception:
            pass
    return DEFAULT_STATE_RISKS


def render_us_risk_heatmap(output_path=None):
    """Renders a true geographic US Risk Heat Map using geographic state polygons."""
    if output_path is None:
        output_path = os.path.join(ASSETS_DIR, "us_risk_heatmap.png")

    geojson_path = os.path.join(DATA_DIR, "us-states.json")
    if not os.path.exists(geojson_path):
        raise FileNotFoundError(f"Missing required geojson file: {geojson_path}")

    with open(geojson_path) as f:
        geo_data = json.load(f)

    state_risks = get_state_risk_data()
    for st, r in DEFAULT_STATE_RISKS.items():
        if st not in state_risks:
            state_risks[st] = r

    fig, ax = plt.subplots(figsize=(15, 9), facecolor="#0b1120")
    ax.set_facecolor("#0b1120")

    state_centroids = {}

    for feature in geo_data["features"]:
        name = feature["properties"]["name"]
        code = STATE_NAME_TO_CODE.get(name, "")
        risk_val = state_risks.get(code, 0.35)
        color = CMAP(risk_val)
        is_key_hotspot = code in ["FL", "CA", "TX", "OH"]
        edge_color = "#ffffff" if is_key_hotspot else "#334155"
        line_width = 1.8 if is_key_hotspot else 0.8

        geom = feature["geometry"]
        gtype = geom["type"]
        coords = geom["coordinates"]

        if gtype == "Polygon":
            polys = [coords]
        elif gtype == "MultiPolygon":
            polys = coords
        else:
            polys = []

        all_xs = []
        all_ys = []

        for poly in polys:
            ring = poly[0]
            xs = [pt[0] for pt in ring]
            ys = [pt[1] for pt in ring]

            # Insets or transformation for Alaska and Hawaii
            if code == "AK":
                # Scale and translate Alaska to bottom-left corner
                scale = 0.35
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                xs = [(x - min_x) * scale - 120 for x in xs]
                ys = [(y - min_y) * scale + 24 for y in ys]
                ring = list(zip(xs, ys))
            elif code == "HI":
                # Scale and translate Hawaii to bottom-left corner
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                xs = [(x - min_x) - 108 for x in xs]
                ys = [(y - min_y) + 24.5 for y in ys]
                ring = list(zip(xs, ys))
            elif code == "PR":
                continue # skip PR for clean continental view

            all_xs.extend(xs)
            all_ys.extend(ys)

            patch = Polygon(
                ring,
                closed=True,
                facecolor=color,
                edgecolor=edge_color,
                linewidth=line_width,
                alpha=0.92,
                zorder=3
            )
            ax.add_patch(patch)

        if all_xs and all_ys and code:
            if code in STATE_LABEL_CUSTOM:
                state_centroids[code] = STATE_LABEL_CUSTOM[code]
            else:
                cx = float(np.mean(all_xs))
                cy = float(np.mean(all_ys))
                state_centroids[code] = (cx, cy)

    # Plot state code labels and risk values
    for code, (cx, cy) in state_centroids.items():
        if code in ["DC", "RI", "DE"]:
            continue  # Avoid cluttering tiny states on main text pass
        risk = state_risks.get(code, 0.35)
        text_color = "#ffffff" if risk > 0.45 else "#0b1120"
        font_weight = "bold" if code in ["FL", "CA", "TX", "OH", "NY", "IL", "GA", "NC"] else "normal"
        font_size = 9 if code in ["FL", "CA", "TX", "OH"] else 7.5

        ax.text(
            cx, cy + 0.15, code,
            ha="center", va="center",
            fontsize=font_size, fontweight=font_weight,
            color=text_color, zorder=5
        )
        if code in ["FL", "CA", "TX", "OH", "GA", "NC", "NY", "PA"]:
            ax.text(
                cx, cy - 0.55, f"{risk:.2f}",
                ha="center", va="center",
                fontsize=6.5, fontweight="semibold",
                color=text_color, alpha=0.9, zorder=5
            )

    # Hotspot Callouts with arrows
    # 1. Florida Coast
    if "FL" in state_centroids:
        fx, fy = state_centroids["FL"]
        ax.annotate(
            "★ Florida Coast\nRisk: 0.88 (+$6,400/mbr)",
            xy=(fx + 0.8, fy), xytext=(fx + 4.2, fy - 1.0),
            arrowprops=dict(facecolor="#f87171", shrink=0.10, width=1.5, headwidth=6, edgecolor="none"),
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor="#ef4444", linewidth=1.5),
            color="#fca5a5", fontsize=9, fontweight="bold", zorder=6
        )

    # 2. Central Valley California
    if "CA" in state_centroids:
        cx, cy = state_centroids["CA"]
        ax.annotate(
            "★ Central Valley CA\nRisk: 0.84 (AQI PM2.5: 142)",
            xy=(cx, cy), xytext=(cx - 6.5, cy + 2.5),
            arrowprops=dict(facecolor="#fb923c", shrink=0.10, width=1.5, headwidth=6, edgecolor="none"),
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor="#f97316", linewidth=1.5),
            color="#fdba74", fontsize=9, fontweight="bold", zorder=6
        )

    # 3. Gulf Industrial Corridor Texas
    if "TX" in state_centroids:
        tx, ty = state_centroids["TX"]
        ax.annotate(
            "★ Gulf Corridor (TX)\nRisk: 0.81 (Industrial PM)",
            xy=(tx + 2.5, ty - 1.5), xytext=(tx + 1.0, ty - 5.5),
            arrowprops=dict(facecolor="#f97316", shrink=0.10, width=1.5, headwidth=6, edgecolor="none"),
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor="#f97316", linewidth=1.5),
            color="#fed7aa", fontsize=8.5, fontweight="bold", zorder=6
        )

    # 4. Ohio River Valley
    if "OH" in state_centroids:
        ox, oy = state_centroids["OH"]
        ax.annotate(
            "★ Ohio River Valley (OH)\nRisk: 0.78 (Basin AQI: 108)",
            xy=(ox, oy), xytext=(ox + 3.0, oy + 3.8),
            arrowprops=dict(facecolor="#fb923c", shrink=0.10, width=1.5, headwidth=6, edgecolor="none"),
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor="#fb923c", linewidth=1.5),
            color="#fed7aa", fontsize=8.5, fontweight="bold", zorder=6
        )

    # Title & Subtitle
    ax.text(
        -125, 50.8, "Population Health — USA Environmental Risk Heat Map",
        fontsize=16, fontweight="bold", color="#f8fafc", ha="left"
    )
    ax.text(
        -125, 49.5, "Geographic Non-Clinical Exposure Index (AQI PM2.5 + Pollen + Transit Barrier + Food Desert Index)",
        fontsize=10.5, color="#94a3b8", ha="left"
    )

    # Inset labels for Alaska & Hawaii
    ax.text(-118, 23.2, "Alaska (AK)", fontsize=7.5, color="#94a3b8", ha="center")
    ax.text(-104, 23.2, "Hawaii (HI)", fontsize=7.5, color="#94a3b8", ha="center")

    # Horizontal Colorbar at the bottom
    norm = mcolors.Normalize(vmin=0.0, vmax=1.0)
    cbar_ax = fig.add_axes([0.22, 0.08, 0.56, 0.035])
    cb = matplotlib.colorbar.ColorbarBase(cbar_ax, cmap=CMAP, norm=norm, orientation='horizontal')
    cb.set_ticks([0.15, 0.45, 0.65, 0.85, 0.95])
    cb.set_ticklabels([
        "Low (0.0-0.34)\n[VT, NH, MN, CO]",
        "Moderate (0.35-0.54)\n[NY, PA, IL]",
        "Med-High (0.55-0.74)\n[GA, NC, AZ, MI]",
        "High Risk (0.75-0.90)\n[FL, CA, TX, OH]",
        "Extreme (>0.90)\n[FL Coast ZIPs]"
    ])
    cb.ax.tick_params(labelsize=8, colors="#cbd5e1", length=0)
    cb.outline.set_edgecolor("#334155")
    cb.outline.set_linewidth(1.0)

    # Map bounds
    ax.set_xlim(-127, -65)
    ax.set_ylim(22, 52)
    ax.set_aspect(1.3)
    ax.axis("off")

    plt.tight_layout()
    fig.subplots_adjust(bottom=0.16)
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f" Generated Geographic US Risk Heat Map at {output_path}")
    return output_path


def render_regional_hotspots(output_path=None):
    """Renders 4-panel regional zoom comparison chart (FL, CA, TX, OH)."""
    if output_path is None:
        output_path = os.path.join(ASSETS_DIR, "regional_hotspots.png")

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), facecolor="#0b1120")
    fig.suptitle("Population Health Regional Hot-Spot Analysis — Top 4 High-Liability Corridors", fontsize=15, fontweight="bold", color="#f8fafc", y=0.98)

    regions = [
        {
            "title": "Florida Coast Corridor (FL)",
            "subtitle": "Key ZIPs: 33010, 33142 | Risk: 0.88",
            "cost_gap": "+$4,820",
            "metrics": {"AQI PM2.5": 138, "Pollen UPI": 4.6, "Transit Barrier": 0.82, "HCC Inefficiency": 2.10},
            "color": "#bd0026",
            "ax": axes[0, 0]
        },
        {
            "title": "Central Valley Corridor (CA)",
            "subtitle": "Key ZIPs: 93201, 93706 | Risk: 0.84",
            "cost_gap": "+$3,720",
            "metrics": {"AQI PM2.5": 142, "Pollen UPI": 3.9, "Transit Barrier": 0.74, "HCC Inefficiency": 1.85},
            "color": "#e11d48",
            "ax": axes[0, 1]
        },
        {
            "title": "Gulf Industrial Corridor (TX)",
            "subtitle": "Key ZIPs: 77012, 77502 | Risk: 0.81",
            "cost_gap": "+$3,320",
            "metrics": {"AQI PM2.5": 122, "Pollen UPI": 4.2, "Transit Barrier": 0.70, "HCC Inefficiency": 1.72},
            "color": "#f97316",
            "ax": axes[1, 0]
        },
        {
            "title": "Ohio River Valley (OH)",
            "subtitle": "Key ZIPs: 45202, 43952 | Risk: 0.78",
            "cost_gap": "+$2,820",
            "metrics": {"AQI PM2.5": 108, "Pollen UPI": 3.6, "Transit Barrier": 0.65, "HCC Inefficiency": 1.60},
            "color": "#fb923c",
            "ax": axes[1, 1]
        }
    ]

    for item in regions:
        ax = item["ax"]
        ax.set_facecolor("#1e293b")
        keys = list(item["metrics"].keys())
        values = list(item["metrics"].values())
        
        max_scales = [160, 5.0, 1.0, 2.5]
        norm_vals = [v / m for v, m in zip(values, max_scales)]
        
        bars = ax.barh(keys, norm_vals, color=item["color"], alpha=0.85, edgecolor="#ffffff", linewidth=0.5, height=0.55)
        
        for bar, raw_val in zip(bars, values):
            width = bar.get_width()
            val_str = f"{raw_val:.1f}" if isinstance(raw_val, float) else f"{raw_val}"
            ax.text(width + 0.03, bar.get_y() + bar.get_height()/2, val_str,
                    va="center", ha="left", color="#f8fafc", fontsize=9, fontweight="bold")

        ax.set_xlim(0, 1.25)
        ax.set_title(item["title"], fontsize=11, fontweight="bold", color="#f8fafc", loc="left", pad=8)
        ax.text(0, 1.04, f"{item['subtitle']} | Liability Gap: {item['cost_gap']}/mbr", transform=ax.transAxes,
                fontsize=8.5, color="#94a3b8")
        ax.tick_params(colors="#cbd5e1", labelsize=8.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#334155')
        ax.spines['left'].set_color('#334155')
        ax.xaxis.set_visible(False)

    plt.tight_layout()
    fig.subplots_adjust(top=0.90, hspace=0.35)
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f" Generated Regional Hot-Spots visual at {output_path}")
    return output_path


def get_dashboard_payload():
    """Returns the A2UI Executive Dashboard JSON payload referencing generated assets."""
    from ui.templates_dashboard import get_executive_dashboard_surface
    return get_executive_dashboard_surface()


if __name__ == "__main__":
    render_us_risk_heatmap()
    render_regional_hotspots()
