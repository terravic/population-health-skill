"""
Mock In-Memory Database Engine for Population Health Skill.
Loads synthetic JSON datasets into an in-memory SQLite database and serves
the runtime view V_combined with zero cloud dependencies.
"""

import json
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


class MockDatabase:
    """In-memory SQLite database managing Population Health member, geospatial, baseline, and proxy data."""

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or DATA_DIR
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self._load_datasets()
        self._create_views()

    def _init_schema(self):
        """Initializes relational tables for members, geo context, proxies, and baseline."""
        cur = self.conn.cursor()
        
        cur.execute("""
            CREATE TABLE members (
                member_id TEXT PRIMARY KEY,
                age INTEGER,
                gender TEXT,
                state TEXT,
                state_fips TEXT,
                zip TEXT,
                chronic_conditions TEXT,
                hcc_score REAL,
                total_cost REAL
            );
        """)

        cur.execute("""
            CREATE TABLE geo_pdi (
                state TEXT,
                state_fips TEXT,
                zip TEXT PRIMARY KEY,
                pdi_embedding TEXT,
                aqi_pm25 REAL,
                pollen_upi REAL,
                food_desert_index REAL,
                transit_accessibility_score REAL,
                composite_environmental_risk REAL
            );
        """)

        cur.execute("""
            CREATE TABLE proxies (
                zip TEXT PRIMARY KEY,
                state TEXT,
                hcc_inefficiency_score REAL,
                structural_barrier_risk REAL,
                air_quality_proxy REAL
            );
        """)

        cur.execute("""
            CREATE TABLE baseline_stats (
                cluster TEXT,
                feature_source TEXT,
                feature_type TEXT,
                feature_name TEXT,
                category_level TEXT,
                method TEXT,
                population_value REAL
            );
        """)
        self.conn.commit()

    def _load_datasets(self):
        """Loads JSON files from data directory into SQLite tables."""
        cur = self.conn.cursor()

        # 1. Members
        members_path = os.path.join(self.data_dir, "synthetic_members.json")
        if os.path.exists(members_path):
            with open(members_path) as f:
                members = json.load(f)
            cur.executemany("""
                INSERT INTO members VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, [
                (
                    m["member_id"],
                    m["age"],
                    m["gender"],
                    m["state"],
                    m["state_fips"],
                    m["zip"],
                    json.dumps(m["chronic_conditions"]),
                    m["hcc_score"],
                    m["total_cost"]
                ) for m in members
            ])

        # 2. Geo PDI
        geo_path = os.path.join(self.data_dir, "synthetic_geo_pdi.json")
        if os.path.exists(geo_path):
            with open(geo_path) as f:
                geo_list = json.load(f)
            cur.executemany("""
                INSERT INTO geo_pdi VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, [
                (
                    g["state"],
                    g["state_fips"],
                    g["zip"],
                    json.dumps(g.get("pdi_embedding", [])),
                    g["aqi_pm25"],
                    g["pollen_upi"],
                    g["food_desert_index"],
                    g["transit_accessibility_score"],
                    g["composite_environmental_risk"]
                ) for g in geo_list
            ])

        # 3. Proxies
        proxies_path = os.path.join(self.data_dir, "synthetic_proxies.json")
        if os.path.exists(proxies_path):
            with open(proxies_path) as f:
                proxies = json.load(f)
            cur.executemany("""
                INSERT INTO proxies VALUES (?, ?, ?, ?, ?);
            """, [
                (
                    p["zip"],
                    p["state"],
                    p["hcc_inefficiency_score"],
                    p["structural_barrier_risk"],
                    p["air_quality_proxy"]
                ) for p in proxies
            ])

        # 4. Baseline Stats
        baseline_path = os.path.join(self.data_dir, "synthetic_baseline_stats.json")
        if os.path.exists(baseline_path):
            with open(baseline_path) as f:
                baseline_list = json.load(f)
            cur.executemany("""
                INSERT INTO baseline_stats VALUES (?, ?, ?, ?, ?, ?, ?);
            """, [
                (
                    b["cluster"],
                    b["feature_source"],
                    b["feature_type"],
                    b["feature_name"],
                    b["category_level"],
                    b["method"],
                    b["population_value"]
                ) for b in baseline_list
            ])

        self.conn.commit()

    def _create_views(self):
        """Creates runtime unified view V_combined."""
        cur = self.conn.cursor()
        cur.execute("DROP VIEW IF EXISTS V_combined;")
        cur.execute("""
            CREATE VIEW V_combined AS
            SELECT 
                m.member_id,
                m.age,
                m.gender,
                m.state,
                m.state_fips,
                m.zip,
                m.chronic_conditions,
                m.hcc_score,
                m.total_cost,
                g.aqi_pm25,
                g.pollen_upi,
                g.food_desert_index,
                g.transit_accessibility_score,
                g.composite_environmental_risk,
                COALESCE(p.hcc_inefficiency_score, 1.0) AS hcc_inefficiency_score,
                COALESCE(p.structural_barrier_risk, 0.2) AS structural_barrier_risk,
                COALESCE(p.air_quality_proxy, 0.2) AS air_quality_proxy
            FROM members m
            LEFT JOIN geo_pdi g ON m.zip = g.zip
            LEFT JOIN proxies p ON m.zip = p.zip;
        """)
        self.conn.commit()

    def execute_query(self, sql: str, params: Optional[Tuple] = None) -> Tuple[List[Dict[str, Any]], List[str], List[Any]]:
        """Executes safe SQL against V_combined and returns records, columns, and flattened values_array."""
        cur = self.conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        
        cols = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        
        records = [dict(zip(cols, row)) for row in rows]
        
        # Flatten all scalar numerical & string outputs into values_array for deterministic fact-checking
        values_array = []
        for r in rows:
            for val in r:
                if val is not None:
                    values_array.append(val)
                    
        return records, cols, values_array

    def get_baseline_stats_dict(self) -> Dict[str, float]:
        """Returns baseline population statistics dictionary."""
        records, _, _ = self.execute_query("SELECT feature_name, population_value FROM baseline_stats WHERE cluster = 'ALL';")
        return {r["feature_name"]: r["population_value"] for r in records}

    def get_cohort_summary(
        self,
        state: Optional[str] = "FL",
        age_min: Optional[int] = 40,
        age_max: Optional[int] = 50,
        zips: Optional[List[str]] = None,
        condition: Optional[str] = None,
        min_risk: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calculates cohort summary metrics and comparisons against baseline."""
        conditions = []
        params = []
        if state and state != "ALL":
            conditions.append("state = ?")
            params.append(state)
        if age_min is not None:
            conditions.append("age >= ?")
            params.append(age_min)
        if age_max is not None:
            conditions.append("age <= ?")
            params.append(age_max)
        if condition:
            conditions.append("chronic_conditions LIKE ?")
            params.append(f"%{condition}%")
        if min_risk is not None:
            conditions.append("composite_environmental_risk >= ?")
            params.append(min_risk)
        if zips:
            placeholders = ",".join(["?"] * len(zips))
            conditions.append(f"zip IN ({placeholders})")
            params.extend(zips)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT 
                member_id, age, gender, state, zip, chronic_conditions,
                hcc_score, total_cost, aqi_pm25, pollen_upi,
                composite_environmental_risk, hcc_inefficiency_score
            FROM V_combined
            WHERE {where_clause};
        """
        records, cols, values_array = self.execute_query(sql, tuple(params))

        if not records:
            return {
                "cohort_n": 0,
                "median_cost": 0.0,
                "mean_hcc": 0.0,
                "copd_prevalence": 0.0,
                "composite_risk": 0.0,
                "baseline_cost": 9080.0,
                "baseline_hcc": 1.10,
                "baseline_copd": 0.082,
                "baseline_risk": 0.42,
                "cost_delta_pct": 0.0,
                "hcc_delta_pct": 0.0,
                "copd_delta_pct": 0.0,
                "risk_delta_pct": 0.0,
                "unpriced_liability": 0.0,
                "records": [],
                "values_array": []
            }

        costs = [r["total_cost"] for r in records]
        hccs = [r["hcc_score"] for r in records]
        risks = [r["composite_environmental_risk"] for r in records if r["composite_environmental_risk"] is not None]
        
        copd_count = sum(1 for r in records if "copd" in (r["chronic_conditions"] or ""))
        
        median_cost = float(np.median(costs))
        mean_hcc = float(np.mean(hccs))
        copd_prev = float(copd_count / len(records))
        mean_risk = float(np.mean(risks)) if risks else 0.50

        baseline = self.get_baseline_stats_dict()
        base_cost = baseline.get("total_cost", 9080.0)
        base_hcc = baseline.get("hcc_score", 1.10)
        base_copd = baseline.get("copd_prevalence", 0.082)
        base_risk = baseline.get("composite_risk", 0.42)

        return {
            "cohort_n": len(records),
            "state": state or "ALL",
            "age_min": age_min,
            "age_max": age_max,
            "median_cost": round(median_cost, 2),
            "mean_hcc": round(mean_hcc, 2),
            "copd_prevalence": round(copd_prev, 3),
            "composite_risk": round(mean_risk, 2),
            "baseline_cost": base_cost,
            "baseline_hcc": base_hcc,
            "baseline_copd": base_copd,
            "baseline_risk": base_risk,
            "cost_delta_pct": round(((median_cost - base_cost) / base_cost) * 100, 1),
            "hcc_delta_pct": round(((mean_hcc - base_hcc) / base_hcc) * 100, 1),
            "copd_delta_pct": round(((copd_prev - base_copd) / base_copd) * 100, 1),
            "risk_delta_pct": round(((mean_risk - base_risk) / base_risk) * 100, 1),
            "unpriced_liability": round(max(0, median_cost - base_cost), 2),
            "values_array": values_array[:100]  # sample values for fact checker
        }

    def get_state_aggregates(self) -> List[Dict[str, Any]]:
        """Returns aggregated metrics for all states."""
        sql = """
            SELECT 
                state,
                COUNT(*) as count,
                AVG(total_cost) as avg_cost,
                AVG(hcc_score) as mean_hcc,
                AVG(composite_environmental_risk) as mean_risk,
                AVG(aqi_pm25) as mean_aqi,
                AVG(CASE WHEN chronic_conditions LIKE '%copd%' THEN 1.0 ELSE 0.0 END) as copd_rate
            FROM V_combined
            GROUP BY state
            ORDER BY mean_risk DESC;
        """
        records, _, _ = self.execute_query(sql)
        for r in records:
            st = r["state"]
            st_costs, _, _ = self.execute_query("SELECT total_cost FROM V_combined WHERE state = ?", (st,))
            if st_costs:
                r["median_cost"] = round(float(np.median([c["total_cost"] for c in st_costs])), 2)
            else:
                r["median_cost"] = round(r["avg_cost"], 2)
            r["mean_hcc"] = round(r["mean_hcc"], 2)
            r["mean_risk"] = round(r["mean_risk"], 2)
            r["mean_aqi"] = round(r["mean_aqi"], 1)
            r["copd_rate"] = round(r["copd_rate"], 3)
            r["unpriced_gap"] = round(max(0, r["median_cost"] - 9080.0), 2)
        return records

    def get_longitudinal_monthly_trends(self, state: Optional[str] = None) -> Dict[str, Any]:
        """Returns 12-month synthetic monthly claims cost and AQI trends."""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        base_cost_curve = [740, 720, 750, 760, 750, 770, 760, 780, 750, 760, 770, 770]
        base_aqi_curve = [42, 45, 48, 52, 55, 60, 62, 58, 54, 50, 46, 44]
        
        st = state if state and state != "ALL" else "FL"
        if st == "FL":
            cohort_cost_curve = [1050, 1020, 1080, 1120, 1180, 1260, 1310, 1290, 1220, 1150, 1120, 1100]
            cohort_aqi_curve = [98, 104, 118, 128, 136, 145, 148, 142, 135, 120, 110, 102]
        elif st == "CA":
            cohort_cost_curve = [1020, 980, 1040, 1090, 1160, 1240, 1290, 1270, 1210, 1140, 1090, 1070]
            cohort_aqi_curve = [92, 98, 112, 125, 134, 142, 145, 140, 130, 115, 105, 96]
        elif st == "TX":
            cohort_cost_curve = [990, 960, 1020, 1070, 1140, 1210, 1260, 1240, 1180, 1120, 1080, 1050]
            cohort_aqi_curve = [88, 94, 106, 118, 126, 135, 138, 132, 124, 112, 102, 94]
        elif st == "OH":
            cohort_cost_curve = [970, 940, 990, 1040, 1100, 1170, 1220, 1200, 1140, 1080, 1050, 1030]
            cohort_aqi_curve = [82, 88, 98, 108, 116, 124, 128, 122, 115, 104, 95, 86]
        else:
            cohort_cost_curve = [820, 790, 830, 860, 890, 940, 970, 960, 920, 880, 850, 840]
            cohort_aqi_curve = [55, 60, 68, 75, 82, 88, 92, 87, 80, 72, 64, 58]

        return {
            "months": months,
            "cohort_claims_cost": cohort_cost_curve,
            "baseline_claims_cost": base_cost_curve,
            "cohort_aqi": cohort_aqi_curve,
            "baseline_aqi": base_aqi_curve
        }

    def get_age_gradient_data(self, state: Optional[str] = None) -> Dict[str, Any]:
        """Returns cost and HCC metrics segmented across age brackets."""
        brackets = [
            {"label": "18–29", "min": 18, "max": 29},
            {"label": "30–39", "min": 30, "max": 39},
            {"label": "40–50", "min": 40, "max": 50},
            {"label": "51–64", "min": 51, "max": 64},
            {"label": "65+", "min": 65, "max": 99}
        ]
        
        cohort_costs = []
        baseline_costs = []
        cohort_hccs = []
        baseline_hccs = []

        st_filter = state if state and state != "ALL" else "FL"

        for b in brackets:
            c_sum = self.get_cohort_summary(state=st_filter, age_min=b["min"], age_max=b["max"])
            b_sum = self.get_cohort_summary(state=None, age_min=b["min"], age_max=b["max"])

            cohort_costs.append(c_sum["median_cost"])
            baseline_costs.append(b_sum["median_cost"])
            cohort_hccs.append(c_sum["mean_hcc"])
            baseline_hccs.append(b_sum["mean_hcc"])

        return {
            "brackets": [b["label"] for b in brackets],
            "cohort_costs": cohort_costs,
            "baseline_costs": baseline_costs,
            "cohort_hccs": cohort_hccs,
            "baseline_hccs": baseline_hccs
        }

    def commit_proxies_to_view(self, new_proxies: List[Dict[str, Any]]) -> int:
        """Commits newly approved candidate proxies to database and refreshes view."""
        cur = self.conn.cursor()
        for p in new_proxies:
            cur.execute("""
                INSERT OR REPLACE INTO proxies (zip, state, hcc_inefficiency_score, structural_barrier_risk, air_quality_proxy)
                VALUES (?, ?, ?, ?, ?);
            """, (
                p.get("zip", "33010"),
                p.get("state", "FL"),
                p.get("hcc_inefficiency_score", 2.10),
                p.get("structural_barrier_risk", 0.85),
                p.get("air_quality_proxy", 0.92)
            ))
        self.conn.commit()
        self._create_views()
        return len(new_proxies)


# Singleton instance for module-level access
_DB_INSTANCE: Optional[MockDatabase] = None

def get_database() -> MockDatabase:
    """Returns or creates the shared MockDatabase instance."""
    global _DB_INSTANCE
    if _DB_INSTANCE is None:
        _DB_INSTANCE = MockDatabase()
    return _DB_INSTANCE
