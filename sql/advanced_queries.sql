-- ==============================================================================
-- advanced_queries.sql
-- E-Commerce Sales, Customer & Profitability Analytics Platform
-- Part 2: Advanced Analytical SQL (Queries 21 to 42+)
-- Featuring: CTEs, Window Functions, LAG/LEAD, Pure SQL RFM, Cohort Retention,
-- Pareto 80/20 Cumulative Distribution, Moving Averages, and Churn Risk Flagging.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 21. MONTH-OVER-MONTH (MoM) REVENUE & PROFIT GROWTH RATE
-- Technique: CTE + LAG() Window Function
-- Business Question: What is the month-over-month revenue percentage change and absolute profit trajectory?
-- ------------------------------------------------------------------------------
WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month,
        d.month_name,
        SUM(f.net_sales) AS current_month_revenue,
        SUM(f.profit) AS current_month_profit
    FROM fact_sales f
    JOIN dim_date d ON f.order_date = d.date_key
    GROUP BY d.year, d.month, d.month_name
),
mom_calc AS (
    SELECT 
        year,
        month,
        month_name,
        ROUND(current_month_revenue, 2) AS revenue,
        ROUND(current_month_profit, 2) AS profit,
        LAG(current_month_revenue, 1) OVER (ORDER BY year, month) AS prev_month_revenue,
        LAG(current_month_profit, 1) OVER (ORDER BY year, month) AS prev_month_profit
    FROM monthly_sales
)
SELECT 
    year,
    month,
    month_name,
    revenue,
    profit,
    ROUND(prev_month_revenue, 2) AS prev_month_revenue,
    ROUND(((revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0)) * 100, 2) AS mom_revenue_growth_pct,
    ROUND(profit - prev_month_profit, 2) AS mom_profit_change_dollars
FROM mom_calc
ORDER BY year, month;

-- ------------------------------------------------------------------------------
-- 22. YEAR-OVER-YEAR (YoY) CATEGORY SALES GROWTH
-- Technique: Multi-level CTE + LAG(..., 12) Window Function
-- Business Question: How has revenue grown compared to the exact same calendar month in the previous year?
-- ------------------------------------------------------------------------------
WITH category_monthly AS (
    SELECT 
        d.year,
        d.month,
        p.category,
        SUM(f.net_sales) AS monthly_sales
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_date d ON f.order_date = d.date_key
    GROUP BY d.year, d.month, p.category
),
yoy_lagged AS (
    SELECT 
        year,
        month,
        category,
        monthly_sales,
        LAG(monthly_sales, 1) OVER (PARTITION BY category, month ORDER BY year) AS same_month_prior_year_sales
    FROM category_monthly
)
SELECT 
    year,
    month,
    category,
    ROUND(monthly_sales, 2) AS current_sales,
    ROUND(same_month_prior_year_sales, 2) AS prior_year_sales,
    ROUND(((monthly_sales - same_month_prior_year_sales) / NULLIF(same_month_prior_year_sales, 0)) * 100, 2) AS yoy_growth_pct
FROM yoy_lagged
WHERE prior_year_sales IS NOT NULL
ORDER BY category, year, month;

-- ------------------------------------------------------------------------------
-- 23. TOP 3 PRODUCTS BY REVENUE WITHIN EACH CATEGORY
-- Technique: DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)
-- Business Question: What are the top 3 highest revenue generating SKUs within every product category?
-- ------------------------------------------------------------------------------
WITH ranked_products AS (
    SELECT 
        p.category,
        p.sub_category,
        p.product_id,
        p.product_name,
        SUM(f.net_sales) AS total_revenue,
        SUM(f.profit) AS total_profit,
        (SUM(f.profit) / SUM(f.net_sales)) * 100 AS profit_margin_pct,
        DENSE_RANK() OVER (PARTITION BY p.category ORDER BY SUM(f.net_sales) DESC) AS rank_in_category
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.category, p.sub_category, p.product_id, p.product_name
)
SELECT 
    category,
    rank_in_category,
    product_id,
    product_name,
    sub_category,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(total_profit, 2) AS total_profit,
    ROUND(profit_margin_pct, 2) AS profit_margin_pct
FROM ranked_products
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- ------------------------------------------------------------------------------
-- 24. CUSTOMER SPEND PERCENTILE RANKING & DECILE ANALYSIS
-- Technique: NTILE(10) Window Function
-- Business Question: How is revenue concentrated across customer spending deciles (10 equal bins)?
-- ------------------------------------------------------------------------------
WITH customer_aggregates AS (
    SELECT 
        customer_id,
        SUM(net_sales) AS customer_total_spend,
        COUNT(DISTINCT order_id) AS total_orders
    FROM fact_sales
    GROUP BY customer_id
),
customer_deciles AS (
    SELECT 
        customer_id,
        customer_total_spend,
        total_orders,
        NTILE(10) OVER (ORDER BY customer_total_spend DESC) AS spend_decile
    FROM customer_aggregates
)
SELECT 
    spend_decile,
    COUNT(customer_id) AS customers_in_decile,
    ROUND(MIN(customer_total_spend), 2) AS min_spend_in_decile,
    ROUND(MAX(customer_total_spend), 2) AS max_spend_in_decile,
    ROUND(SUM(customer_total_spend), 2) AS total_decile_revenue,
    ROUND((SUM(customer_total_spend) / (SELECT SUM(customer_total_spend) FROM customer_aggregates)) * 100, 2) AS revenue_share_pct
FROM customer_deciles
GROUP BY spend_decile
ORDER BY spend_decile ASC;

-- ------------------------------------------------------------------------------
-- 25. PARETO 80/20 ANALYSIS (CUMULATIVE REVENUE SHARE OF PRODUCTS)
-- Technique: Running SUM() OVER (ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
-- Business Question: What percentage of products account for 80% of total company revenue?
-- ------------------------------------------------------------------------------
WITH product_revenue AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        SUM(f.net_sales) AS product_sales
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
),
cumulative_pareto AS (
    SELECT 
        product_id,
        product_name,
        category,
        product_sales,
        SUM(product_sales) OVER (ORDER BY product_sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
        SUM(product_sales) OVER () AS total_company_revenue,
        ROW_NUMBER() OVER (ORDER BY product_sales DESC) AS product_rank,
        COUNT(*) OVER () AS total_products
    FROM product_revenue
)
SELECT 
    product_rank,
    product_id,
    product_name,
    category,
    ROUND(product_sales, 2) AS product_sales,
    ROUND(cumulative_revenue, 2) AS running_cumulative_revenue,
    ROUND((cumulative_revenue / total_company_revenue) * 100, 2) AS cumulative_revenue_pct,
    ROUND((CAST(product_rank AS REAL) / total_products) * 100, 2) AS cumulative_products_pct,
    CASE 
        WHEN (cumulative_revenue / total_company_revenue) <= 0.80 THEN 'Top 80% Contributor'
        ELSE 'Long Tail (Bottom 20%)'
    END AS pareto_classification
FROM cumulative_pareto
ORDER BY product_rank
LIMIT 25;

-- ------------------------------------------------------------------------------
-- 26. PURE SQL RFM CUSTOMER SEGMENTATION
-- Technique: Multi-tier CTEs + NTILE(5) + CASE Classification
-- Business Question: Calculate Recency, Frequency, Monetary scores in pure SQL and segment the customer base.
-- ------------------------------------------------------------------------------
WITH rfm_raw AS (
    SELECT 
        customer_id,
        -- Calculate Recency relative to maximum dataset order date
        CAST((JULIANDAY('2026-01-01') - JULIANDAY(MAX(order_date))) AS INTEGER) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(net_sales) AS monetary
    FROM fact_sales
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT 
        customer_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score, -- Lower recency days = higher score (5)
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_raw
),
rfm_segmented AS (
    SELECT 
        customer_id,
        recency_days,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        (r_score || f_score || m_score) AS rfm_composite,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent New Customers'
            WHEN r_score >= 3 AND m_score >= 3 THEN 'Potential Loyalists'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At-Risk High Value'
            WHEN r_score = 1 AND f_score = 1 THEN 'Lost Inactive'
            ELSE 'Standard Customers'
        END AS rfm_segment
    FROM rfm_scored
)
SELECT 
    rfm_segment,
    COUNT(customer_id) AS total_customers,
    ROUND((CAST(COUNT(customer_id) AS REAL) / (SELECT COUNT(*) FROM rfm_segmented)) * 100, 2) AS customer_share_pct,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_order_frequency,
    ROUND(AVG(monetary), 2) AS avg_monetary_spend,
    ROUND(SUM(monetary), 2) AS total_segment_revenue,
    ROUND((SUM(monetary) / (SELECT SUM(monetary) FROM rfm_segmented)) * 100, 2) AS revenue_share_pct
FROM rfm_segmented
GROUP BY rfm_segment
ORDER BY total_segment_revenue DESC;

-- ------------------------------------------------------------------------------
-- 27. CUSTOMER COHORT RETENTION GRID
-- Technique: Acquisition Month CTE + Cohort Indexing + Conditional Aggregation
-- Business Question: How do monthly customer acquisition cohorts retain and repeat purchase over time?
-- ------------------------------------------------------------------------------
WITH customer_cohort AS (
    -- Step 1: Determine acquisition (first order) month for each customer
    SELECT 
        customer_id,
        STRFTIME('%Y-%m', MIN(order_date)) AS cohort_month
    FROM fact_sales
    GROUP BY customer_id
),
customer_activities AS (
    -- Step 2: Extract all active purchase months per customer
    SELECT DISTINCT 
        f.customer_id,
        c.cohort_month,
        STRFTIME('%Y-%m', f.order_date) AS activity_month,
        -- Calculate month index (number of months since acquisition)
        (CAST(STRFTIME('%Y', f.order_date) AS INTEGER) - CAST(SUBSTR(c.cohort_month, 1, 4) AS INTEGER)) * 12 +
        (CAST(STRFTIME('%m', f.order_date) AS INTEGER) - CAST(SUBSTR(c.cohort_month, 6, 2) AS INTEGER)) AS month_index
    FROM fact_sales f
    JOIN customer_cohort c ON f.customer_id = c.customer_id
)
SELECT 
    cohort_month,
    COUNT(DISTINCT CASE WHEN month_index = 0 THEN customer_id END) AS cohort_size_m0,
    ROUND(COUNT(DISTINCT CASE WHEN month_index = 1 THEN customer_id END) * 100.0 / COUNT(DISTINCT CASE WHEN month_index = 0 THEN customer_id END), 1) AS retention_m1_pct,
    ROUND(COUNT(DISTINCT CASE WHEN month_index = 2 THEN customer_id END) * 100.0 / COUNT(DISTINCT CASE WHEN month_index = 0 THEN customer_id END), 1) AS retention_m2_pct,
    ROUND(COUNT(DISTINCT CASE WHEN month_index = 3 THEN customer_id END) * 100.0 / COUNT(DISTINCT CASE WHEN month_index = 0 THEN customer_id END), 1) AS retention_m3_pct,
    ROUND(COUNT(DISTINCT CASE WHEN month_index = 6 THEN customer_id END) * 100.0 / COUNT(DISTINCT CASE WHEN month_index = 0 THEN customer_id END), 1) AS retention_m6_pct,
    ROUND(COUNT(DISTINCT CASE WHEN month_index = 12 THEN customer_id END) * 100.0 / COUNT(DISTINCT CASE WHEN month_index = 0 THEN customer_id END), 1) AS retention_m12_pct
FROM customer_activities
WHERE cohort_month BETWEEN '2022-01' AND '2023-12'
GROUP BY cohort_month
ORDER BY cohort_month ASC;

-- ------------------------------------------------------------------------------
-- 28. CUSTOMER LIFETIME VALUE (CLV) BY ACQUISITION YEAR
-- Technique: Historical Spend Aggregation + Cohort Analysis
-- Business Question: What is the cumulative historical spend and profit generated per customer by acquisition cohort?
-- ------------------------------------------------------------------------------
WITH customer_first_year AS (
    SELECT 
        customer_id,
        MIN(CAST(SUBSTR(order_date, 1, 4) AS INTEGER)) AS acquisition_year
    FROM fact_sales
    GROUP BY customer_id
)
SELECT 
    cf.acquisition_year,
    COUNT(DISTINCT cf.customer_id) AS acquired_customers,
    COUNT(DISTINCT f.order_id) AS total_orders_placed,
    ROUND(SUM(f.net_sales), 2) AS cumulative_cohort_revenue,
    ROUND(SUM(f.profit), 2) AS cumulative_cohort_profit,
    ROUND(SUM(f.net_sales) / COUNT(DISTINCT cf.customer_id), 2) AS historical_clv_revenue,
    ROUND(SUM(f.profit) / COUNT(DISTINCT cf.customer_id), 2) AS historical_clv_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS cohort_margin_pct
FROM customer_first_year cf
JOIN fact_sales f ON cf.customer_id = f.customer_id
GROUP BY cf.acquisition_year
ORDER BY cf.acquisition_year;

-- ------------------------------------------------------------------------------
-- 29. DISCOUNT ELASTICITY & MARGIN DEGRADATION ANALYSIS
-- Technique: Conditional aggregation & profit loss simulation
-- Business Question: How does gross profit margin deteriorate across discount tiers, and what is total discount given?
-- ------------------------------------------------------------------------------
SELECT 
    discount_bracket,
    COUNT(order_item_id) AS transaction_count,
    ROUND(SUM(gross_sales), 2) AS gross_list_value,
    ROUND(SUM(gross_sales - net_sales), 2) AS total_discount_given,
    ROUND(SUM(net_sales), 2) AS realized_net_sales,
    ROUND(SUM(profit), 2) AS realized_net_profit,
    ROUND((SUM(profit) / SUM(net_sales)) * 100, 2) AS profit_margin_pct,
    ROUND((SUM(gross_sales - net_sales) / SUM(gross_sales)) * 100, 2) AS effective_discount_pct
FROM fact_sales
GROUP BY discount_bracket
ORDER BY effective_discount_pct ASC;

-- ------------------------------------------------------------------------------
-- 30. ROLLING 3-MONTH MOVING AVERAGE OF REVENUE & PROFIT
-- Technique: AVG() OVER (ORDER BY ... ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
-- Business Question: Smooth seasonal fluctuations using a 3-month trailing moving average.
-- ------------------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT 
        d.year,
        d.month,
        d.month_name,
        SUM(f.net_sales) AS revenue,
        SUM(f.profit) AS profit
    FROM fact_sales f
    JOIN dim_date d ON f.order_date = d.date_key
    GROUP BY d.year, d.month, d.month_name
)
SELECT 
    year,
    month,
    month_name,
    ROUND(revenue, 2) AS monthly_revenue,
    ROUND(profit, 2) AS monthly_profit,
    ROUND(AVG(revenue) OVER (ORDER BY year, month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m_avg_revenue,
    ROUND(AVG(profit) OVER (ORDER BY year, month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m_avg_profit
FROM monthly_metrics
ORDER BY year, month;

-- ------------------------------------------------------------------------------
-- 31. CUSTOMER CHURN & INACTIVITY RISK FLAGGING
-- Technique: Recency Thresholds + Frequency Conditionals
-- Business Question: Identify high-frequency customers (> 5 lifetime orders) who have not purchased in > 180 days.
-- ------------------------------------------------------------------------------
WITH customer_activity AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        COUNT(DISTINCT f.order_id) AS lifetime_orders,
        SUM(f.net_sales) AS lifetime_spend,
        MAX(f.order_date) AS last_order_date,
        CAST((JULIANDAY('2026-01-01') - JULIANDAY(MAX(f.order_date))) AS INTEGER) AS days_since_last_order
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    GROUP BY c.customer_id, c.customer_name, c.customer_segment
)
SELECT 
    customer_id,
    customer_name,
    customer_segment,
    lifetime_orders,
    ROUND(lifetime_spend, 2) AS lifetime_spend,
    last_order_date,
    days_since_last_order,
    'High-Priority Reactivation Candidate' AS retention_action
FROM customer_activity
WHERE lifetime_orders >= 5 AND days_since_last_order > 180
ORDER BY lifetime_spend DESC
LIMIT 20;

-- ------------------------------------------------------------------------------
-- 32. MARKET BASKET AFFINITY: CO-PURCHASED SUB-CATEGORIES
-- Technique: Self-join on order_id
-- Business Question: Which sub-categories are most frequently bought together in the same order?
-- ------------------------------------------------------------------------------
SELECT 
    p1.sub_category AS subcategory_a,
    p2.sub_category AS subcategory_b,
    COUNT(DISTINCT f1.order_id) AS co_purchase_frequency
FROM fact_sales f1
JOIN fact_sales f2 ON f1.order_id = f2.order_id AND f1.product_id < f2.product_id
JOIN dim_product p1 ON f1.product_id = p1.product_id
JOIN dim_product p2 ON f2.product_id = p2.product_id
WHERE p1.sub_category <> p2.sub_category
GROUP BY p1.sub_category, p2.sub_category
ORDER BY co_purchase_frequency DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- 33. INTER-ORDER PURCHASE INTERVAL (REPEAT PURCHASE VELOCITY)
-- Technique: LEAD() Window Function over order dates
-- Business Question: What is the average number of days between successive orders for repeat customers?
-- ------------------------------------------------------------------------------
WITH customer_order_sequence AS (
    SELECT DISTINCT 
        customer_id,
        order_id,
        order_date,
        LEAD(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_order_date
    FROM fact_sales
),
interval_diffs AS (
    SELECT 
        customer_id,
        order_id,
        order_date,
        next_order_date,
        CAST((JULIANDAY(next_order_date) - JULIANDAY(order_date)) AS INTEGER) AS days_to_next_order
    FROM customer_order_sequence
    WHERE next_order_date IS NOT NULL
)
SELECT 
    COUNT(days_to_next_order) AS total_repeat_order_intervals,
    ROUND(AVG(days_to_next_order), 1) AS avg_days_between_orders,
    MIN(days_to_next_order) AS min_days_gap,
    MAX(days_to_next_order) AS max_days_gap
FROM interval_diffs;

-- ------------------------------------------------------------------------------
-- 34. REGIONAL SALES CONCENTRATION (HERFINDAHL-HIRSCHMAN INDEX - HHI)
-- Technique: Squared market share summation
-- Business Question: How concentrated is company revenue across geographic regions?
-- ------------------------------------------------------------------------------
WITH regional_shares AS (
    SELECT 
        l.region,
        SUM(f.net_sales) AS region_sales,
        (SUM(f.net_sales) / (SELECT SUM(net_sales) FROM fact_sales)) * 100.0 AS market_share_pct
    FROM fact_sales f
    JOIN dim_location l ON f.location_id = l.location_id
    GROUP BY l.region
)
SELECT 
    region,
    ROUND(region_sales, 2) AS region_sales,
    ROUND(market_share_pct, 2) AS market_share_pct,
    ROUND(market_share_pct * market_share_pct, 2) AS hhi_share_squared
FROM regional_shares
UNION ALL
SELECT 
    'TOTAL HHI INDEX' AS region,
    NULL,
    100.0,
    ROUND(SUM(market_share_pct * market_share_pct), 2)
FROM regional_shares;

-- ------------------------------------------------------------------------------
-- 35. FIRST-TIME PURCHASE VS REPEAT PURCHASE PROFITABILITY
-- Technique: Order sequence numbering
-- Business Question: Is the company more profitable on initial customer acquisition orders or repeat purchases?
-- ------------------------------------------------------------------------------
WITH customer_order_ranks AS (
    SELECT 
        f.order_id,
        f.customer_id,
        f.net_sales,
        f.cost_amount,
        f.profit,
        DENSE_RANK() OVER (PARTITION BY f.customer_id ORDER BY f.order_date) AS order_sequence_num
    FROM fact_sales f
)
SELECT 
    CASE WHEN order_sequence_num = 1 THEN '1. First Acquisition Order' ELSE '2. Subsequent Repeat Order' END AS order_type,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(net_sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(net_sales)) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(net_sales) / COUNT(DISTINCT order_id), 2) AS aov
FROM customer_order_ranks
GROUP BY CASE WHEN order_sequence_num = 1 THEN '1. First Acquisition Order' ELSE '2. Subsequent Repeat Order' END;

-- ------------------------------------------------------------------------------
-- 36. SALES CONTRIBUTION BY CUSTOMER TENURE TIER
-- Technique: Tenure calculation from first order date
-- Business Question: How does revenue break down across customer age in the platform?
-- ------------------------------------------------------------------------------
WITH customer_tenure AS (
    SELECT 
        customer_id,
        CAST((JULIANDAY('2026-01-01') - JULIANDAY(MIN(order_date))) AS INTEGER) AS tenure_days
    FROM fact_sales
    GROUP BY customer_id
),
customer_tenure_brackets AS (
    SELECT 
        customer_id,
        CASE 
            WHEN tenure_days < 180 THEN 'New (< 6 Months)'
            WHEN tenure_days BETWEEN 180 AND 365 THEN 'Developing (6-12 Months)'
            WHEN tenure_days BETWEEN 366 AND 730 THEN 'Established (1-2 Years)'
            ELSE 'Mature (2+ Years)'
        END AS tenure_tier
    FROM customer_tenure
)
SELECT 
    tb.tenure_tier,
    COUNT(DISTINCT tb.customer_id) AS customer_count,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct
FROM fact_sales f
JOIN customer_tenure_brackets tb ON f.customer_id = tb.customer_id
GROUP BY tb.tenure_tier
ORDER BY total_revenue DESC;

-- ------------------------------------------------------------------------------
-- 37. OUTLIER ORDER DETECTION (STATISTICAL ANOMALIES)
-- Technique: Standard deviation and mean calculation CTE
-- Business Question: Flag individual transactions that exceed 3 standard deviations from average order size.
-- ------------------------------------------------------------------------------
WITH order_totals AS (
    SELECT 
        order_id,
        customer_id,
        SUM(net_sales) AS order_total_sales
    FROM fact_sales
    GROUP BY order_id, customer_id
),
stats AS (
    SELECT 
        AVG(order_total_sales) AS mean_sales,
        -- SQLite standard deviation approximation
        AVG(order_total_sales * order_total_sales) - (AVG(order_total_sales) * AVG(order_total_sales)) AS variance_sales
    FROM order_totals
)
SELECT 
    ot.order_id,
    ot.customer_id,
    ROUND(ot.order_total_sales, 2) AS order_revenue,
    ROUND(s.mean_sales, 2) AS benchmark_mean,
    'Statistical High-Value Outlier (> 3 Sigma)' AS outlier_flag
FROM order_totals ot, stats s
WHERE ot.order_total_sales > (s.mean_sales + 3.0 * SQRT(MAX(s.variance_sales, 0)))
ORDER BY ot.order_total_sales DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 38. YEAR-TO-DATE (YTD) CUMULATIVE REVENUE ACCELERATION
-- Technique: SUM() OVER (PARTITION BY year ORDER BY month)
-- Business Question: Track cumulative revenue build-up across months within each fiscal year.
-- ------------------------------------------------------------------------------
WITH monthly_revenue AS (
    SELECT 
        d.year,
        d.month,
        d.month_name,
        SUM(f.net_sales) AS monthly_sales
    FROM fact_sales f
    JOIN dim_date d ON f.order_date = d.date_key
    GROUP BY d.year, d.month, d.month_name
)
SELECT 
    year,
    month,
    month_name,
    ROUND(monthly_sales, 2) AS monthly_sales,
    ROUND(SUM(monthly_sales) OVER (PARTITION BY year ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_ytd_revenue
FROM monthly_revenue
ORDER BY year, month;

-- ------------------------------------------------------------------------------
-- 39. SUB-CATEGORY SHIPPING COST TO REVENUE IMPACT
-- Technique: Ratio analysis & logistics sensitivity
-- Business Question: Which subcategories have high logistics costs eating into net revenue?
-- ------------------------------------------------------------------------------
SELECT 
    p.category,
    p.sub_category,
    ROUND(SUM(f.net_sales), 2) AS net_sales,
    ROUND(SUM(f.shipping_cost), 2) AS total_shipping_costs,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.shipping_cost) / SUM(f.net_sales)) * 100, 2) AS shipping_to_sales_ratio_pct,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY shipping_to_sales_ratio_pct DESC;

-- ------------------------------------------------------------------------------
-- 40. MULTI-PAYMENT METHOD VALUE COMPARISON
-- Technique: Aggregation by payment instrument
-- Business Question: Does payment method correlate with customer retention or order size?
-- ------------------------------------------------------------------------------
SELECT 
    f.payment_method,
    COUNT(DISTINCT f.customer_id) AS unique_customers_used,
    COUNT(DISTINCT f.order_id) AS total_transactions,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct,
    ROUND(SUM(f.net_sales) / COUNT(DISTINCT f.order_id), 2) AS average_basket_value
FROM fact_sales f
GROUP BY f.payment_method
ORDER BY total_revenue DESC;
