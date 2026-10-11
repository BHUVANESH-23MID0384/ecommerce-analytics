"""
load.py
Relational Database Loader Module.
Creates the Star Schema relational database (SQLite/PostgreSQL compatible),
defines primary/foreign key constraints, creates performance indexes,
and loads dimension and fact tables.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict

def load_to_database(
    star_schema: Dict[str, pd.DataFrame],
    db_path: str = "ecommerce.db"
) -> sqlite3.Connection:
    """
    Loads transformed dimension and fact tables into a relational SQLite database
    and builds analytical views and indexes.
    """
    print(f"[LOAD] Initializing relational database at: {db_path}")
    if os.path.exists(db_path):
        os.remove(db_path) # Fresh rebuild for repeatable pipeline runs

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign key constraint support in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Create Schema Tables
    print("[LOAD] Creating Star Schema tables and constraints...")
    
    # dim_customer
    cursor.execute("""
    CREATE TABLE dim_customer (
        customer_id VARCHAR(50) PRIMARY KEY,
        customer_name VARCHAR(150) NOT NULL,
        customer_segment VARCHAR(50),
        gender VARCHAR(10),
        age INTEGER
    );
    """)

    # dim_product
    cursor.execute("""
    CREATE TABLE dim_product (
        product_id VARCHAR(50) PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        category VARCHAR(100) NOT NULL,
        sub_category VARCHAR(100) NOT NULL,
        brand VARCHAR(100),
        standard_retail_price REAL
    );
    """)

    # dim_location
    cursor.execute("""
    CREATE TABLE dim_location (
        location_id VARCHAR(50) PRIMARY KEY,
        city VARCHAR(100) NOT NULL,
        state VARCHAR(100) NOT NULL,
        country VARCHAR(100) NOT NULL,
        region VARCHAR(50) NOT NULL
    );
    """)

    # dim_date
    cursor.execute("""
    CREATE TABLE dim_date (
        date_key VARCHAR(10) PRIMARY KEY,
        full_date DATE NOT NULL,
        year INTEGER NOT NULL,
        quarter INTEGER NOT NULL,
        quarter_name VARCHAR(10) NOT NULL,
        month INTEGER NOT NULL,
        month_name VARCHAR(20) NOT NULL,
        week_of_year INTEGER NOT NULL,
        day_of_month INTEGER NOT NULL,
        day_name VARCHAR(20) NOT NULL,
        is_weekend INTEGER NOT NULL
    );
    """)

    # fact_sales
    cursor.execute("""
    CREATE TABLE fact_sales (
        order_id VARCHAR(50) NOT NULL,
        order_item_id VARCHAR(50) PRIMARY KEY,
        order_date VARCHAR(10) NOT NULL,
        ship_date VARCHAR(10) NOT NULL,
        customer_id VARCHAR(50) NOT NULL,
        product_id VARCHAR(50) NOT NULL,
        location_id VARCHAR(50) NOT NULL,
        ship_mode VARCHAR(50) NOT NULL,
        payment_method VARCHAR(50) NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        discount_rate REAL NOT NULL,
        gross_sales REAL NOT NULL,
        net_sales REAL NOT NULL,
        cost_amount REAL NOT NULL,
        profit REAL NOT NULL,
        profit_margin_pct REAL NOT NULL,
        shipping_cost REAL NOT NULL,
        shipping_duration_days INTEGER NOT NULL,
        discount_bracket VARCHAR(50) NOT NULL,
        return_flag INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        is_profitable INTEGER NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id),
        FOREIGN KEY (product_id) REFERENCES dim_product (product_id),
        FOREIGN KEY (location_id) REFERENCES dim_location (location_id),
        FOREIGN KEY (order_date) REFERENCES dim_date (date_key)
    );
    """)

    # rfm_customer_segments
    cursor.execute("""
    CREATE TABLE rfm_customer_segments (
        customer_id VARCHAR(50) PRIMARY KEY,
        recency_days INTEGER NOT NULL,
        frequency INTEGER NOT NULL,
        monetary REAL NOT NULL,
        total_profit REAL NOT NULL,
        avg_order_value REAL NOT NULL,
        first_order_date VARCHAR(10),
        last_order_date VARCHAR(10),
        r_score INTEGER NOT NULL,
        f_score INTEGER NOT NULL,
        m_score INTEGER NOT NULL,
        rfm_composite VARCHAR(10) NOT NULL,
        rfm_score_avg REAL NOT NULL,
        customer_segment_rfm VARCHAR(50) NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id)
    );
    """)

    # 2. Insert Data
    print("[LOAD] Ingesting dimension and fact records...")
    star_schema["dim_customer"].to_sql("dim_customer", conn, if_exists="append", index=False)
    star_schema["dim_product"].to_sql("dim_product", conn, if_exists="append", index=False)
    star_schema["dim_location"].to_sql("dim_location", conn, if_exists="append", index=False)
    
    # Format dates for dim_date
    date_df = star_schema["dim_date"].copy()
    date_df["full_date"] = date_df["full_date"].astype(str)
    date_df.to_sql("dim_date", conn, if_exists="append", index=False)
    
    star_schema["fact_sales"].to_sql("fact_sales", conn, if_exists="append", index=False)
    
    # RFM table
    rfm_df = star_schema["rfm_segments"].copy()
    rfm_df.columns = [c.lower() for c in rfm_df.columns]
    rfm_df.to_sql("rfm_customer_segments", conn, if_exists="append", index=False)

    # 3. Create Performance Indexes
    print("[LOAD] Building analytical performance indexes...")
    cursor.execute("CREATE INDEX idx_fact_sales_order_date ON fact_sales (order_date);")
    cursor.execute("CREATE INDEX idx_fact_sales_customer_id ON fact_sales (customer_id);")
    cursor.execute("CREATE INDEX idx_fact_sales_product_id ON fact_sales (product_id);")
    cursor.execute("CREATE INDEX idx_fact_sales_location_id ON fact_sales (location_id);")
    cursor.execute("CREATE INDEX idx_dim_product_category ON dim_product (category, sub_category);")
    cursor.execute("CREATE INDEX idx_dim_location_region ON dim_location (region, state);")

    # 4. Create Analytical Views
    cursor.execute("""
    CREATE VIEW vw_sales_summary AS
    SELECT 
        f.order_id,
        f.order_date,
        d.year,
        d.quarter_name,
        d.month_name,
        c.customer_name,
        c.customer_segment,
        l.region,
        l.state,
        l.city,
        p.category,
        p.sub_category,
        p.product_name,
        p.brand,
        f.quantity,
        f.gross_sales,
        f.discount_rate,
        f.net_sales,
        f.cost_amount,
        f.profit,
        f.profit_margin_pct,
        f.shipping_cost,
        f.return_flag
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_date d ON f.order_date = d.date_key;
    """)

    conn.commit()
    
    # Verify Counts
    print("[LOAD] Verification check on loaded entities:")
    for tbl in ["dim_customer", "dim_product", "dim_location", "dim_date", "fact_sales", "rfm_customer_segments"]:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        cnt = cursor.fetchone()[0]
        print(f"  - Table '{tbl}': {cnt:,} rows")

    print("[LOAD] Database loading complete and verified.")
    return conn

if __name__ == "__main__":
    from extract import extract_data
    from transform import transform_ecommerce_data
    df_raw, _ = extract_data()
    _, star = transform_ecommerce_data(df_raw)
    conn = load_to_database(star)
    conn.close()
