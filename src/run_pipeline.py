"""
run_pipeline.py
Master Orchestration Script for E-Commerce Analytics ETL Pipeline.
Executes: Data Generation -> Ingestion -> Quality Audit -> Transformation -> Star Schema Database Load.
"""

import sys
import time
from generate_raw_data import generate_raw_ecommerce_data
from extract import extract_data
from validate import validate_raw_data
from transform import transform_ecommerce_data
from load import load_to_database

def run_full_pipeline(num_records: int = 65000):
    start_time = time.time()
    print("=" * 70)
    print("  E-COMMERCE SALES & PROFITABILITY ANALYTICS PLATFORM - ETL PIPELINE")
    print("=" * 70)
    
    # Step 1: Raw Data Generation (with controlled anomalies)
    print("\n[STEP 1/5] Synthesizing Enterprise Transactional Dataset...")
    raw_path = generate_raw_ecommerce_data(num_records=num_records)
    
    # Step 2: Extraction
    print("\n[STEP 2/5] Extracting & Ingesting Raw Data...")
    df_raw, meta = extract_data(raw_path)
    
    # Step 3: Validation & Data Quality Audit
    print("\n[STEP 3/5] Performing Data Quality Audit...")
    audit_metrics = validate_raw_data(df_raw)
    
    # Step 4: Transformation & Feature Engineering
    print("\n[STEP 4/5] Executing Data Cleaning & Star Schema Deconstruction...")
    df_clean, star_schema = transform_ecommerce_data(df_raw)
    
    # Step 5: Relational Load
    print("\n[STEP 5/5] Loading Star Schema into Relational SQLite Database...")
    conn = load_to_database(star_schema, db_path="ecommerce.db")
    conn.close()
    
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"  ETL PIPELINE COMPLETED SUCCESSFULLY IN {elapsed}s")
    print(f"  - Raw Records: {audit_metrics['total_raw_records']:,}")
    print(f"  - Cleaned Fact Records: {len(star_schema['fact_sales']):,}")
    print(f"  - Unique Customers: {len(star_schema['dim_customer']):,}")
    print(f"  - Unique SKUs: {len(star_schema['dim_product']):,}")
    print(f"  - Database: 'ecommerce.db' (Ready for SQL Queries & Power BI)")
    print("=" * 70)

if __name__ == "__main__":
    records = 65000
    if len(sys.argv) > 1:
        try:
            records = int(sys.argv[1])
        except ValueError:
            pass
    run_full_pipeline(num_records=records)
