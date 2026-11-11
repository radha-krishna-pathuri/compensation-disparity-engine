import os
from src.generate_data import export_all
from src.engine import CompensationEngine

def main():
    print("Step 1: Generating synthetic records...")
    export_all()

    print("\nStep 2: Loading & Normalizing Data...")
    engine = CompensationEngine()
    df = engine.run_normalization_and_enrichment()

    print("\nStep 3: Detecting Violations & Band Exceptions...")
    exceptions = engine.detect_exceptions(df)
    print(f"Total Policy Exceptions Isolated: {len(exceptions)}")
    print(exceptions.head(5))

    print("\nStep 4: Running Multivariate OLS Regression...")
    model = engine.analyze_equity_regression(df)
    print(model.summary().tables[1])

    print("\nStep 5: Generating Remediation Proposals...")
    proposals = engine.generate_remediation_proposals(df)
    os.makedirs("data/processed", exist_ok=True)
    proposals.to_csv("data/processed/adjustment_proposals.csv", index=False)
    print(f"Remediation plans generated for {len(proposals)} eligible employees.")

if __name__ == "__main__":
    main()