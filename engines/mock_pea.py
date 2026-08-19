"""
Mock PEA Engine (Proxy Enrichment & Actuarial Staging).
Executes S1-S3 multi-stage validation:
- S1: Semantic similarity & clustering
- S2: Actuarial correlation & residual cost variance reduction (r=0.33, r=0.31)
- S3: Staging for HITL approval
- Emits Surface 4 A2UI payload and handles proxy commit.
"""

from typing import Any, Dict, List, Optional
from engines.mock_pqa import get_pqa_engine
from engines.mock_database import get_database
from ui.templates_hitl_approval import get_hitl_approval_surface, render_hitl_approval_a2ui


class MockPEAEngine:
    """Actuarial proxy enrichment, statistical validation, and staging pipeline."""

    def __init__(self):
        self.pqa = get_pqa_engine()
        self.db = get_database()

    def run_enrichment_pipeline(self, problem_statement: str = "Identify non-clinical ZIP-level drivers of cost not captured by HCC") -> Dict[str, Any]:
        """Runs S1-S3 enrichment pipeline and returns structured validation metrics."""
        intake_res = self.pqa.process_intake(problem_statement)

        # S1 Validation: Semantic Similarity & Cluster Stability
        s1_results = {
            "gate": "S1",
            "status": "PASS",
            "silhouette_score": 0.72,
            "cluster_coherence": 0.88,
            "semantic_distance": 0.14
        }

        # S2 Validation: Actuarial Correlation with Unexplained Residual Cost
        s2_results = {
            "gate": "S2",
            "status": "PASS",
            "proxies": [
                {
                    "name": "PDI_AQI_PM25_Proxy",
                    "correlation_r": 0.33,
                    "p_value": 0.0001,
                    "time_stability": 0.89,
                    "vif": 1.18  # Low collinearity
                },
                {
                    "name": "Structural_Transit_Barrier_Proxy",
                    "correlation_r": 0.31,
                    "p_value": 0.0002,
                    "time_stability": 0.86,
                    "vif": 1.22  # Low collinearity
                }
            ],
            "combined_r2_gain_pct": 11.4,
            "unexplained_variance_reduction_pct": 18.2
        }

        # S3 Validation: Staging Readiness
        s3_results = {
            "gate": "S3",
            "status": "READY_FOR_COMMIT",
            "hitl_required": True,
            "recommended_action": "APPROVE"
        }

        a2ui_messages = get_hitl_approval_surface(
            problem_statement=problem_statement,
            proxy_1_name="PDI_AQI_PM25_Proxy",
            proxy_1_corr=0.33,
            proxy_1_stability=0.89,
            proxy_2_name="Structural_Transit_Barrier_Proxy",
            proxy_2_corr=0.31,
            proxy_2_stability=0.86,
            r2_gain=11.4,
            silhouette_score=0.72
        )

        return {
            "intake": intake_res,
            "s1": s1_results,
            "s2": s2_results,
            "s3": s3_results,
            "a2ui_messages": a2ui_messages,
            "a2ui_payload": render_hitl_approval_a2ui(
                problem_statement=problem_statement
            )
        }

    def commit_approval(self, proxy_names: List[str]) -> Dict[str, Any]:
        """Applies approved candidate proxies into the runtime view V_combined."""
        # Update proxy weights
        enriched_proxies = [
            {"zip": "33010", "state": "FL", "hcc_inefficiency_score": 2.20, "structural_barrier_risk": 0.88, "air_quality_proxy": 0.94},
            {"zip": "33142", "state": "FL", "hcc_inefficiency_score": 2.15, "structural_barrier_risk": 0.85, "air_quality_proxy": 0.91},
            {"zip": "93201", "state": "CA", "hcc_inefficiency_score": 1.95, "structural_barrier_risk": 0.78, "air_quality_proxy": 0.89},
            {"zip": "77012", "state": "TX", "hcc_inefficiency_score": 1.82, "structural_barrier_risk": 0.74, "air_quality_proxy": 0.86},
            {"zip": "45202", "state": "OH", "hcc_inefficiency_score": 1.70, "structural_barrier_risk": 0.68, "air_quality_proxy": 0.82}
        ]
        count = self.db.commit_proxies_to_view(enriched_proxies)
        return {
            "status": "COMMITTED",
            "committed_count": count,
            "view": "V_combined",
            "message": f"Successfully committed {len(proxy_names)} proxy features to runtime view V_combined across {count} ZIP clusters."
        }


# Singleton instance
_PEA_INSTANCE: Optional[MockPEAEngine] = None

def get_pea_engine() -> MockPEAEngine:
    """Returns or creates the shared MockPEAEngine instance."""
    global _PEA_INSTANCE
    if _PEA_INSTANCE is None:
        _PEA_INSTANCE = MockPEAEngine()
    return _PEA_INSTANCE
