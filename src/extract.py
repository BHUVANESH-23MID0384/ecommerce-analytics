"""
extract.py
Module responsible for raw data ingestion, schema validation, and metadata extraction.
"""

import os
import pandas as pd
from typing import Tuple, Dict, Any

MANDATORY_COLUMNS = [
    "Order_ID", "Order_Date", "Ship_Date", "Ship_Mode",
    "Customer_ID", "Customer_Name", "Customer_Segment", "Customer_City",
    "Customer_State", "Customer_Country", "Region",
    "Product_ID", "Product_Name", "Category", "Sub_Category", "Brand",
    "Quantity", "Unit_Price", "Discount", "Sales", "Cost", "Profit"
]

def extract_data(file_path: str = "data/raw/ecommerce_raw_transactions.csv") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Extracts raw e-commerce transaction data from CSV, validates schema presence,
    and captures operational metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw data file not found at: {file_path}")
    
    print(f"[EXTRACT] Loading raw dataset from: {file_path}")
    df_raw = pd.read_csv(file_path, dtype=str) # Read as raw strings first to preserve anomalies for auditing
    
    # Check for mandatory columns
    missing_cols = [col for col in MANDATORY_COLUMNS if col not in df_raw.columns]
    if missing_cols:
        raise ValueError(f"[EXTRACT ERROR] Raw dataset is missing mandatory columns: {missing_cols}")
        
    metadata = {
        "file_path": file_path,
        "raw_record_count": len(df_raw),
        "raw_column_count": len(df_raw.columns),
        "columns": list(df_raw.columns),
        "memory_usage_mb": round(df_raw.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    }
    
    print(f"[EXTRACT] Ingestion complete. Read {metadata['raw_record_count']} rows across {metadata['raw_column_count']} columns ({metadata['memory_usage_mb']} MB).")
    return df_raw, metadata

if __name__ == "__main__":
    df, meta = extract_data()
    print("Extraction sample:")
    print(df.head(2))
