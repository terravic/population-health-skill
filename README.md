# Population Health Skill

> Interactive Population Health Intelligence with USA Geographic Environmental Risk Heat Map.
> Designed for Gemini Enterprise, Antigravity, and Agent-to-User Interface (A2UI v0.8) Harnesses.

---

## Architecture & System Workflow

![Population Health Skill Architecture & System Workflow](assets/skill_workflow_overview.png)

---

## Core Capabilities

- **Geographic Environmental Risk Mapping**: High-resolution continuous risk gradient visualization across state and ZIP boundaries incorporating EPA PM2.5 AQI, pollen index, and climate vulnerability.
- **Zero Cloud Footprint**: Fully self-contained execution via an in-memory SQLite database view (`V_combined`), synthetic patient datasets (5,000 records), and local rendering assets without external cloud or API dependencies.
- **Actuarial Paradox Detection**: Identification of cohorts exhibiting significant claims cost spikes despite low baseline CMS-HCC clinical risk scores.
- **Multi-Persona Actionable Interventions**: Automated generation of underwriting renewal loading recommendations and proactive care management outreach protocols.
- **Deterministic Fact-Checking & Safety Verification**: 100% numerical claim verification against underlying SQLite runtime data alongside AutoRater safety scoring (5.0 / 5.0).
- **Actuarial Feature Staging (HITL)**: Formal S1-S3 statistical gate validation ($r=0.33, r=0.31, p<0.001$) with Human-in-the-Loop approval workflows.

---

## Executive Surfaces

1. **Surface 1: Executive Overview**: National KPI summary tiles, geographic environmental risk heat map, and top regional liability corridors.
2. **Surface 2: Cohort Analytics & Graphs**: Interactive filter selectors (State, Age Bracket, Disease Focus, Exposure Tier) with 12-month seasonal claims line graphs and multi-metric comparison bar charts.
3. **Surface 3: Actionable Interventions**: Dual-persona intervention cards (Actuarial Pricing Loading Memo and Clinical Telehealth Outreach) with real-time fact-checking verification badges.
4. **Surface 4: Actuarial Staging & Approval**: Data science evaluation scorecard for candidate non-clinical proxies with one-click commit actions.

---

## Project Structure

```
population-health-skill/
├── SKILL.md                          # Main Skill instructions, system prompts & routing
├── plugin.json                       # Plugin descriptor bundle for Gemini Enterprise / Jetski
├── LICENSE                           # Apache License, Version 2.0
├── README.md                         # Project documentation
├── requirements.txt                  # Python dependencies
├── generate_synthetic_data.py        # Calibrated synthetic health & geospatial data generator
├── run_demo.py                       # Interactive CLI demonstration of both CUJs
├── serve_web_preview.py              # Lightweight local HTTP server for executive UI
├── test_scenarios.py                 # Automated verification test suite
├── assets/
│   ├── skill_workflow_overview.png   # End-to-end architecture & workflow diagram
│   ├── us_risk_heatmap.png           # Geographic US Risk Heat Map
│   └── regional_hotspots.png         # 4-panel regional hot-spot analysis chart
├── data/
│   ├── us-states.json                # Local US state boundary GeoJSON polygons
│   ├── synthetic_members.json        # 5,000 synthetic patient member records
│   ├── synthetic_geo_pdi.json        # Geospatial context, 16-dim PDI vectors & AQI PM2.5
│   ├── synthetic_baseline_stats.json # Long-format EAV population baseline stats
│   └── synthetic_proxies.json        # Enriched ZIP proxies (HCC inefficiency, transit barriers)
├── engines/
│   ├── __init__.py
│   ├── mock_database.py              # In-memory SQLite engine serving runtime view V_combined
│   ├── mock_pqa.py                   # Problem Quality Assessment & candidate proxy intake
│   ├── mock_pea.py                   # Proxy Enrichment Engine (S1-S3 correlation & staging)
│   ├── mock_nl2sql.py                # Safe NL2SQL cohort resolution & delta computation
│   ├── mock_pie.py                   # Population Insights Engine & deterministic fact-checker
│   └── map_generator.py              # Geographic US Map & regional visual renderer
├── skills/
│   └── population-health-skill/
│       ├── SKILL.md                  # Skill instructions & metadata
│       └── README.md                 # Skill documentation
└── ui/
    ├── __init__.py
    ├── a2ui_catalog.py               # A2UI v0.8 BasicCatalog component definitions & builders
    ├── templates_dashboard.py        # Executive Overview Dashboard (Surface 1)
    ├── templates_cohort.py           # Cohort Comparison Card (Surface 2)
    ├── templates_interventions.py    # Interventions Card & Fact-Checking (Surface 3)
    ├── templates_hitl_approval.py    # Data Scientist Staging & Approval Card (Surface 4)
    └── vega_specs.py                 # Vega-Lite TopoJSON & comparative chart specifications
```

---

## Quickstart & Verification

### 1. Run Automated Test Suite
```bash
python3 test_scenarios.py
```

### 2. Run Interactive CLI Demonstration
```bash
python3 run_demo.py --cuj all
```

### 3. Launch Local Executive UI Server
```bash
python3 serve_web_preview.py
```
Open [http://localhost:8088](http://localhost:8088) in any browser.

---

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for the full license text.
