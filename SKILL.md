---
name: population-health-skill
description: >-
  Interactive conversational Population Health Skill using A2UI v0.8.
  Features a continuous US Risk Heat Map, cohort drill-down comparisons, deterministic fact-checking,
  and actionable pricing and clinical intervention generation for Gemini Enterprise App, Spark, and Antigravity.
tags:
  - population-health
  - healthcare
  - a2ui
  - conversational-bi
  - actuarial-science
  - environmental-risk
  - sdoh
  - nl2sql
  - fact-checking
  - care-management
---

# Population Health Skill

This skill implements an **interactive, conversational "Looker-style" executive dashboard** based on the Google Health Population Health framework. It uses **A2UI v0.8 (Agent-to-User Interface)** to render interactive UI cards, a USA Risk Heat Map, dynamic cohort comparisons, and automated clinical/pricing intervention generators.

All data is **100% self-contained and local** (in-memory SQLite + synthetic JSON). No cloud dependencies, GCP credentials, BigQuery datasets, or external APIs are required.

--------------------------------------------------------------------------------

## 1. Overview & Capabilities

- **Surface 1: Executive Overview & US Risk Heat Map** (`executive-dashboard`): Looker-style multi-tile dashboard displaying population baseline KPIs, high-resolution US environmental risk map, and top regional hot spots.
- **Surface 2: Cohort Comparison Card** (`cohort-comparison`): Side-by-side metric comparison tiles highlighting the actuarial paradox (e.g., Florida age 40–50 cohort having 53% higher claims costs despite 15% lower clinical HCC risk scores).
- **Surface 3: Actionable Interventions Card** (`actionable-interventions`): Dual-persona intervention recommendations (Actuarial Pricing renewal loadings and Clinical Operations proactive respiratory care) with 100% deterministic fact-checking and AutoRater scorecards.
- **Surface 4: Actuarial Data Scientist Staging & Approval Card** (`actuarial-hitl-approval`): PQA/PEA candidate proxy validation (r=0.33, r=0.31) with interactive Human-in-the-Loop (HITL) approval buttons.

--------------------------------------------------------------------------------

## 2. When to Use This Skill

Activate this skill when the user:
1. Asks for a **population health executive overview**, Looker dashboard, or national health risk map.
2. Requests an **actuarial cohort drill-down** (e.g., "Show me Florida hot spots", "Analyze respiratory patients in high pollution ZIPs", "Compare California cohort to baseline").
3. Asks to **generate actionable interventions** for pricing/underwriting or clinical operations.
4. Inquires about **non-clinical drivers of healthcare cost** not captured by CMS-HCC (environmental AQI, pollen, transit barriers, food deserts).
5. Requests **proxy enrichment, PQA intake, or actuarial validation** for new non-clinical features.

--------------------------------------------------------------------------------

## 3. Core Engine Architecture

```
engines/
├── mock_database.py     # In-memory SQLite runtime view V_combined (5,000 members)
├── mock_pqa.py          # Problem-to-Proxy Quality Assessment & Intake logic
├── mock_pea.py          # Proxy Enrichment Engine (S1-S3 correlation & staging)
├── mock_nl2sql.py       # Safe NL2SQL resolver & delta calculator
├── mock_pie.py          # Population Insights Engine & deterministic fact-checker
└── map_generator.py     # High-res US Choropleth & regional hot-spot visual renderer
```

### Python Programmatic Usage

```python
from engines.mock_database import get_database
from engines.mock_nl2sql import get_nl2sql_engine
from engines.mock_pie import get_pie_engine
from engines.mock_pea import get_pea_engine
from ui.templates_dashboard import render_dashboard_a2ui
from ui.templates_cohort import render_cohort_a2ui
from ui.templates_interventions import render_interventions_a2ui
from ui.templates_hitl_approval import render_hitl_approval_a2ui

# 1. Generate Executive Overview
dash_a2ui_json = render_dashboard_a2ui()

# 2. Resolve Florida Cohort Drilldown
nl2sql = get_nl2sql_engine()
cohort_res = nl2sql.resolve_cohort("Florida members age 40 to 50", state="FL", age_min=40, age_max=50)
cohort_a2ui_json = cohort_res["a2ui_payload"]

# 3. Generate Fact-Checked Interventions
pie = get_pie_engine()
intv_res = pie.generate_interventions(cohort_summary=cohort_res["summary"], state="FL", age_min=40, age_max=50)
intv_a2ui_json = intv_res["a2ui_payload"]

# 4. Run Actuarial Staging & HITL Approval
pea = get_pea_engine()
enrich_res = pea.run_enrichment_pipeline("Identify non-clinical drivers of cost")
hitl_a2ui_json = enrich_res["a2ui_payload"]
```

--------------------------------------------------------------------------------

## 4. A2UI v0.8 Output Directives

When interacting with a user in an A2UI-capable harness (Gemini Enterprise App, Spark, ADK Web), emit structured `<a2ui-json>` message envelopes:

```json
<a2ui-json>
[
  { "beginRendering": { "surfaceId": "executive-dashboard", "root": "dash_root" } },
  { "surfaceUpdate": { "surfaceId": "executive-dashboard", "components": [ ... ] } },
  { "dataModelUpdate": { "surfaceId": "executive-dashboard", "path": "/", "contents": [] } }
]
</a2ui-json>
```

### BasicCatalog v0.8 Permitted Components & Icons
- Layout: `Column`, `Row`, `Card`, `Divider`
- Content: `Text` (usageHint: `h1`, `h2`, `h3`, `body`, `caption`, `callout`), `Image`, `Icon`
- Interactive: `Button` (action name + context parameters)
- Standard Icons: `"payment"`, `"favorite"`, `"check"`, `"warning"`, `"analytics"`

--------------------------------------------------------------------------------

## 5. End-to-End User Journeys (CUJs)

### CUJ 1: Executive Dashboard & Geospatial Exploration
1. **User**: "Open the executive population health overview."
   - **Agent**: Emits Surface 1 (Executive Dashboard with KPI summary, US Heat Map, and hot-spot buttons).
2. **User**: Clicks `[Drilldown: Florida Hot Spot (Age 40-50)]` (or asks "Analyze Florida cohort").
   - **Agent**: Runs NL2SQL against `V_combined`, computes baseline deltas, and emits Surface 2 (Cohort Comparison Card).
3. **User**: Clicks `[Generate Tailored Interventions]`.
   - **Agent**: Runs PIE engine, performs deterministic fact-checking against `values_array`, validates AutoRater scorecard, and emits Surface 3 (Actionable Interventions Card).

### CUJ 2: Actuarial Data Enrichment (Setup Phase)
1. **User**: "Help me find non-clinical ZIP-level drivers of cost not captured by HCC."
   - **Agent**: Runs PQA intake and PEA S1–S3 correlation checks ($r = 0.33, 0.31$, $R^2$ gain $+11.4\%$), emitting Surface 4 (Actuarial HITL Approval Card).
2. **User**: Clicks `[Approve & Commit Proxies to V_combined]`.
   - **Agent**: Commits proxy features to in-memory `V_combined` runtime view and updates baseline stats.

--------------------------------------------------------------------------------

## 6. Verification & Automated Testing

Execute the automated test suite:
```bash
python3 test_scenarios.py
```

Run the interactive CLI demonstration:
```bash
python3 run_demo.py --cuj all
```

Launch the local web preview server (port 8088):
```bash
python3 serve_web_preview.py
```
