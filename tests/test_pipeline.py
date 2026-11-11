import hashlib
import pandas as pd
import pytest
from src.generate_data import export_all
from src.engine import CompensationEngine

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def test_deterministic_reproducibility():
    export_all()
    emp_hash_1 = get_file_hash("data/raw/employees.csv")
    sal_hash_1 = get_file_hash("data/raw/salary_records.csv")

    export_all()
    emp_hash_2 = get_file_hash("data/raw/employees.csv")
    sal_hash_2 = get_file_hash("data/raw/salary_records.csv")

    assert emp_hash_1 == emp_hash_2
    assert sal_hash_1 == sal_hash_2

def test_referential_integrity():
    engine = CompensationEngine()
    emp_ids = set(engine.employees["emp_id"])
    role_ids = set(pd.read_csv("data/raw/roles.csv")["role_id"])

    assert set(engine.salaries["emp_id"]).issubset(emp_ids)
    assert set(engine.employees["role_id"]).issubset(role_ids)

def test_ground_truth_capture():
    engine = CompensationEngine()
    df = engine.run_normalization_and_enrichment()
    detected_anomalies = engine.detect_exceptions(df)
    ground_truth = pd.read_csv("data/raw/ground_truth.csv")

    detected_ids = set(detected_anomalies["entity_id"])
    gt_ids = set(ground_truth["entity_id"])

    overlap = detected_ids.intersection(gt_ids)
    recall = len(overlap) / len(gt_ids)

    assert recall >= 0.85