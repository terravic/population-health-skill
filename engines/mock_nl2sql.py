"""
Mock NL2SQL & Cohort Resolver Engine for Population Health Skill.
Translates natural language questions into safe SQL against V_combined,
executes queries in SQLite, and computes delta percentages against baseline statistics.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from engines.mock_database import get_database
from ui.templates_cohort import get_cohort_comparison_surface, render_cohort_a2ui


class MockNL2SQLEngine:
    """NL2SQL Cohort resolution engine with safe query execution against V_combined."""

    def __init__(self):
        self.db = get_database()

    def parse_intent_to_cohort_params(self, natural_language_query: str) -> Dict[str, Any]:
        """Extracts cohort filters (state, age range, condition, risk) from natural language."""
        q = natural_language_query.lower()
        params: Dict[str, Any] = {
            "state": None,
            "age_min": None,
            "age_max": None,
            "condition": None,
            "high_pollution_only": False
        }

        # State extraction
        state_map = {
            "florida": "FL", "fl": "FL",
            "california": "CA", "ca": "CA",
            "texas": "TX", "tx": "TX",
            "ohio": "OH", "oh": "OH",
            "new york": "NY", "ny": "NY",
            "georgia": "GA", "ga": "GA",
            "north carolina": "NC", "nc": "NC",
            "arizona": "AZ", "az": "AZ",
            "michigan": "MI", "mi": "MI",
            "vermont": "VT", "vt": "VT"
        }
        for name, code in state_map.items():
            if re.search(r'\b' + re.escape(name) + r'\b', q):
                params["state"] = code
                break

        # Age range extraction
        age_match = re.search(r'(?:age|aged|ages)\s*(?:between\s*)?(\d{1,2})\s*(?:-|to|and)\s*(\d{1,2})', q)
        if age_match:
            params["age_min"] = int(age_match.group(1))
            params["age_max"] = int(age_match.group(2))
        elif "40-50" in q or "40 to 50" in q or "forties" in q:
            params["age_min"] = 40
            params["age_max"] = 50
        elif "65+" in q or "over 65" in q or "senior" in q:
            params["age_min"] = 65
            params["age_max"] = 85

        # Condition extraction
        if "copd" in q or "respiratory" in q:
            params["condition"] = "copd"
        elif "diabetes" in q:
            params["condition"] = "diabetes"
        elif "hypertension" in q or "blood pressure" in q:
            params["condition"] = "hypertension"

        # Pollution / hot spot flag
        if any(w in q for w in ["pollution", "hot spot", "hotspot", "high risk", "unpriced", "aqi"]):
            params["high_pollution_only"] = True

        # Default fallback for demo
        if not params["state"] and not params["age_min"]:
            params["state"] = "FL"
            params["age_min"] = 40
            params["age_max"] = 50

        return params

    def build_sql_query(self, params: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Constructs parameterized SQL against V_combined."""
        where_clauses = []
        sql_params = []

        if params.get("state"):
            where_clauses.append("state = ?")
            sql_params.append(params["state"])

        if params.get("age_min") is not None:
            where_clauses.append("age >= ?")
            sql_params.append(params["age_min"])

        if params.get("age_max") is not None:
            where_clauses.append("age <= ?")
            sql_params.append(params["age_max"])

        if params.get("condition"):
            where_clauses.append("chronic_conditions LIKE ?")
            sql_params.append(f"%{params['condition']}%")

        if params.get("high_pollution_only"):
            where_clauses.append("composite_environmental_risk >= 0.70")

        where_stmt = " AND ".join(where_clauses) if where_clauses else "1=1"
        sql = f"""
            SELECT 
                member_id, age, gender, state, zip, chronic_conditions,
                hcc_score, total_cost, aqi_pm25, pollen_upi,
                composite_environmental_risk, hcc_inefficiency_score
            FROM V_combined
            WHERE {where_stmt}
            ORDER BY total_cost DESC;
        """
        return sql, sql_params

    def resolve_cohort(
        self,
        query_or_params: Optional[str] = None,
        state: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None
    ) -> Dict[str, Any]:
        """Resolves cohort, executes SQL, computes deltas, and formats Surface 2 A2UI payload."""
        if isinstance(query_or_params, str):
            params = self.parse_intent_to_cohort_params(query_or_params)
        else:
            params = {
                "state": state or "FL",
                "age_min": age_min if age_min is not None else 40,
                "age_max": age_max if age_max is not None else 50,
                "condition": None,
                "high_pollution_only": False
            }

        # Override with explicit kwargs if passed
        if state:
            params["state"] = state
        if age_min is not None:
            params["age_min"] = age_min
        if age_max is not None:
            params["age_max"] = age_max

        sql, sql_params = self.build_sql_query(params)
        records, cols, values_array = self.db.execute_query(sql, tuple(sql_params))

        # Summary statistics calculation
        summary = self.db.get_cohort_summary(
            state=params.get("state"),
            age_min=params.get("age_min"),
            age_max=params.get("age_max")
        )

        st = params.get("state", "FL")
        title = f"{st} High-Risk Cohort (Age {params.get('age_min', 40)}–{params.get('age_max', 50)})"
        zips_str = "33010, 33142" if st == "FL" else ("93201, 93706" if st == "CA" else "77012, 77502")

        a2ui_messages = get_cohort_comparison_surface(
            cohort_title=title,
            cohort_zips=zips_str,
            cohort_n=summary["cohort_n"],
            cohort_cost=summary["median_cost"],
            baseline_cost=summary["baseline_cost"],
            cohort_hcc=summary["mean_hcc"],
            baseline_hcc=summary["baseline_hcc"],
            cohort_copd=summary["copd_prevalence"],
            baseline_copd=summary["baseline_copd"],
            cohort_risk=summary["composite_risk"],
            baseline_risk=summary["baseline_risk"],
            state=st,
            age_min=params.get("age_min", 40),
            age_max=params.get("age_max", 50)
        )

        return {
            "query_parsed": params,
            "generated_sql": sql.strip(),
            "summary": summary,
            "total_records_matched": len(records),
            "values_array": values_array,
            "a2ui_messages": a2ui_messages,
            "a2ui_payload": render_cohort_a2ui(
                cohort_title=title,
                cohort_zips=zips_str,
                cohort_n=summary["cohort_n"],
                cohort_cost=summary["median_cost"],
                baseline_cost=summary["baseline_cost"],
                cohort_hcc=summary["mean_hcc"],
                baseline_hcc=summary["baseline_hcc"],
                cohort_copd=summary["copd_prevalence"],
                baseline_copd=summary["baseline_copd"],
                cohort_risk=summary["composite_risk"],
                baseline_risk=summary["baseline_risk"],
                state=st,
                age_min=params.get("age_min", 40),
                age_max=params.get("age_max", 50)
            )
        }


# Singleton instance
_NL2SQL_INSTANCE: Optional[MockNL2SQLEngine] = None

def get_nl2sql_engine() -> MockNL2SQLEngine:
    """Returns or creates the shared MockNL2SQLEngine instance."""
    global _NL2SQL_INSTANCE
    if _NL2SQL_INSTANCE is None:
        _NL2SQL_INSTANCE = MockNL2SQLEngine()
    return _NL2SQL_INSTANCE
