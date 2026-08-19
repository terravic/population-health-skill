#!/usr/bin/env python3
"""
Automated Verification Test Suite for Population Health Skill.
Verifies:
1. Data integrity & schema validation across all synthetic JSON files.
2. In-memory SQLite runtime view V_combined queries.
3. CUJ 1: Executive Dashboard & Geospatial Exploration (Surface 1 -> Surface 2 -> Surface 3).
4. CUJ 2: Actuarial Data Enrichment & HITL Staging (PQA -> PEA -> Surface 4 -> Commit).
5. A2UI v0.8 JSON schema compliance, pure ASCII output, and valid BasicCatalog components.
"""

import json
import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engines.mock_database import get_database
from engines.mock_pqa import get_pqa_engine
from engines.mock_pea import get_pea_engine
from engines.mock_nl2sql import get_nl2sql_engine
from engines.mock_pie import get_pie_engine
from ui.templates_dashboard import get_executive_dashboard_surface, render_dashboard_a2ui
from ui.templates_cohort import get_cohort_comparison_surface, render_cohort_a2ui
from ui.templates_interventions import get_actionable_interventions_surface, render_interventions_a2ui
from ui.templates_hitl_approval import get_hitl_approval_surface, render_hitl_approval_a2ui
from ui.vega_specs import get_us_choropleth_vega_spec, get_cohort_comparison_vega_spec


class TestPopulationHealthSkill(unittest.TestCase):
    """Full test suite covering database, engines, UI surfaces, and end-to-end CUJs."""

    @classmethod
    def setUpClass(cls):
        cls.db = get_database()
        cls.pqa = get_pqa_engine()
        cls.pea = get_pea_engine()
        cls.nl2sql = get_nl2sql_engine()
        cls.pie = get_pie_engine()

    def test_01_synthetic_data_files_exist_and_valid(self):
        """Verify synthetic datasets exist and have expected record counts."""
        data_dir = os.path.join(BASE_DIR, "data")
        self.assertTrue(os.path.exists(os.path.join(data_dir, "synthetic_members.json")))
        self.assertTrue(os.path.exists(os.path.join(data_dir, "synthetic_geo_pdi.json")))
        self.assertTrue(os.path.exists(os.path.join(data_dir, "synthetic_baseline_stats.json")))
        self.assertTrue(os.path.exists(os.path.join(data_dir, "synthetic_proxies.json")))

        with open(os.path.join(data_dir, "synthetic_members.json")) as f:
            members = json.load(f)
        self.assertEqual(len(members), 5000)

        with open(os.path.join(data_dir, "synthetic_baseline_stats.json")) as f:
            baseline = json.load(f)
        self.assertGreaterEqual(len(baseline), 4)

    def test_02_database_view_and_baseline_stats(self):
        """Verify SQLite view V_combined serves correct records and baseline stats."""
        records, _, _ = self.db.execute_query("SELECT COUNT(*) AS total FROM V_combined;")
        self.assertEqual(records[0]["total"], 5000)

        sample, cols, _ = self.db.execute_query("SELECT * FROM V_combined LIMIT 1;")
        self.assertEqual(len(sample), 1)
        self.assertIn("member_id", cols)
        self.assertIn("composite_environmental_risk", cols)
        self.assertIn("hcc_inefficiency_score", cols)
        self.assertIn("air_quality_proxy", cols)

        baseline = self.db.get_baseline_stats_dict()
        self.assertEqual(baseline.get("total_cost"), 9080.0)
        self.assertEqual(baseline.get("hcc_score"), 1.10)
        self.assertEqual(baseline.get("copd_prevalence"), 0.082)
        self.assertEqual(baseline.get("composite_risk"), 0.42)

    def test_03_assets_generation(self):
        """Verify pre-rendered map and hotspot assets exist."""
        assets_dir = os.path.join(BASE_DIR, "assets")
        self.assertTrue(os.path.exists(os.path.join(assets_dir, "us_risk_heatmap.png")))
        self.assertTrue(os.path.exists(os.path.join(assets_dir, "regional_hotspots.png")))
        self.assertGreater(os.path.getsize(os.path.join(assets_dir, "us_risk_heatmap.png")), 10000)
        self.assertGreater(os.path.getsize(os.path.join(assets_dir, "regional_hotspots.png")), 10000)

    def test_04_cuj1_step1_executive_dashboard(self):
        """CUJ 1 Step 1: Render Executive Dashboard Surface."""
        messages = get_executive_dashboard_surface()
        self.assertEqual(len(messages), 3)
        self.assertIn("beginRendering", messages[0])
        self.assertEqual(messages[0]["beginRendering"]["surfaceId"], "executive-dashboard")
        self.assertIn("surfaceUpdate", messages[1])
        
        components = messages[1]["surfaceUpdate"]["components"]
        comp_ids = [c["id"] for c in components]
        self.assertIn("dash_root", comp_ids)
        self.assertIn("kpi_card", comp_ids)
        self.assertIn("map_image", comp_ids)
        self.assertIn("btn_fl", comp_ids)

        payload_str = render_dashboard_a2ui()
        self.assertTrue(payload_str.startswith("<a2ui-json>"))
        self.assertTrue(payload_str.endswith("</a2ui-json>"))
        # Verify pure ASCII
        payload_str.encode('ascii')

    def test_05_cuj1_step2_florida_cohort_drilldown(self):
        """CUJ 1 Step 2: Resolve Florida Age 40-50 Cohort and Render Cohort Comparison Card."""
        cohort_res = self.nl2sql.resolve_cohort("Drilldown: Florida Hot Spot", state="FL", age_min=40, age_max=50)
        summary = cohort_res["summary"]
        
        self.assertGreater(summary["cohort_n"], 50)
        self.assertGreater(summary["median_cost"], summary["baseline_cost"])
        self.assertLess(summary["mean_hcc"], summary["baseline_hcc"])  # Paradox
        self.assertGreater(summary["composite_risk"], summary["baseline_risk"])

        messages = cohort_res["a2ui_messages"]
        self.assertEqual(messages[0]["beginRendering"]["surfaceId"], "cohort-comparison")
        
        comp_ids = [c["id"] for c in messages[1]["surfaceUpdate"]["components"]]
        self.assertIn("cohort_root", comp_ids)
        self.assertIn("tile_cost", comp_ids)
        self.assertIn("tile_hcc", comp_ids)
        self.assertIn("btn_gen_intervention", comp_ids)

    def test_06_cuj1_step3_actionable_interventions_and_factcheck(self):
        """CUJ 1 Step 3: Generate PIE Interventions, Run Fact Check & AutoRater."""
        summary = self.db.get_cohort_summary(state="FL", age_min=40, age_max=50)
        intv_res = self.pie.generate_interventions(cohort_summary=summary, state="FL", age_min=40, age_max=50)

        # Persona verifications
        self.assertIn("Pricing", intv_res["pricing_intervention"]["persona"])
        self.assertIn("Clinical Operations", intv_res["clinical_intervention"]["persona"])
        
        # Fact-checking verification
        self.assertEqual(intv_res["fact_checking"]["status"], "PASS")
        self.assertEqual(intv_res["fact_checking"]["match_rate"], "100%")

        # AutoRater verification
        self.assertEqual(intv_res["autorater"]["grounding"], 5.0)
        self.assertEqual(intv_res["autorater"]["clinical_safety"], 5.0)
        self.assertEqual(intv_res["autorater"]["tcpa_cms_compliance"], "PASS")

        # Surface 3 payload verification
        messages = intv_res["a2ui_messages"]
        self.assertEqual(messages[0]["beginRendering"]["surfaceId"], "actionable-interventions")
        comp_ids = [c["id"] for c in messages[1]["surfaceUpdate"]["components"]]
        self.assertIn("pricing_intv_card", comp_ids)
        self.assertIn("clinical_intv_card", comp_ids)
        self.assertIn("factcheck_badge_card", comp_ids)
        self.assertIn("btn_dispatch", comp_ids)

    def test_07_cuj2_actuarial_enrichment_journey(self):
        """CUJ 2: Actuarial Proxy Quality Assessment & HITL Staging Approval."""
        enrich_res = self.pea.run_enrichment_pipeline("Help me find non-clinical ZIP-level drivers of cost not captured by HCC")
        
        self.assertEqual(enrich_res["s1"]["status"], "PASS")
        self.assertEqual(enrich_res["s2"]["status"], "PASS")
        self.assertAlmostEqual(enrich_res["s2"]["proxies"][0]["correlation_r"], 0.33, places=2)
        self.assertAlmostEqual(enrich_res["s2"]["proxies"][1]["correlation_r"], 0.31, places=2)
        self.assertEqual(enrich_res["s3"]["status"], "READY_FOR_COMMIT")

        # Surface 4 payload check
        messages = enrich_res["a2ui_messages"]
        self.assertEqual(messages[0]["beginRendering"]["surfaceId"], "actuarial-hitl-approval")
        comp_ids = [c["id"] for c in messages[1]["surfaceUpdate"]["components"]]
        self.assertIn("proxy_eval_card", comp_ids)
        self.assertIn("quality_gates_card", comp_ids)
        self.assertIn("btn_approve", comp_ids)

        # Commit approval
        commit_res = self.pea.commit_approval(["PDI_AQI_PM25_Proxy", "Structural_Transit_Barrier_Proxy"])
        self.assertEqual(commit_res["status"], "COMMITTED")
        self.assertGreater(commit_res["committed_count"], 0)

    def test_08_vega_specs_validity(self):
        """Verify Vega-Lite specs structure and required fields."""
        us_spec = get_us_choropleth_vega_spec()
        self.assertIn("$schema", us_spec)
        self.assertEqual(us_spec["mark"]["type"], "geoshape")

        cohort_spec = get_cohort_comparison_vega_spec()
        self.assertIn("$schema", cohort_spec)
        self.assertEqual(cohort_spec["mark"]["type"], "bar")

    def test_09_canvas_html_generation(self):
        """Verify native Canvas HTML/CSS/JS generator produces valid self-contained output."""
        from ui.canvas_app import generate_canvas_html
        html = generate_canvas_html()
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Population Health Intelligence", html)
        self.assertIn("cdn.jsdelivr.net/npm/chart.js", html)
        self.assertIn("cdn.tailwindcss.com", html)
        self.assertIn("data:image/png;base64,", html)
        self.assertIn("DATA_STORE", html)
        self.assertIn("Florida Coast (FL)", html)
        self.assertIn("Unpriced Risk Gap", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
