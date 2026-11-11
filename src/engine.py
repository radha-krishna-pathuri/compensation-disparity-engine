import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols

FX_RATES = {
    "USD": 1.00,
    "EUR": 1.08,
    "GBP": 1.27,
    "CAD": 0.74,
    "INR": 0.012
}

class CompensationEngine:
    def __init__(self, data_path="data/raw"):
        self.data_path = data_path
        self.load_data()

    def load_data(self):
        self.employees = pd.read_csv(f"{self.data_path}/employees.csv")
        self.salaries = pd.read_csv(f"{self.data_path}/salary_records.csv")
        self.bands = pd.read_csv(f"{self.data_path}/compensation_bands.csv")
        self.performances = pd.read_csv(f"{self.data_path}/performance_evidence.csv")
        self.adjustments = pd.read_csv(f"{self.data_path}/adjustment_proposals.csv")
        self.promotions = pd.read_csv(f"{self.data_path}/promotions.csv")

    def run_normalization_and_enrichment(self) -> pd.DataFrame:
        recent_sal = self.salaries[self.salaries["effective_date"].str.startswith("2026")].copy()
        recent_sal["fx_rate"] = recent_sal["currency"].map(FX_RATES)
        recent_sal["base_usd"] = recent_sal["base_salary_local"] * recent_sal["fx_rate"]
        recent_sal["annualized_fte_salary_usd"] = recent_sal["base_usd"] / recent_sal["fte"]

        df = recent_sal.merge(self.bands, on="band_id", how="left", suffixes=("", "_band"))
        df["band_expired"] = df["effective_year"] != 2026

        df["mid_base_usd"] = (df["mid_base_local"] * df["currency_band"].map(FX_RATES))
        df["min_base_usd"] = (df["min_base_local"] * df["currency_band"].map(FX_RATES))
        df["max_base_usd"] = (df["max_base_local"] * df["currency_band"].map(FX_RATES))

        df["compa_ratio"] = df["annualized_fte_salary_usd"] / df["mid_base_usd"]
        df["range_penetration"] = (
            (df["annualized_fte_salary_usd"] - df["min_base_usd"]) /
            (df["max_base_usd"] - df["min_base_usd"])
        ).clip(0, 1)

        df = df.merge(self.employees, on="emp_id", suffixes=("", "_emp"))
        
        ref_date = pd.to_datetime("2026-01-01")
        df["tenure_years"] = (ref_date - pd.to_datetime(df["hire_date"])).dt.days / 365.25

        avg_perf = self.performances.groupby("emp_id")["rating"].mean().reset_index()
        avg_perf = avg_perf.rename(columns={"rating": "avg_perf_rating"})
        df = df.merge(avg_perf, on="emp_id", how="left")

        return df

    def detect_exceptions(self, df: pd.DataFrame) -> pd.DataFrame:
        anomalies = []

        # Rule 1: Expired compensation band
        expired = df[df["band_expired"]]
        for _, row in expired.iterrows():
            anomalies.append({
                "entity_id": row["salary_rec_id"],
                "rule": "RULE_EXPIRED_BAND",
                "severity": "HIGH",
                "detail": f"Band effective year is {row['effective_year']} but salary date is {row['effective_date']}"
            })

        # Rule 2: Unapproved Adjustments
        unapproved = self.adjustments[
            (self.adjustments["status"] == "APPLIED") & (self.adjustments["approver_id"].isna())
        ]
        for _, row in unapproved.iterrows():
            anomalies.append({
                "entity_id": row["adj_id"],
                "rule": "RULE_UNAPPROVED_ADJUSTMENT",
                "severity": "CRITICAL",
                "detail": "Adjustment marked APPLIED without valid approver_id."
            })

        # Rule 3: Extreme Compa-Ratio Outliers (< 0.80)
        outliers = df[df["compa_ratio"] < 0.80]
        for _, row in outliers.iterrows():
            anomalies.append({
                "entity_id": row["emp_id"],
                "rule": "RULE_BAND_OUTLIER",
                "severity": "MEDIUM",
                "detail": f"Compa-ratio {row['compa_ratio']:.2f} falls outside allowable bounds."
            })

        # Rule 4: Part-time FTE unscaled compensation error
        # If unscaled, annualized_fte_salary_usd / mid_base_usd inflates compa_ratio significantly beyond normal 1.0 FTE expectations (> 1.20)
        fte_errors = df[(df["fte"] < 1.0) & (df["compa_ratio"] > 1.18)]
        for _, row in fte_errors.iterrows():
            anomalies.append({
                "entity_id": row["salary_rec_id"],
                "rule": "RULE_FTE_CALCULATION_ERROR",
                "severity": "HIGH",
                "detail": f"Part-time FTE {row['fte']} base salary appears unpro-rated against band."
            })

        return pd.DataFrame(anomalies)

    def analyze_equity_regression(self, df: pd.DataFrame):
        df_model = df.dropna(subset=["annualized_fte_salary_usd", "tenure_years", "avg_perf_rating"]).copy()
        df_model["log_salary"] = np.log(df_model["annualized_fte_salary_usd"])
        formula = "log_salary ~ C(role_id) + C(level_id) + C(location_id) + tenure_years + avg_perf_rating + C(gender) + C(ethnicity)"
        model = ols(formula, data=df_model).fit()
        return model

    def generate_remediation_proposals(self, df: pd.DataFrame) -> pd.DataFrame:
        underpaid = df[(df["compa_ratio"] < 0.85) & (df["avg_perf_rating"] >= 3.0)].copy()
        proposals = []

        for idx, row in underpaid.iterrows():
            target_salary_usd = row["mid_base_usd"] * 0.90 * row["fte"]
            diff_usd = target_salary_usd - row["base_usd"]
            diff_local = diff_usd / row["fx_rate"]

            proposals.append({
                "proposal_id": f"ADJ-PROP-{row['emp_id']}",
                "emp_id": row["emp_id"],
                "current_salary_local": row["base_salary_local"],
                "proposed_adjustment_local": round(diff_local, 2),
                "currency": row["currency"],
                "current_compa_ratio": round(row["compa_ratio"], 2),
                "target_compa_ratio": 0.90,
                "status": "PENDING_APPROVAL",
                "justification": f"Under-range remedy: rating={row['avg_perf_rating']:.2f}, tenure={row['tenure_years']:.1f}y"
            })

        return pd.DataFrame(proposals)