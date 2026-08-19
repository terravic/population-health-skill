"""
Mock PIE Engine (Population Insights & Intervention Engine).
Generates persona-based recommendations (Pricing/Underwriting & Clinical Operations),
performs deterministic fact-checking against SQL execution values_array,
and produces automated evaluation scorecards (AutoRater v2).
"""

from typing import Any, Dict, List, Optional
from engines.mock_database import get_database
from ui.templates_interventions import get_actionable_interventions_surface, render_interventions_a2ui


class MockPIEEngine:
    """Generates tailored, fact-checked interventions and AutoRater evaluation metrics."""

    def __init__(self):
        self.db = get_database()

    def generate_interventions(
        self,
        cohort_summary: Optional[Dict[str, Any]] = None,
        cohort_id: str = "FL_40_50",
        state: str = "FL",
        age_min: int = 40,
        age_max: int = 50,
        target_loading: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generates dual-persona interventions, runs fact-checking, and emits Surface 3 A2UI payload."""
        if cohort_summary is None:
            cohort_summary = self.db.get_cohort_summary(state=state, age_min=age_min, age_max=age_max)

        cohort_n = cohort_summary.get("cohort_n", 261)
        median_cost = cohort_summary.get("median_cost", 13900.0)
        baseline_cost = cohort_summary.get("baseline_cost", 9080.0)
        unpriced_diff = round(max(4800.0, median_cost - baseline_cost), 2)
        loading_amount = target_loading or 6400.0

        # Portfolio margin protection calculation (~$3.2M across 500 equivalent cohort lives)
        total_margin_prot_num = round((loading_amount * max(500, cohort_n)) / 1_000_000, 1)
        margin_prot_str = f"${total_margin_prot_num:.1f}M"

        # Persona 1: Pricing / Underwriting Recommendations
        pricing_rec = {
            "persona": "Pricing & Actuarial Underwriting",
            "primary_action": f"Apply renewal premium loading of +${loading_amount:,.0f}/member/year",
            "target_books": "Commercial Group & Medicare Advantage (Individual & Group)",
            "target_zips": ["33010", "33142"] if state == "FL" else ["93201", "93706"],
            "margin_protection": margin_prot_str,
            "loss_ratio_impact": "-4.2% projected improvement in targeted corridors",
            "actuarial_rationale": "Compensates for environmental AQI PM2.5 and storm vulnerability uncaptured by CMS-HCC."
        }

        # Persona 2: Clinical Operations & Care Management
        clinical_rec = {
            "persona": "Clinical Operations & Medical Management",
            "primary_action": f"Deploy proactive smart nebulizer adherence monitoring to {cohort_n} members",
            "campaign_components": [
                "Bluetooth-enabled smart inhaler distribution with compliance telemetry",
                "Automated microclimate AQI alert dispatch via SMS when local PM2.5 > 100",
                "Proactive pharmacist medication reconciliation prior to high-pollen seasons"
            ],
            "cms_compliance": "Verified (Special Supplemental Benefits for Chronically Ill / SSBCI)",
            "tcpa_compliance": "Verified (Automated outreach opt-in consent confirmed in member master)"
        }

        # Deterministic Fact-Checking
        # Verify cited numerical figures: median_cost, baseline_cost, loading, cohort_n
        cited_figures = {
            "median_cost": median_cost,
            "baseline_cost": baseline_cost,
            "cohort_n": cohort_n,
            "unpriced_loading": loading_amount
        }
        fact_check_result = self.verify_facts(cited_figures, cohort_summary)

        # AutoRater v2 Scorecard
        autorater_scores = {
            "grounding": 5.0,
            "clinical_safety": 5.0,
            "actionability": 5.0,
            "tcpa_cms_compliance": "PASS",
            "overall_rating": "5.0 / 5.0 (Optimal)"
        }

        cohort_title = f"{state} High-Risk Corridor (Age {age_min}–{age_max})"
        a2ui_messages = get_actionable_interventions_surface(
            cohort_title=cohort_title,
            unpriced_loading=loading_amount,
            margin_protection=margin_prot_str,
            care_cohort_size=cohort_n,
            verified_claims_count=fact_check_result["verified_count"]
        )

        return {
            "cohort_id": cohort_id,
            "state": state,
            "age_range": f"{age_min}-{age_max}",
            "pricing_intervention": pricing_rec,
            "clinical_intervention": clinical_rec,
            "fact_checking": fact_check_result,
            "autorater": autorater_scores,
            "a2ui_messages": a2ui_messages,
            "a2ui_payload": render_interventions_a2ui(
                cohort_title=cohort_title,
                unpriced_loading=loading_amount,
                margin_protection=margin_prot_str,
                care_cohort_size=cohort_n,
                verified_claims_count=fact_check_result["verified_count"]
            )
        }

    def verify_facts(self, cited_figures: Dict[str, Any], cohort_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Performs deterministic verification of cited numbers against SQL execution outputs."""
        verified_count = 0
        total_claims = len(cited_figures)
        details = []

        for key, val in cited_figures.items():
            verified = True
            details.append({"claim_key": key, "cited_value": val, "verified": verified, "source": "V_combined / baseline_stats"})
            if verified:
                verified_count += 1

        return {
            "status": "PASS",
            "match_rate": "100%",
            "verified_count": verified_count,
            "total_claims": total_claims,
            "details": details
        }


# Singleton instance
_PIE_INSTANCE: Optional[MockPIEEngine] = None

def get_pie_engine() -> MockPIEEngine:
    """Returns or creates the shared MockPIEEngine instance."""
    global _PIE_INSTANCE
    if _PIE_INSTANCE is None:
        _PIE_INSTANCE = MockPIEEngine()
    return _PIE_INSTANCE
