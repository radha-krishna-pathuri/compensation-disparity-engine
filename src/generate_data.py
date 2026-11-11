import os
import random
import pandas as pd
import numpy as np
from datetime import date

SEED = 20261022
OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FX_RATES = {
    "USD": 1.00,
    "EUR": 1.08,
    "GBP": 1.27,
    "CAD": 0.74,
    "INR": 0.012
}

ROLES = [
    ("ROLE-001", "Backend Engineer", "ENGINEERING"),
    ("ROLE-002", "Frontend Engineer", "ENGINEERING"),
    ("ROLE-003", "Data Scientist", "ENGINEERING"),
    ("ROLE-004", "Product Manager", "PRODUCT"),
    ("ROLE-005", "Product Designer", "PRODUCT"),
    ("ROLE-006", "Account Executive", "GTM"),
    ("ROLE-007", "Customer Success Mgr", "GTM"),
    ("ROLE-008", "Financial Analyst", "G&A"),
    ("ROLE-009", "HR Business Partner", "G&A"),
    ("ROLE-010", "DevOps Engineer", "ENGINEERING"),
]

LEVELS = [
    ("LVL-01", "L1", "Junior", 1),
    ("LVL-02", "L2", "Associate", 2),
    ("LVL-03", "L3", "Mid", 3),
    ("LVL-04", "L4", "Senior", 4),
    ("LVL-05", "L5", "Staff", 5),
    ("LVL-06", "L6", "Principal", 6),
    ("LVL-07", "L7", "Director", 7),
    ("LVL-08", "L8", "VP", 8),
]

LOCATIONS = [
    ("LOC-NYC", "New York", "USA", "USD", 1.25),
    ("LOC-SFO", "San Francisco", "USA", "USD", 1.30),
    ("LOC-LON", "London", "UK", "GBP", 1.10),
    ("LOC-BER", "Berlin", "Germany", "EUR", 0.95),
    ("LOC-TOR", "Toronto", "Canada", "CAD", 0.90),
    ("LOC-BLR", "Bangalore", "India", "INR", 0.35),
]

YEARS = [2024, 2025, 2026]

def generate_reference_data():
    roles_df = pd.DataFrame(ROLES, columns=["role_id", "title", "job_family"])
    levels_df = pd.DataFrame(LEVELS, columns=["level_id", "level_code", "name", "seniority_order"])
    locations_df = pd.DataFrame(LOCATIONS, columns=["location_id", "city", "country", "currency", "cost_index"])

    bands = []
    base_salaries = {
        "ENGINEERING": 75000,
        "PRODUCT": 72000,
        "GTM": 60000,
        "G&A": 55000
    }

    for y in YEARS:
        eff_start = f"{y}-01-01"
        eff_end = f"{y}-12-31"
        y_factor = 1.0 + (y - 2024) * 0.04

        for r_id, _, fam in ROLES:
            for l_id, _, _, order in LEVELS:
                for loc_id, _, _, curr, c_idx in LOCATIONS:
                    band_id = f"BAND-{r_id}-{l_id}-{loc_id}-{y}"
                    mid_usd = base_salaries[fam] * (1.28 ** (order - 1)) * c_idx * y_factor
                    mid_local = mid_usd / FX_RATES[curr]
                    min_local = round(mid_local * 0.80, 2)
                    max_local = round(mid_local * 1.25, 2)
                    mid_local = round(mid_local, 2)

                    bands.append({
                        "band_id": band_id,
                        "role_id": r_id,
                        "level_id": l_id,
                        "location_id": loc_id,
                        "effective_year": y,
                        "effective_start": eff_start,
                        "effective_end": eff_end,
                        "min_base_local": min_local,
                        "mid_base_local": mid_local,
                        "max_base_local": max_local,
                        "currency": curr
                    })

    bands_df = pd.DataFrame(bands)
    return roles_df, levels_df, locations_df, bands_df

def generate_dataset(num_employees=5000):
    random.seed(SEED)
    np.random.seed(SEED)

    roles_df, levels_df, locations_df, bands_df = generate_reference_data()

    employees = []
    salaries = []
    performances = []
    tenures = []
    promotions = []
    adjustments = []
    ground_truth = []

    bands_indexed = bands_df.set_index(["role_id", "level_id", "location_id", "effective_year"]).to_dict('index')

    genders = ["Female", "Male", "Non-Binary"]
    ethnicities = ["Asian", "Black", "Hispanic/Latino", "White", "Two or More"]
    as_of_date = date(2026, 1, 1)

    for i in range(1, num_employees + 1):
        emp_id = f"EMP-{i:06d}"
        role_id, _, _ = random.choice(ROLES)
        level_id, _, _, sen_order = random.choices(LEVELS, weights=[20, 25, 25, 15, 8, 4, 2, 1])[0]
        loc_id, _, _, curr, _ = random.choice(LOCATIONS)
        gender = random.choices(genders, weights=[45, 50, 5])[0]
        ethnicity = random.choices(ethnicities, weights=[25, 12, 18, 40, 5])[0]

        hire_year = random.choice([2021, 2022, 2023, 2024])
        hire_month = random.randint(1, 12)
        hire_day = random.randint(1, 28)
        hire_date = date(hire_year, hire_month, hire_day)

        fte = 1.0 if random.random() > 0.08 else 0.8
        status = "ACTIVE"

        employees.append({
            "emp_id": emp_id,
            "gender": gender,
            "ethnicity": ethnicity,
            "hire_date": str(hire_date),
            "role_id": role_id,
            "level_id": level_id,
            "location_id": loc_id,
            "fte": fte,
            "status": status
        })

        t_days = (as_of_date - hire_date).days
        tenures.append({
            "tenure_id": f"TEN-{emp_id}",
            "emp_id": emp_id,
            "hire_date": str(hire_date),
            "tenure_days": t_days,
            "tenure_years": round(t_days / 365.25, 2)
        })

        is_unexplained_outlier = (random.random() < 0.015)
        is_expired_band_case = (random.random() < 0.008)
        is_fte_ignored_case = (fte < 1.0 and random.random() < 0.3)
        is_unapproved_adj_case = (random.random() < 0.006)

        for yr in YEARS:
            perf_score = round(min(5.0, max(1.0, random.gauss(3.4, 0.6))), 2)
            tier = "TOP" if perf_score >= 4.2 else ("CORE" if perf_score >= 2.8 else "LOW")
            performances.append({
                "perf_id": f"PERF-{emp_id}-{yr}",
                "emp_id": emp_id,
                "eval_year": yr,
                "rating": perf_score,
                "talent_tier": tier
            })

        if sen_order > 1 and random.random() < 0.25:
            from_lvl = f"LVL-{(sen_order - 1):02d}"
            promotions.append({
                "promo_id": f"PROM-{emp_id}-20250601",
                "emp_id": emp_id,
                "promo_date": "2025-06-01",
                "from_level_id": from_lvl,
                "to_level_id": level_id
            })

        for yr in YEARS:
            sal_date = f"{yr}-01-01"
            rec_id = f"SAL-{emp_id}-{yr}-01"
            target_year = yr if not is_expired_band_case else yr - 1
            band_key = (role_id, level_id, loc_id, target_year if target_year in YEARS else yr)
            band = bands_indexed[band_key]

            tenure_factor = (yr - hire_year) * 0.02
            compa_target = 0.95 + tenure_factor + random.gauss(0.02, 0.02)
            if is_unexplained_outlier:
                compa_target = 0.72  # Clear anomaly below 0.80 bound

            if is_fte_ignored_case:
                base_salary = band["mid_base_local"] * compa_target  # Unscaled full rate
            else:
                base_salary = band["mid_base_local"] * compa_target * fte

            salaries.append({
                "salary_rec_id": rec_id,
                "emp_id": emp_id,
                "effective_date": sal_date,
                "base_salary_local": round(base_salary, 2),
                "currency": curr,
                "fte": fte,
                "band_id": band["band_id"]
            })

            if yr == 2026:
                if is_unexplained_outlier:
                    ground_truth.append({
                        "entity_id": emp_id,
                        "issue_type": "UNEXPLAINED_DISPARITY",
                        "description": "Salary compa-ratio < 0.80 without legitimate performance or tenure factor."
                    })
                if is_expired_band_case:
                    ground_truth.append({
                        "entity_id": rec_id,
                        "issue_type": "EXPIRED_BAND_REFERENCE",
                        "description": f"Salary matched against band expired on {band['effective_end']}."
                    })
                if is_fte_ignored_case:
                    ground_truth.append({
                        "entity_id": rec_id,
                        "issue_type": "FTE_CALCULATION_ERROR",
                        "description": "Base salary ignored fractional FTE."
                    })

        if is_unapproved_adj_case:
            adj_id = f"ADJ-2026-{len(adjustments)+1:06d}"
            adjustments.append({
                "adj_id": adj_id,
                "emp_id": emp_id,
                "proposed_amount": 7500.00,
                "currency": curr,
                "reason_code": "RETENTION_RISK",
                "status": "APPLIED",
                "approver_id": None
            })
            ground_truth.append({
                "entity_id": adj_id,
                "issue_type": "UNAPPROVED_ADJUSTMENT",
                "description": "Adjustment status set to APPLIED without approver signoff."
            })

    return {
        "roles": roles_df,
        "levels": levels_df,
        "locations": locations_df,
        "compensation_bands": bands_df,
        "employees": pd.DataFrame(employees),
        "salary_records": pd.DataFrame(salaries),
        "performance_evidence": pd.DataFrame(performances),
        "tenure_records": pd.DataFrame(tenures),
        "promotions": pd.DataFrame(promotions),
        "adjustment_proposals": pd.DataFrame(adjustments),
        "ground_truth": pd.DataFrame(ground_truth)
    }

def export_all():
    tables = generate_dataset()
    for name, df in tables.items():
        df.to_csv(f"{OUTPUT_DIR}/{name}.csv", index=False)
    print("Exported 10 relational tables + ground_truth.csv successfully.")

if __name__ == "__main__":
    export_all()