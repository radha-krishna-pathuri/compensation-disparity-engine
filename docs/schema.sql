-- Schema DDL: 10 Core Entities for Compensation Equity Architecture

CREATE TABLE Role (
    role_id VARCHAR(16) PRIMARY KEY,
    title VARCHAR(64) NOT NULL,
    job_family VARCHAR(32) NOT NULL
);

CREATE TABLE Level (
    level_id VARCHAR(16) PRIMARY KEY,
    level_code VARCHAR(8) UNIQUE NOT NULL,
    name VARCHAR(32) NOT NULL,
    seniority_order INT UNIQUE NOT NULL
);

CREATE TABLE Location (
    location_id VARCHAR(16) PRIMARY KEY,
    city VARCHAR(64) NOT NULL,
    country VARCHAR(64) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    cost_index NUMERIC(4,2) NOT NULL
);

CREATE TABLE CompensationBand (
    band_id VARCHAR(64) PRIMARY KEY,
    role_id VARCHAR(16) REFERENCES Role(role_id),
    level_id VARCHAR(16) REFERENCES Level(level_id),
    location_id VARCHAR(16) REFERENCES Location(location_id),
    effective_year INT NOT NULL,
    effective_start DATE NOT NULL,
    effective_end DATE NOT NULL,
    min_base_local NUMERIC(12,2) NOT NULL,
    mid_base_local NUMERIC(12,2) NOT NULL,
    max_base_local NUMERIC(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    CONSTRAINT chk_band_limits CHECK (min_base_local < mid_base_local AND mid_base_local < max_base_local)
);

CREATE TABLE Employee (
    emp_id VARCHAR(16) PRIMARY KEY,
    gender VARCHAR(16) NOT NULL,
    ethnicity VARCHAR(32) NOT NULL,
    hire_date DATE NOT NULL,
    role_id VARCHAR(16) REFERENCES Role(role_id),
    level_id VARCHAR(16) REFERENCES Level(level_id),
    location_id VARCHAR(16) REFERENCES Location(location_id),
    fte NUMERIC(3,2) NOT NULL CHECK (fte > 0 AND fte <= 1.0),
    status VARCHAR(16) NOT NULL
);

CREATE TABLE SalaryRecord (
    salary_rec_id VARCHAR(32) PRIMARY KEY,
    emp_id VARCHAR(16) REFERENCES Employee(emp_id),
    effective_date DATE NOT NULL,
    base_salary_local NUMERIC(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    fte NUMERIC(3,2) NOT NULL,
    band_id VARCHAR(64) REFERENCES CompensationBand(band_id)
);

CREATE TABLE PerformanceEvidence (
    perf_id VARCHAR(32) PRIMARY KEY,
    emp_id VARCHAR(16) REFERENCES Employee(emp_id),
    eval_year INT NOT NULL,
    rating NUMERIC(3,2) NOT NULL CHECK (rating >= 1.0 AND rating <= 5.0),
    talent_tier VARCHAR(16) NOT NULL
);

CREATE TABLE Tenure (
    tenure_id VARCHAR(32) PRIMARY KEY,
    emp_id VARCHAR(16) UNIQUE REFERENCES Employee(emp_id),
    hire_date DATE NOT NULL,
    tenure_days INT NOT NULL,
    tenure_years NUMERIC(4,2) NOT NULL
);

CREATE TABLE Promotion (
    promo_id VARCHAR(32) PRIMARY KEY,
    emp_id VARCHAR(16) REFERENCES Employee(emp_id),
    promo_date DATE NOT NULL,
    from_level_id VARCHAR(16) REFERENCES Level(level_id),
    to_level_id VARCHAR(16) REFERENCES Level(level_id)
);

CREATE TABLE AdjustmentProposal (
    adj_id VARCHAR(32) PRIMARY KEY,
    emp_id VARCHAR(16) REFERENCES Employee(emp_id),
    proposed_amount NUMERIC(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    reason_code VARCHAR(32) NOT NULL,
    status VARCHAR(16) NOT NULL,
    approver_id VARCHAR(16) REFERENCES Employee(emp_id),
    CONSTRAINT chk_applied_approver CHECK (status != 'APPLIED' OR approver_id IS NOT NULL)
);