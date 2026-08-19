#!/usr/bin/env python3
"""
Interactive CLI Runner for Population Health Skill.
Simulates end-to-end user journeys for Antigravity, Gemini Enterprise App, and ADK harness testing.
"""

import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engines.mock_database import get_database
from engines.mock_nl2sql import get_nl2sql_engine
from engines.mock_pie import get_pie_engine
from engines.mock_pea import get_pea_engine
from ui.templates_dashboard import render_dashboard_a2ui
from ui.templates_cohort import render_cohort_a2ui
from ui.templates_interventions import render_interventions_a2ui
from ui.templates_hitl_approval import render_hitl_approval_a2ui


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_cuj_1():
    """Executes CUJ 1: Executive Dashboard & Geospatial Exploration."""
    print_banner("CUJ 1: Executive Dashboard & Geospatial Exploration")
    
    print(">>> [User Intent]: 'Open the executive population health overview.'")
    print(">>> [Skill Action]: Emitting Surface 1 (A2UI Executive Dashboard)...")
    dash_payload = render_dashboard_a2ui()
    print(dash_payload[:800] + "\n... [truncated A2UI payload] ...\n</a2ui-json>\n")

    print("-" * 80)
    print(">>> [User Action]: Clicks '[Drilldown: Florida Hot Spot (Age 40-50)]'")
    print(">>> [Skill Action]: NL2SQL engine executing safe SQL against V_combined...")
    
    nl2sql = get_nl2sql_engine()
    cohort_res = nl2sql.resolve_cohort("Florida members age 40 to 50", state="FL", age_min=40, age_max=50)
    summary = cohort_res["summary"]
    
    print(f"\n[SQL Generated]:\n{cohort_res['generated_sql']}\n")
    print(f"[Cohort Metrics (N={summary['cohort_n']})]:")
    print(f"  • Median Claims Cost: ${summary['median_cost']:,.2f} (Baseline: ${summary['baseline_cost']:,.2f} | Δ +{summary['cost_delta_pct']}%)")
    print(f"  • Clinical HCC Risk:  {summary['mean_hcc']:.2f} (Baseline: {summary['baseline_hcc']:.2f} | Δ {summary['hcc_delta_pct']}%)")
    print(f"  • COPD Prevalence:   {summary['copd_prevalence']*100:.1f}% (Baseline: {summary['baseline_copd']*100:.1f}% | Δ +{summary['copd_delta_pct']}%)")
    print(f"  • Environmental Risk: {summary['composite_risk']:.2f} (Baseline: {summary['baseline_risk']:.2f} | Δ +{summary['risk_delta_pct']}%)")
    print(f"  • Unpriced Liability Gap: +${summary['unpriced_liability']:,.2f} / member\n")
    
    print(">>> [Skill Action]: Emitting Surface 2 (Cohort Comparison Card)...")
    print(cohort_res["a2ui_payload"][:800] + "\n... [truncated A2UI payload] ...\n</a2ui-json>\n")

    print("-" * 80)
    print(">>> [User Action]: Clicks '[Generate Tailored Interventions]'")
    print(">>> [Skill Action]: PIE Engine generating dual-persona recommendations with deterministic fact-checking...")
    
    pie = get_pie_engine()
    intv_res = pie.generate_interventions(cohort_summary=summary, state="FL", age_min=40, age_max=50)
    
    print("\n[Pricing / Underwriting Recommendation]:")
    print(f"  • Action: {intv_res['pricing_intervention']['primary_action']}")
    print(f"  • Target ZIPs: {intv_res['pricing_intervention']['target_zips']}")
    print(f"  • Margin Protection: {intv_res['pricing_intervention']['margin_protection']}")

    print("\n[Clinical Operations Recommendation]:")
    print(f"  • Action: {intv_res['clinical_intervention']['primary_action']}")
    print(f"  • Compliance: {intv_res['clinical_intervention']['tcpa_compliance']}")

    print("\n[Deterministic Fact-Check Verification]:")
    print(f"  • Status: {intv_res['fact_checking']['status']} ({intv_res['fact_checking']['match_rate']})")
    print(f"  • Verified {intv_res['fact_checking']['verified_count']}/{intv_res['fact_checking']['total_claims']} numerical claims against SQLite view V_combined.")

    print("\n[AutoRater Scorecard]:")
    print(f"  • Grounding: {intv_res['autorater']['grounding']}/5.0 | Safety: {intv_res['autorater']['clinical_safety']}/5.0 | Rating: {intv_res['autorater']['overall_rating']}")

    print("\n>>> [Skill Action]: Emitting Surface 3 (Actionable Interventions Card)...")
    print(intv_res["a2ui_payload"][:800] + "\n... [truncated A2UI payload] ...\n</a2ui-json>\n")


def run_cuj_2():
    """Executes CUJ 2: Actuarial Data Enrichment & HITL Staging Journey."""
    print_banner("CUJ 2: Actuarial Data Enrichment (Setup Phase)")

    query = "Help me find non-clinical ZIP-level drivers of cost not captured by HCC"
    print(f">>> [User Intent]: '{query}'")
    print(">>> [Skill Action]: PQA and PEA engines executing S1-S3 enrichment pipeline...")

    pea = get_pea_engine()
    enrich_res = pea.run_enrichment_pipeline(query)

    print("\n[Proxy Quality Assessment (PQA) Results]:")
    for c in enrich_res["intake"]["candidates"]:
        print(f"  • Candidate: {c['name']} (Target: {c['target_domain']} | Signal Score: {c['initial_relevance_score']})")

    print("\n[Actuarial Statistical Validation (PEA S1–S3 Gates)]:")
    print(f"  • S1 Semantic Clustering: {enrich_res['s1']['status']} (Silhouette Score: {enrich_res['s1']['silhouette_score']})")
    print(f"  • S2 Cost Correlation (PDI AQI): r = {enrich_res['s2']['proxies'][0]['correlation_r']:.2f} (p < 0.001)")
    print(f"  • S2 Cost Correlation (Transit): r = {enrich_res['s2']['proxies'][1]['correlation_r']:.2f} (p < 0.001)")
    print(f"  • S2 Combined R² Gain: +{enrich_res['s2']['combined_r2_gain_pct']:.1f}%")
    print(f"  • S3 Staging Status: {enrich_res['s3']['status']}")

    print("\n>>> [Skill Action]: Emitting Surface 4 (Actuarial HITL Approval Card)...")
    print(enrich_res["a2ui_payload"][:800] + "\n... [truncated A2UI payload] ...\n</a2ui-json>\n")

    print("-" * 80)
    print(">>> [User Action]: Clicks '[Approve & Commit Proxies to V_combined]'")
    print(">>> [Skill Action]: Committing proxies to database view and refreshing schema...")
    
    commit_res = pea.commit_approval(["PDI_AQI_PM25_Proxy", "Structural_Transit_Barrier_Proxy"])
    print(f"\n[Commit Result]: {commit_res['message']}")
    print(f"Status: {commit_res['status']} | Enriched View: {commit_res['view']}\n")


def main():
    parser = argparse.ArgumentParser(description="Population Health Skill Interactive Runner")
    parser.add_argument("--cuj", choices=["1", "2", "all"], default="all", help="Which CUJ to execute")
    args = parser.parse_args()

    if args.cuj in ["1", "all"]:
        run_cuj_1()
    if args.cuj in ["2", "all"]:
        run_cuj_2()


if __name__ == "__main__":
    main()
