# Compensation Equity Engine - Data Dictionary

## 1. Role (`roles.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `role_id` | VARCHAR(16) | Yes | PK | e.g., `ROLE-001` | Pattern `^ROLE-[0-9]{3}$` |
| `title` | VARCHAR(64) | Yes | No | Free text (e.g., `Backend Engineer`) | Not empty |
| `job_family` | VARCHAR(32) | Yes | No | `ENGINEERING`, `PRODUCT`, `GTM`, `G&A` | Enum check |

## 2. Level (`levels.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `level_id` | VARCHAR(16) | Yes | PK | e.g., `LVL-01` | Pattern `^LVL-[0-9]{2}$` |
| `level_code` | VARCHAR(8) | Yes | Unique | `L1` to `L8` | Enum check |
| `name` | VARCHAR(32) | Yes | No | `Junior`, `Associate`, `Mid`, `Senior`, `Staff`, `Principal`, `Director`, `VP` | Enum check |
| `seniority_order` | INT | Yes | Unique | 1 to 8 | Integer between 1 and 8 |

## 3. Location (`locations.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `location_id` | VARCHAR(16) | Yes | PK | e.g., `LOC-NYC` | Pattern `^LOC-[A-Z]{3}$` |
| `city` | VARCHAR(64) | Yes | No | Free text | Not empty |
| `country` | VARCHAR(64) | Yes | No | ISO country or standard name | Not empty |
| `currency` | VARCHAR(3) | Yes | No | `USD`, `EUR`, `GBP`, `CAD`, `INR` | 3-letter currency code |
| `cost_index` | NUMERIC(4,2) | Yes | No | Ratio (relative to baseline 1.00) | Must be > 0.0 |

## 4. CompensationBand (`compensation_bands.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `band_id` | VARCHAR(64) | Yes | PK | Format: `BAND-<role>-<lvl>-<loc>-<yr>` | Deterministic format |
| `role_id` | VARCHAR(16) | Yes | FK | References `Role.role_id` | Valid FK |
| `level_id` | VARCHAR(16) | Yes | FK | References `Level.level_id` | Valid FK |
| `location_id` | VARCHAR(16) | Yes | FK | References `Location.location_id` | Valid FK |
| `effective_year` | INT | Yes | No | 2024, 2025, 2026 | Valid year |
| `effective_start` | DATE | Yes | No | `YYYY-MM-DD` | `effective_start <= effective_end` |
| `effective_end` | DATE | Yes | No | `YYYY-MM-DD` | `effective_end >= effective_start` |
| `min_base_local` | NUMERIC(12,2) | Yes | No | Local currency | `> 0` and `< mid_base_local` |
| `mid_base_local` | NUMERIC(12,2) | Yes | No | Local currency | `> min_base_local` and `< max_base_local` |
| `max_base_local` | NUMERIC(12,2) | Yes | No | Local currency | `> mid_base_local` |
| `currency` | VARCHAR(3) | Yes | No | Matches `Location.currency` | Valid ISO currency |

## 5. Employee (`employees.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `emp_id` | VARCHAR(16) | Yes | PK | `EMP-000001` to `EMP-999999` | Pattern `^EMP-[0-9]{6}$` |
| `gender` | VARCHAR(16) | Yes | No | `Female`, `Male`, `Non-Binary` | Enum check |
| `ethnicity` | VARCHAR(32) | Yes | No | Demographic classifications | Enum check |
| `hire_date` | DATE | Yes | No | `YYYY-MM-DD` | Not in future |
| `role_id` | VARCHAR(16) | Yes | FK | References `Role.role_id` | Valid FK |
| `level_id` | VARCHAR(16) | Yes | FK | References `Level.level_id` | Valid FK |
| `location_id` | VARCHAR(16) | Yes | FK | References `Location.location_id` | Valid FK |
| `fte` | NUMERIC(3,2) | Yes | No | Fraction: 0.10 to 1.00 | `fte > 0 AND fte <= 1.0` |
| `status` | VARCHAR(16) | Yes | No | `ACTIVE`, `TERMINATED` | Enum check |

## 6. SalaryRecord (`salary_records.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `salary_rec_id` | VARCHAR(32) | Yes | PK | `SAL-<emp_id>-<YYYY>-<MM>` | Deterministic format |
| `emp_id` | VARCHAR(16) | Yes | FK | References `Employee.emp_id` | Valid FK |
| `effective_date` | DATE | Yes | No | `YYYY-MM-DD` | Effective timestamp |
| `base_salary_local` | NUMERIC(12,2) | Yes | No | Local currency | Must be positive |
| `currency` | VARCHAR(3) | Yes | No | ISO currency code | Matches employee location currency |
| `fte` | NUMERIC(3,2) | Yes | No | Snapshot of FTE at date | Between 0.1 and 1.0 |
| `band_id` | VARCHAR(64) | Yes | FK | References `CompensationBand.band_id` | Valid FK (checks date validity) |

## 7. PerformanceEvidence (`performance_evidence.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `perf_id` | VARCHAR(32) | Yes | PK | `PERF-<emp_id>-<YYYY>` | Pattern `^PERF-.*` |
| `emp_id` | VARCHAR(16) | Yes | FK | References `Employee.emp_id` | Valid FK |
| `eval_year` | INT | Yes | No | Calendar year | Between 2020 and 2026 |
| `rating` | NUMERIC(3,2) | Yes | No | Scale 1.00 to 5.00 | `rating >= 1.0 AND rating <= 5.0` |
| `talent_tier` | VARCHAR(16) | Yes | No | `LOW`, `CORE`, `TOP` | Enum check |

## 8. Tenure (`tenure_records.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `tenure_id` | VARCHAR(32) | Yes | PK | `TEN-<emp_id>` | Matches employee |
| `emp_id` | VARCHAR(16) | Yes | FK / Unique | References `Employee.emp_id` | 1:1 with Employee |
| `hire_date` | DATE | Yes | No | `YYYY-MM-DD` | Equal to `Employee.hire_date` |
| `tenure_days` | INT | Yes | No | Integer days | `(snapshot_date - hire_date)` |
| `tenure_years` | NUMERIC(4,2) | Yes | No | Floating years | `tenure_days / 365.25` |

## 9. Promotion (`promotions.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `promo_id` | VARCHAR(32) | Yes | PK | `PROM-<emp_id>-<YYYYMMDD>` | Deterministic format |
| `emp_id` | VARCHAR(16) | Yes | FK | References `Employee.emp_id` | Valid FK |
| `promo_date` | DATE | Yes | No | `YYYY-MM-DD` | After employee hire date |
| `from_level_id` | VARCHAR(16) | Yes | FK | References `Level.level_id` | Valid FK |
| `to_level_id` | VARCHAR(16) | Yes | FK | References `Level.level_id` | `to_level.order > from_level.order` |

## 10. AdjustmentProposal (`adjustment_proposals.csv`)
| Field | Type | Required | Uniqueness | Allowed Values / Units | Validation Rule |
|---|---|---|---|---|---|
| `adj_id` | VARCHAR(32) | Yes | PK | `ADJ-<YYYY>-<counter>` | Pattern `^ADJ-[0-9]{4}-[0-9]{6}$` |
| `emp_id` | VARCHAR(16) | Yes | FK | References `Employee.emp_id` | Valid FK |
| `proposed_amount` | NUMERIC(12,2) | Yes | No | Local currency | Greater than 0 |
| `currency` | VARCHAR(3) | Yes | No | ISO currency | Matches employee currency |
| `reason_code` | VARCHAR(32) | Yes | No | `RETENTION_RISK`, `MARKET_CORRECTION`, `EQUITY_REMEDY` | Enum check |
| `status` | VARCHAR(16) | Yes | No | `DRAFT`, `APPROVED`, `APPLIED`, `REJECTED` | Enum check |
| `approver_id` | VARCHAR(16) | Optional | No | References `Employee.emp_id` | Required if status is `APPLIED` |