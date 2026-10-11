-- ==============================================================================
-- schema.sql
-- E-Commerce Sales, Customer & Profitability Analytics Platform
-- Relational Star Schema DDL (ANSI SQL / PostgreSQL & SQLite Compatible)
-- ==============================================================================

-- 1. DROP EXISTING OBJECTS (FOR REPEATABLE RUNS)
DROP VIEW IF EXISTS vw_monthly_category_performance;
DROP VIEW IF EXISTS vw_customer_rfm_summary;
DROP VIEW IF EXISTS vw_sales_summary;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS rfm_customer_segments;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;

-- ==============================================================================
-- 2. DIMENSION TABLES
-- ==============================================================================

-- Dimension: Customer
CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    gender VARCHAR(10),
    age INTEGER
);

-- Dimension: Product
CREATE TABLE dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    standard_retail_price NUMERIC(10, 2) NOT NULL
);

-- Dimension: Location
CREATE TABLE dim_location (
    location_id VARCHAR(50) PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL
);

-- Dimension: Date
CREATE TABLE dim_date (
    date_key VARCHAR(10) PRIMARY KEY, -- Format: YYYY-MM-DD
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

-- ==============================================================================
-- 3. FACT TABLE: fact_sales
-- ==============================================================================

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
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    discount_rate NUMERIC(5, 4) NOT NULL CHECK (discount_rate >= 0.0 AND discount_rate <= 1.0),
    gross_sales NUMERIC(12, 2) NOT NULL,
    net_sales NUMERIC(12, 2) NOT NULL,
    cost_amount NUMERIC(12, 2) NOT NULL,
    profit NUMERIC(12, 2) NOT NULL,
    profit_margin_pct NUMERIC(6, 2) NOT NULL,
    shipping_cost NUMERIC(10, 2) NOT NULL,
    shipping_duration_days INTEGER NOT NULL,
    discount_bracket VARCHAR(50) NOT NULL,
    return_flag INTEGER NOT NULL DEFAULT 0 CHECK (return_flag IN (0, 1)),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    is_profitable INTEGER NOT NULL CHECK (is_profitable IN (0, 1)),
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES dim_product (product_id),
    CONSTRAINT fk_sales_location FOREIGN KEY (location_id) REFERENCES dim_location (location_id),
    CONSTRAINT fk_sales_date FOREIGN KEY (order_date) REFERENCES dim_date (date_key)
);

-- Dimension/Summary: RFM Customer Segments
CREATE TABLE rfm_customer_segments (
    customer_id VARCHAR(50) PRIMARY KEY,
    recency_days INTEGER NOT NULL,
    frequency INTEGER NOT NULL,
    monetary NUMERIC(12, 2) NOT NULL,
    total_profit NUMERIC(12, 2) NOT NULL,
    avg_order_value NUMERIC(10, 2) NOT NULL,
    first_order_date VARCHAR(10),
    last_order_date VARCHAR(10),
    r_score INTEGER NOT NULL CHECK (r_score BETWEEN 1 AND 5),
    f_score INTEGER NOT NULL CHECK (f_score BETWEEN 1 AND 5),
    m_score INTEGER NOT NULL CHECK (m_score BETWEEN 1 AND 5),
    rfm_composite VARCHAR(10) NOT NULL,
    rfm_score_avg NUMERIC(4, 2) NOT NULL,
    customer_segment_rfm VARCHAR(50) NOT NULL,
    CONSTRAINT fk_rfm_customer FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id)
);

-- ==============================================================================
-- 4. PERFORMANCE INDEXES
-- ==============================================================================

CREATE INDEX idx_fact_sales_order_date ON fact_sales (order_date);
CREATE INDEX idx_fact_sales_customer_id ON fact_sales (customer_id);
CREATE INDEX idx_fact_sales_product_id ON fact_sales (product_id);
CREATE INDEX idx_fact_sales_location_id ON fact_sales (location_id);
CREATE INDEX idx_fact_sales_order_id ON fact_sales (order_id);
CREATE INDEX idx_dim_product_cat_subcat ON dim_product (category, sub_category);
CREATE INDEX idx_dim_location_reg_state ON dim_location (region, state);
CREATE INDEX idx_dim_date_yr_mo ON dim_date (year, month);

-- ==============================================================================
-- 5. ANALYTICAL BUSINESS VIEWS
-- ==============================================================================

-- View 1: Unified Sales Transaction Summary View
CREATE VIEW vw_sales_summary AS
SELECT 
    f.order_id,
    f.order_item_id,
    f.order_date,
    f.ship_date,
    d.year,
    d.quarter_name,
    d.month,
    d.month_name,
    d.day_name,
    d.is_weekend,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.gender AS customer_gender,
    c.age AS customer_age,
    l.city,
    l.state,
    l.region,
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    p.brand,
    f.ship_mode,
    f.payment_method,
    f.quantity,
    f.unit_price,
    f.discount_rate,
    f.discount_bracket,
    f.gross_sales,
    f.net_sales,
    f.cost_amount,
    f.profit,
    f.profit_margin_pct,
    f.shipping_cost,
    f.shipping_duration_days,
    f.return_flag,
    f.rating,
    f.is_profitable
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_location l ON f.location_id = l.location_id
JOIN dim_date d ON f.order_date = d.date_key;

-- View 2: Monthly Category Performance Rollup
CREATE VIEW vw_monthly_category_performance AS
SELECT 
    d.year,
    d.month,
    d.month_name,
    p.category,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.net_sales), 2) AS total_net_sales,
    ROUND(SUM(f.cost_amount), 2) AS total_cost,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / NULLIF(SUM(f.net_sales), 0)) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(f.discount_rate) * 100, 2) AS avg_discount_pct,
    ROUND(AVG(f.return_flag) * 100, 2) AS return_rate_pct
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_date d ON f.order_date = d.date_key
GROUP BY d.year, d.month, d.month_name, p.category;

-- View 3: Customer Value & RFM Profile View
CREATE VIEW vw_customer_rfm_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.gender,
    c.age,
    r.recency_days,
    r.frequency,
    r.monetary,
    r.total_profit,
    r.avg_order_value,
    r.r_score,
    r.f_score,
    r.m_score,
    r.rfm_composite,
    r.customer_segment_rfm
FROM dim_customer c
JOIN rfm_customer_segments r ON c.customer_id = r.customer_id;
