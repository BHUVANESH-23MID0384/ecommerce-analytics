-- ==============================================================================
-- analysis_queries.sql
-- E-Commerce Sales, Customer & Profitability Analytics Platform
-- Part 1: Core Business, Time-Series, Product, Customer & Regional SQL Queries (1 to 20)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. EXECUTIVE KPI SUMMARY
-- Business Question: What is the overall revenue, profit, gross margin, AOV, order volume, and customer base?
-- ------------------------------------------------------------------------------
SELECT 
    ROUND(SUM(net_sales), 2) AS total_revenue,
    ROUND(SUM(cost_amount), 2) AS total_cost,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(net_sales)) * 100, 2) AS gross_profit_margin_pct,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(order_item_id) AS total_line_items,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT customer_id) AS total_unique_customers,
    ROUND(SUM(net_sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND(AVG(discount_rate) * 100, 2) AS average_discount_pct
FROM fact_sales;

-- ------------------------------------------------------------------------------
-- 2. MONTHLY REVENUE & PROFITABILITY TRENDS
-- Business Question: How do revenue, profit, and profit margins evolve across months and years?
-- ------------------------------------------------------------------------------
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS order_count,
    ROUND(SUM(f.net_sales), 2) AS monthly_revenue,
    ROUND(SUM(f.profit), 2) AS monthly_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_date d ON f.order_date = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- ------------------------------------------------------------------------------
-- 3. QUARTER-OVER-QUARTER (QoQ) PERFORMANCE BREAKDOWN
-- Business Question: What is the revenue and profit contribution by financial quarter?
-- ------------------------------------------------------------------------------
SELECT 
    d.year,
    d.quarter_name,
    COUNT(DISTINCT f.order_id) AS orders,
    ROUND(SUM(f.net_sales), 2) AS quarterly_revenue,
    ROUND(SUM(f.profit), 2) AS quarterly_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct
FROM fact_sales f
JOIN dim_date d ON f.order_date = d.date_key
GROUP BY d.year, d.quarter_name
ORDER BY d.year, d.quarter_name;

-- ------------------------------------------------------------------------------
-- 4. ANNUAL PERFORMANCE BY PRODUCT CATEGORY
-- Business Question: How is each product category performing year over year?
-- ------------------------------------------------------------------------------
SELECT 
    d.year,
    p.category,
    COUNT(DISTINCT f.order_id) AS orders,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.net_sales), 2) AS category_revenue,
    ROUND(SUM(f.profit), 2) AS category_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_date d ON f.order_date = d.date_key
GROUP BY d.year, p.category
ORDER BY d.year, category_revenue DESC;

-- ------------------------------------------------------------------------------
-- 5. TOP 10 REVENUE-GENERATING PRODUCTS
-- Business Question: Which top 10 SKUs generate the most total revenue?
-- ------------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    p.brand,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category, p.brand
ORDER BY total_revenue DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 6. TOP 10 MOST PROFITABLE PRODUCTS
-- Business Question: Which 10 SKUs generate the highest absolute dollar profit?
-- ------------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    p.brand,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category, p.brand
ORDER BY total_profit DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 7. BOTTOM 10 LOSS-MAKING PRODUCTS (MARGIN EROSION ROOT CAUSE)
-- Business Question: Which products generate the greatest financial loss, and what is their discount rate?
-- ------------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct,
    ROUND(AVG(f.discount_rate) * 100, 2) AS avg_discount_pct
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
ORDER BY total_profit ASC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 8. HIGH SALES BUT LOW PROFITABILITY PRODUCTS (POTENTIAL DISCOUNTS EROSION)
-- Business Question: Which products achieve high sales (top 25% revenue) but have margin below 10%?
-- ------------------------------------------------------------------------------
WITH product_stats AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        SUM(f.net_sales) AS revenue,
        SUM(f.profit) AS profit,
        (SUM(f.profit) / SUM(f.net_sales)) * 100 AS margin_pct,
        AVG(f.discount_rate) * 100 AS avg_discount
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category, p.sub_category
)
SELECT 
    product_id,
    product_name,
    category,
    sub_category,
    ROUND(revenue, 2) AS revenue,
    ROUND(profit, 2) AS profit,
    ROUND(margin_pct, 2) AS margin_pct,
    ROUND(avg_discount, 2) AS avg_discount_pct
FROM product_stats
WHERE revenue > 15000 AND margin_pct < 10.0
ORDER BY revenue DESC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- 9. SALES & PROFIT PERFORMANCE BY CUSTOMER SEGMENT
-- Business Question: How does revenue and profitability compare across Consumer, Corporate, and Home Office?
-- ------------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct,
    ROUND(SUM(f.net_sales) / COUNT(DISTINCT f.order_id), 2) AS average_order_value,
    ROUND(SUM(f.net_sales) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;

-- ------------------------------------------------------------------------------
-- 10. REGIONAL SALES & PROFITABILITY BREAKDOWN
-- Business Question: Which geographic regions drive the highest revenue and net profit margins?
-- ------------------------------------------------------------------------------
SELECT 
    l.region,
    COUNT(DISTINCT l.state) AS states_count,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct,
    ROUND(SUM(f.net_sales) / COUNT(DISTINCT f.order_id), 2) AS aov
FROM fact_sales f
JOIN dim_location l ON f.location_id = l.location_id
GROUP BY l.region
ORDER BY total_revenue DESC;

-- ------------------------------------------------------------------------------
-- 11. SHIPPING MODE PROFITABILITY & DELIVERY DURATION
-- Business Question: How do shipping tiers impact gross profit margins and average delivery duration?
-- ------------------------------------------------------------------------------
SELECT 
    f.ship_mode,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS margin_pct,
    ROUND(AVG(f.shipping_cost), 2) AS avg_shipping_cost,
    ROUND(AVG(f.shipping_duration_days), 1) AS avg_delivery_days
FROM fact_sales f
GROUP BY f.ship_mode
ORDER BY total_orders DESC;

-- ------------------------------------------------------------------------------
-- 12. RETURN RATE BY PRODUCT CATEGORY & SUB-CATEGORY
-- Business Question: Which product categories suffer from the highest product return rates?
-- ------------------------------------------------------------------------------
SELECT 
    p.category,
    p.sub_category,
    COUNT(f.order_item_id) AS total_items_sold,
    SUM(f.return_flag) AS total_returns,
    ROUND((CAST(SUM(f.return_flag) AS REAL) / COUNT(f.order_item_id)) * 100, 2) AS return_rate_pct,
    ROUND(SUM(CASE WHEN f.return_flag = 1 THEN f.net_sales ELSE 0 END), 2) AS returned_revenue_value
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY return_rate_pct DESC;

-- ------------------------------------------------------------------------------
-- 13. PAYMENT METHOD DISTRIBUTION & TRANSACTION VALUE
-- Business Question: What is the preferred customer payment method and transaction size?
-- ------------------------------------------------------------------------------
SELECT 
    f.payment_method,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND((SUM(f.net_sales) / (SELECT SUM(net_sales) FROM fact_sales)) * 100, 2) AS revenue_share_pct,
    ROUND(SUM(f.net_sales) / COUNT(DISTINCT f.order_id), 2) AS avg_transaction_value
FROM fact_sales f
GROUP BY f.payment_method
ORDER BY total_orders DESC;

-- ------------------------------------------------------------------------------
-- 14. CUSTOMER DEMOGRAPHIC PREFERENCES (AGE GROUP & GENDER)
-- Business Question: How does spending behavior differ across age demographics and genders?
-- ------------------------------------------------------------------------------
WITH customer_orders AS (
    SELECT 
        c.customer_id,
        c.gender,
        CASE 
            WHEN c.age < 25 THEN '18-24'
            WHEN c.age BETWEEN 25 AND 34 THEN '25-34'
            WHEN c.age BETWEEN 35 AND 49 THEN '35-49'
            WHEN c.age BETWEEN 50 AND 64 THEN '50-64'
            ELSE '65+'
        END AS age_group,
        f.net_sales,
        f.profit
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_id = c.customer_id
)
SELECT 
    age_group,
    gender,
    COUNT(DISTINCT customer_id) AS customer_count,
    ROUND(SUM(net_sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(net_sales), 2) AS avg_spend_per_item
FROM customer_orders
GROUP BY age_group, gender
ORDER BY age_group, gender;

-- ------------------------------------------------------------------------------
-- 15. DISCOUNT BRACKET IMPACT ON PROFIT MARGINS
-- Business Question: How severely does discounting erode gross profit margin percentages?
-- ------------------------------------------------------------------------------
SELECT 
    discount_bracket,
    COUNT(order_item_id) AS item_count,
    ROUND(SUM(net_sales), 2) AS total_sales,
    ROUND(SUM(cost_amount), 2) AS total_cost,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(net_sales)) * 100, 2) AS realized_profit_margin_pct,
    ROUND(AVG(discount_rate) * 100, 2) AS avg_discount_pct
FROM fact_sales
GROUP BY discount_bracket
ORDER BY avg_discount_pct ASC;

-- ------------------------------------------------------------------------------
-- 16. CUSTOMER RATING VS RETURN RATE RELATIONSHIP
-- Business Question: How does customer satisfaction rating correlate with product returns?
-- ------------------------------------------------------------------------------
SELECT 
    rating AS star_rating,
    COUNT(order_item_id) AS total_reviews,
    SUM(return_flag) AS total_returned_items,
    ROUND((CAST(SUM(return_flag) AS REAL) / COUNT(order_item_id)) * 100, 2) AS return_rate_pct,
    ROUND(AVG(net_sales), 2) AS avg_order_item_value
FROM fact_sales
GROUP BY rating
ORDER BY star_rating DESC;

-- ------------------------------------------------------------------------------
-- 17. DAY OF WEEK & WEEKEND SALES PERFORMANCE
-- Business Question: Is there a significant revenue difference between weekday and weekend purchasing?
-- ------------------------------------------------------------------------------
SELECT 
    d.day_name,
    d.is_weekend,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(SUM(f.net_sales) / COUNT(DISTINCT f.order_id), 2) AS aov
FROM fact_sales f
JOIN dim_date d ON f.order_date = d.date_key
GROUP BY d.day_name, d.is_weekend
ORDER BY total_revenue DESC;

-- ------------------------------------------------------------------------------
-- 18. CUSTOMER REPEAT PURCHASE RATE
-- Business Question: What proportion of customer base are repeat purchasers vs one-time buyers?
-- ------------------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(net_sales) AS total_spend
    FROM fact_sales
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN total_orders = 1 THEN '1-Time Buyer'
        WHEN total_orders BETWEEN 2 AND 4 THEN '2-4 Orders (Repeat)'
        WHEN total_orders BETWEEN 5 AND 9 THEN '5-9 Orders (Frequent)'
        ELSE '10+ Orders (Power Buyer)'
    END AS buyer_tier,
    COUNT(customer_id) AS customer_count,
    ROUND((CAST(COUNT(customer_id) AS REAL) / (SELECT COUNT(*) FROM customer_order_counts)) * 100, 2) AS pct_of_customers,
    ROUND(SUM(total_spend), 2) AS tier_revenue,
    ROUND((SUM(total_spend) / (SELECT SUM(total_spend) FROM customer_order_counts)) * 100, 2) AS revenue_share_pct
FROM customer_order_counts
GROUP BY buyer_tier
ORDER BY tier_revenue DESC;

-- ------------------------------------------------------------------------------
-- 19. TOP 1% HIGH-VALUE CUSTOMERS (VIP IDENTIFICATION)
-- Business Question: Who are the top 20 highest lifetime value customers?
-- ------------------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    l.city,
    l.state,
    l.region,
    COUNT(DISTINCT f.order_id) AS lifetime_orders,
    SUM(f.quantity) AS total_units_bought,
    ROUND(SUM(f.net_sales), 2) AS total_lifetime_spend,
    ROUND(SUM(f.profit), 2) AS total_lifetime_profit,
    ROUND((SUM(f.profit) / SUM(f.net_sales)) * 100, 2) AS customer_profit_margin_pct
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_location l ON f.location_id = l.location_id
GROUP BY c.customer_id, c.customer_name, c.customer_segment, l.city, l.state, l.region
ORDER BY total_lifetime_spend DESC
LIMIT 20;

-- ------------------------------------------------------------------------------
-- 20. ORDER BASKET SIZE DISTRIBUTION (UNITS PER LINE ITEM)
-- Business Question: What is the distribution of quantities purchased per order line item?
-- ------------------------------------------------------------------------------
SELECT 
    quantity AS units_purchased,
    COUNT(order_item_id) AS frequency,
    ROUND((CAST(COUNT(order_item_id) AS REAL) / (SELECT COUNT(*) FROM fact_sales)) * 100, 2) AS frequency_pct,
    ROUND(SUM(net_sales), 2) AS total_sales_volume,
    ROUND(AVG(profit_margin_pct), 2) AS avg_margin_pct
FROM fact_sales
GROUP BY quantity
ORDER BY units_purchased ASC;
