# Compensation Equity & Disparity Analysis Engine

An end-to-end analytical pipeline designed to audit enterprise compensation against role, level, location, and legitimate job-related factors (tenure, performance) to isolate unexplained pay disparities and compliance violations.

---

## Architecture & Data Model

The pipeline models enterprise compensation across **10 core relational entities** using deterministic identifiers and referential integrity constraints:

1. **Role** (`roles.csv`): Job titles and functional job families (`ENGINEERING`, `PRODUCT`, `GTM`, `G&A`).
2. **Level** (`levels.csv`): Career ladder levels (`LVL-01` to `LVL-08`, $L1$–$L8$) with strict ordinal ranking.
3. **Location** (`locations.csv`): Geographic tiers, base currencies (`USD`, `EUR`, `GBP`, `CAD`, `INR`), and cost-of-labor indices.
4. **CompensationBand** (`compensation_bands.csv`): Effective-dated salary ranges (`min`, `mid`, `max`) per role/level/location combination across 3 calendar years (2024–2026).
5. **Employee** (`employees.csv`): Demographic attributes, hire dates, job assignments, and FTE status for 5,000 employees.
6. **SalaryRecord** (`salary_records.csv`): 3-year historical compensation event snapshots linked to effective bands.
7. **PerformanceEvidence** (`performance_evidence.csv`): Annual evaluations and ratings ($1.00$–$5.00$).
8. **Tenure** (`tenure_records.csv`): Derived tenure metrics (days and fractional years) relative to the evaluation date.
9. **Promotion** (`promotions.csv`): Upward level transitions preserving career progression history.
10. **AdjustmentProposal** (`adjustment_proposals.csv`): Audit log of equity adjustments, reason codes, statuses, and approver IDs.

* **Ground Truth** (`ground_truth.csv`): Isolated label store containing injected edge cases and system anomalies (never leaked to model feature inputs).

---

## Core Capabilities & Analysis Workflow

1. **Deterministic Data Synthesis:**
   - Generates 5,000 employees, 200 role/level pairings, and 3 years of longitudinal salary records using a fixed pseudo-random seed (`20261022`).
   - Ensures byte-level reproducibility across repeated executions.

2. **Multi-Currency & FTE Normalization:**
   - Normalizes local currencies to a unified USD baseline using spot exchange rates.
   - Converts fractional FTE salaries ($0.80$ FTE) to annualized full-time equivalents to prevent false underpayment flags.

3. **Effective-Dated Band Joining & Range Metrics:**
   - Matches transactions against corresponding temporal bands.
   - Computes **Compa-Ratio** ($\frac{\text{Annualized FTE Salary}}{\text{Band Midpoint}}$) and **Range Penetration** ($\frac{\text{Salary} - \text{Min}}{\text{Max} - \text{Min}}$).

4. **Policy Exception & Violation Detection:**
   - Identifies salaries referencing expired compensation bands.
   - Isolates out-of-process adjustments marked `APPLIED` without an authorized `approver_id`.
   - Surfaces unscaled part-time base pay errors.

5. **Multivariate Statistical Disparity Modeling:**
   - Employs an Ordinary Least Squares (OLS) regression:
     $$\ln(\text{Salary}) = \beta_0 + \beta_1(\text{Role}) + \beta_2(\text{Level}) + \beta_3(\text{Location}) + \beta_4(\text{Tenure}) + \beta_5(\text{Rating}) + \beta_6(\text{Gender}) + \beta_7(\text{Ethnicity}) + \epsilon$$
   - Controls for legitimate business drivers before evaluating demographic parity.

6. **Remediation Proposals:**
   - Generates targeted, auditable salary adjustments bringing under-range employees with solid performance ($\ge 3.0$) up to target compa-ratio standards ($0.90$).

---

## Directory Structure

```text
CompenAnalys/
├── data/
│   ├── raw/                  # 10 synthetic entity CSVs + ground_truth.csv
│   └── processed/            # Generated adjustment proposals
├── docs/
│   ├── data_dictionary.md    # Field types, enums, units, and validation rules
│   └── schema.sql            # Relational DDL definitions and constraints
├── src/
│   ├── __init__.py
│   ├── generate_data.py      # Deterministic data generation engine
│   ├── engine.py             # Normalization, anomaly scan, and OLS regression
│   └── main.py               # End-to-end execution pipeline
├── tests/
│   └── test_pipeline.py      # Determinism, integrity, and recall test suite
├── .gitignore
├── requirements.txt
└── README.md