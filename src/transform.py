"""
transform.py
Data Transformation, Cleaning, and Star Schema Normalization Module.
Cleans raw transaction records, imputes missing values, engineers business KPIs,
and extracts dimensional entities (Customer, Product, Location, Date, Fact Sales).
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple

def transform_ecommerce_data(
    df_raw: pd.DataFrame,
    processed_dir: str = "data/processed"
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Cleans raw data, engineers derived metrics, and splits into Star Schema tables.
    """
    print("[TRANSFORM] Starting Data Cleaning and Feature Engineering...")
    df = df_raw.copy()
    
    # 1. Deduplication
    initial_count = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    dedup_count = len(df)
    print(f"[TRANSFORM] Removed {initial_count - dedup_count} duplicate records.")

    # 2. Text Normalization and Whitespace Trimming
    text_cols = ["Customer_Name", "Customer_Segment", "Customer_City", "Customer_State",
                 "Customer_Country", "Region", "Category", "Sub_Category", "Brand",
                 "Product_Name", "Ship_Mode", "Payment_Method"]
    
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            if col in ["Category", "Sub_Category", "Customer_Segment", "Region", "Ship_Mode"]:
                df[col] = df[col].str.title()

    # 3. Date Parsing and Filtering Invalid Records
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce", format="%Y-%m-%d")
    df["Ship_Date"] = pd.to_datetime(df["Ship_Date"], errors="coerce", format="%Y-%m-%d")
    
    valid_date_mask = df["Order_Date"].notnull() & df["Ship_Date"].notnull()
    df = df[valid_date_mask].reset_index(drop=True)
    print(f"[TRANSFORM] Retained {len(df)} records after date validation.")

    # 4. Numerical Parsing and Filtering Anomalies
    num_cols = ["Quantity", "Unit_Price", "Discount", "Sales", "Cost", "Profit", "Shipping_Cost", "Customer_Age", "Rating"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    # Exclude invalid quantities or impossible discount rates
    valid_numeric_mask = (
        (df["Quantity"] > 0) &
        (df["Unit_Price"] > 0) &
        (df["Discount"] >= 0.0) &
        (df["Discount"] <= 1.0)
    )
    df = df[valid_numeric_mask].reset_index(drop=True)
    print(f"[TRANSFORM] Retained {len(df)} records after numerical bounds filtering.")

    # 5. Missing Value Imputation
    # Customer Name
    df["Customer_Name"] = df["Customer_Name"].replace({"nan": "Valued Customer", "None": "Valued Customer"})
    df["Customer_Name"] = df["Customer_Name"].fillna("Valued Customer")
    
    # Payment Method
    df["Payment_Method"] = df["Payment_Method"].replace({"nan": "Credit Card", "None": "Credit Card"})
    df["Payment_Method"] = df["Payment_Method"].fillna("Credit Card")
    
    # Customer Age: Impute by Segment Median
    age_medians = df.groupby("Customer_Segment")["Customer_Age"].transform("median")
    df["Customer_Age"] = df["Customer_Age"].fillna(age_medians).fillna(38).astype(int)
    
    # Rating: Impute with median rating (4.0)
    df["Rating"] = df["Rating"].fillna(4.0).astype(int)
    
    # Return Flag
    df["Return_Flag"] = pd.to_numeric(df["Return_Flag"], errors="coerce").fillna(0).astype(int)

    # 6. Feature Engineering and Financial Derived KPIs
    df["Gross_Sales"] = round(df["Unit_Price"] * df["Quantity"], 2)
    df["Discount_Amount"] = round(df["Gross_Sales"] * df["Discount"], 2)
    df["Net_Sales"] = round(df["Gross_Sales"] - df["Discount_Amount"], 2)
    df["Cost_Amount"] = round(df["Cost"], 2)
    df["Gross_Profit"] = round(df["Net_Sales"] - df["Cost_Amount"], 2)
    df["Profit_Margin_Pct"] = np.where(df["Net_Sales"] > 0, round((df["Gross_Profit"] / df["Net_Sales"]) * 100, 2), 0.0)
    
    # Shipping duration in days
    df["Shipping_Duration_Days"] = (df["Ship_Date"] - df["Order_Date"]).dt.days
    df["Shipping_Duration_Days"] = df["Shipping_Duration_Days"].clip(lower=0)

    # Discount Brackets for profitability analysis
    def assign_discount_tier(d):
        if d == 0.0:
            return "None (0%)"
        elif d <= 0.15:
            return "Low (1-15%)"
        elif d <= 0.30:
            return "Medium (16-30%)"
        else:
            return "High (31%+)"
            
    df["Discount_Bracket"] = df["Discount"].apply(assign_discount_tier)
    df["Is_Profitable"] = (df["Gross_Profit"] > 0).astype(int)

    # Add unique line item surrogate ID
    df["Order_Item_ID"] = [f"ITEM-{i+100000}" for i in range(len(df))]

    # 7. Extract Star Schema Dimension Tables
    print("[TRANSFORM] Generating Star Schema relational dimension tables...")
    os.makedirs(processed_dir, exist_ok=True)
    
    # 7a. dim_customer
    dim_customer = df[[
        "Customer_ID", "Customer_Name", "Customer_Segment",
        "Customer_Gender", "Customer_Age"
    ]].drop_duplicates(subset=["Customer_ID"]).reset_index(drop=True)
    dim_customer.columns = ["customer_id", "customer_name", "customer_segment", "gender", "age"]

    # 7b. dim_product
    dim_product = df[[
        "Product_ID", "Product_Name", "Category", "Sub_Category", "Brand", "Unit_Price"
    ]].drop_duplicates(subset=["Product_ID"]).reset_index(drop=True)
    dim_product.columns = ["product_id", "product_name", "category", "sub_category", "brand", "standard_retail_price"]

    # 7c. dim_location
    dim_location = df[[
        "Customer_City", "Customer_State", "Customer_Country", "Region"
    ]].drop_duplicates().reset_index(drop=True)
    dim_location["location_id"] = [f"LOC-{i+1001}" for i in range(len(dim_location))]
    dim_location = dim_location[["location_id", "Customer_City", "Customer_State", "Customer_Country", "Region"]]
    dim_location.columns = ["location_id", "city", "state", "country", "region"]

    # Merge location_id back into main df
    df = df.merge(
        dim_location,
        left_on=["Customer_City", "Customer_State", "Customer_Country", "Region"],
        right_on=["city", "state", "country", "region"],
        how="left"
    )

    # 7d. dim_date
    min_date = df["Order_Date"].min()
    max_date = df["Ship_Date"].max()
    all_dates = pd.date_range(min_date, max_date, freq="D")
    
    dim_date = pd.DataFrame({
        "date_key": all_dates.strftime("%Y-%m-%d"),
        "full_date": all_dates,
        "year": all_dates.year,
        "quarter": all_dates.quarter,
        "quarter_name": "Q" + all_dates.quarter.astype(str),
        "month": all_dates.month,
        "month_name": all_dates.strftime("%B"),
        "week_of_year": all_dates.isocalendar().week,
        "day_of_month": all_dates.day,
        "day_name": all_dates.strftime("%A"),
        "is_weekend": all_dates.dayofweek.isin([5, 6]).astype(int)
    })

    # 7e. fact_sales
    fact_sales = df[[
        "Order_ID", "Order_Item_ID", "Order_Date", "Ship_Date", "Customer_ID",
        "Product_ID", "location_id", "Ship_Mode", "Payment_Method", "Quantity",
        "Unit_Price", "Discount", "Gross_Sales", "Net_Sales", "Cost_Amount",
        "Gross_Profit", "Profit_Margin_Pct", "Shipping_Cost", "Shipping_Duration_Days",
        "Discount_Bracket", "Return_Flag", "Rating", "Is_Profitable"
    ]].copy()
    
    fact_sales["Order_Date"] = fact_sales["Order_Date"].dt.strftime("%Y-%m-%d")
    fact_sales["Ship_Date"] = fact_sales["Ship_Date"].dt.strftime("%Y-%m-%d")
    
    fact_sales.columns = [
        "order_id", "order_item_id", "order_date", "ship_date", "customer_id",
        "product_id", "location_id", "ship_mode", "payment_method", "quantity",
        "unit_price", "discount_rate", "gross_sales", "net_sales", "cost_amount",
        "profit", "profit_margin_pct", "shipping_cost", "shipping_duration_days",
        "discount_bracket", "return_flag", "rating", "is_profitable"
    ]

    # 8. Calculate RFM Customer Segmentation Table
    print("[TRANSFORM] Calculating RFM Customer Segmentation...")
    snapshot_date = pd.to_datetime(df["Order_Date"]).max() + pd.Timedelta(days=1)
    
    rfm = df.groupby("Customer_ID").agg(
        Recency_Days=("Order_Date", lambda d: (snapshot_date - pd.to_datetime(d).max()).days),
        Frequency=("Order_ID", "nunique"),
        Monetary=("Net_Sales", "sum"),
        Total_Profit=("Gross_Profit", "sum"),
        Avg_Order_Value=("Net_Sales", "mean"),
        First_Order_Date=("Order_Date", "min"),
        Last_Order_Date=("Order_Date", "max")
    ).reset_index()

    # R, F, M Scoring (1-5 quintiles)
    rfm["R_Score"] = pd.qcut(rfm["Recency_Days"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_Composite"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    rfm["RFM_Score_Avg"] = round((rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]) / 3.0, 2)

    # Segment Classification
    def assign_rfm_segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        if (r >= 4) and (f >= 4) and (m >= 4):
            return "Champions"
        elif (r >= 3) and (f >= 3):
            return "Loyal Customers"
        elif (r >= 4) and (f <= 2):
            return "Recent New Customers"
        elif (r >= 3) and (m >= 3):
            return "Potential Loyalists"
        elif (r <= 2) and (f >= 3):
            return "At-Risk High Value"
        elif (r == 1) and (f == 1):
            return "Lost Inactive"
        else:
            return "Standard Customers"

    rfm["Customer_Segment_RFM"] = rfm.apply(assign_rfm_segment, axis=1)

    # Save Cleaned and Processed Datasets
    cleaned_flat_path = os.path.join(processed_dir, "ecommerce_cleaned_transactions.csv")
    df.to_csv(cleaned_flat_path, index=False)
    dim_customer.to_csv(os.path.join(processed_dir, "dim_customer.csv"), index=False)
    dim_product.to_csv(os.path.join(processed_dir, "dim_product.csv"), index=False)
    dim_location.to_csv(os.path.join(processed_dir, "dim_location.csv"), index=False)
    dim_date.to_csv(os.path.join(processed_dir, "dim_date.csv"), index=False)
    fact_sales.to_csv(os.path.join(processed_dir, "fact_sales.csv"), index=False)
    rfm.to_csv(os.path.join(processed_dir, "rfm_customer_segments.csv"), index=False)

    print(f"[TRANSFORM] Successfully transformed {len(df)} records and saved Star Schema tables to '{processed_dir}/'.")
    
    star_schema = {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_location": dim_location,
        "dim_date": dim_date,
        "fact_sales": fact_sales,
        "rfm_segments": rfm
    }
    return df, star_schema

if __name__ == "__main__":
    from extract import extract_data
    df_raw, _ = extract_data()
    df_clean, star = transform_ecommerce_data(df_raw)
    print("Cleaned records count:", len(df_clean))
