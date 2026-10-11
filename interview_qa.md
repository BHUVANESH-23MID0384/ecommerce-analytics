# Comprehensive Data Analyst Interview Preparation Guide

This guide prepares candidates to confidently explain every technical and business dimension of the **E-Commerce Sales, Customer & Profitability Analytics Platform** in hiring manager and campus placement interviews.

---

## 1. Technical Interview Questions & Senior-Level Answers

### Q1: Why did you choose a relational database and a Star Schema design instead of keeping a single flat table?
**Answer**:
> "A single denormalized table creates massive data redundancy, slows down aggregation queries on large datasets, and increases the risk of update anomalies (e.g., updating a customer address requires modifying thousands of past order rows).  
> By deconstructing the transactions into a **Star Schema** with one centralized fact table (`fact_sales`) and clean dimension tables (`dim_customer`, `dim_product`, `dim_location`, `dim_date`), we achieved three key benefits:
> 1. **Storage & Engine Efficiency**: Smaller dictionary encoding in columnar storage engines like Power BI's VertiPaq.
> 2. **Query Performance**: Fact tables contain only foreign keys and numeric metrics, allowing sub-second aggregations via indexed joins.
> 3. **Unambiguous Business Semantics**: Analysts and BI tools can slice and dice metrics without duplicate row counting errors."

---

### Q2: How did you handle data quality issues, and why did you not simply delete all rows with missing values?
**Answer**:
> "In enterprise data engineering, silently deleting rows with missing values introduces severe **selection bias** and distorts financial reporting (e.g., deleting an order because `Customer_Age` was missing would artificially understate total revenue and order volume).  
> We implemented a strict **Problem $\rightarrow$ Decision $\rightarrow$ Reason** governance framework:
> - **Missing Demographics (`Customer_Age`, `Rating`)**: Imputed `Customer_Age` using the median age of that specific customer segment, and imputed categorical fields with `'Unknown'`, preserving 100% of revenue transactions.
> - **Duplicate Records (1.5%)**: Deduplicated based on exact line item signatures keeping the first instance to prevent double-counting.
> - **Corrupted Telemetry (Negative quantities, invalid dates)**: Excluded corrupted entries and logged them in a separate audit exception trail.
> - **Text Inconsistencies**: Normalized all casing with `.str.strip().str.title()` to ensure SQL joins and groupings matched perfectly."

---

### Q3: Why did you use CTEs and Window Functions (`RANK`, `LAG`, `NTILE`) in your SQL queries?
**Answer**:
> "Common Table Expressions (CTEs) make complex analytical logic modular, readable, and maintainable compared to deeply nested subqueries.  
> Window functions allowed us to compute advanced multi-row business calculations in a single SQL scan without expensive self-joins:
> - **`LAG()`**: Used in Month-over-Month and Year-over-Year calculations to retrieve prior period values alongside current period metrics.
> - **`DENSE_RANK() OVER (PARTITION BY ...)`**: Used to identify the top 3 products within each category without collapsing the line-item granularity.
> - **`NTILE(5)` & `NTILE(10)`**: Used in pure SQL to assign quantile scores for RFM segmentation and customer spending deciles.
> - **`SUM() OVER (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`**: Computed running cumulative revenue for our Pareto 80/20 product analysis."

---

### Q4: How did you design and validate your RFM Customer Segmentation model?
**Answer**:
> "We extracted three fundamental behavioral attributes for every customer:
> 1. **Recency ($R$)**: Days since the customer's most recent transaction relative to the dataset snapshot date.
> 2. **Frequency ($F$)**: Total count of distinct orders placed over their lifetime.
> 3. **Monetary ($M$)**: Cumulative net spend.
> 
> Because customer distributions are heavily right-skewed (following a power-law distribution), we used quintile scoring (`qcut` in Python / `NTILE(5)` in SQL) from 1 to 5 to normalize each dimension. We then mapped the composite scores into 7 actionable business segments: *Champions*, *Loyal Customers*, *Potential Loyalists*, *Recent New Customers*, *At-Risk High Value*, *Standard Customers*, and *Lost Inactive*.  
> We validated the model by verifying that Champions generated 61%+ of company profits despite representing only ~22% of the customer base."

---

### Q5: How did you calculate Customer Cohort Retention, and what does it tell you?
**Answer**:
> "We indexed each customer by their **Acquisition Month ($M_0$)**—the month of their very first transaction. For each subsequent transaction, we computed the elapsed month index ($M_n = \text{Order Month} - M_0$).  
> We then pivoted the data into a cohort retention matrix where each cell represents the percentage of the original acquisition cohort that placed at least one order in month $n$.  
> This analysis revealed that customer repeat purchasing stabilizes at approximately 18–22% after month 3, indicating that our primary churn risk occurs between month 1 and month 3 post-acquisition."

---

### Q6: What statistical hypothesis test did you perform, and what was the business interpretation?
**Answer**:
> "We tested whether deep discounting ($\ge 20\%$) leads to statistically significantly lower profit margins than standard pricing.
> - **Null Hypothesis ($H_0$)**: $\mu_{\text{high discount}} = \mu_{\text{low discount}}$
> - **Alternative Hypothesis ($H_1$)**: $\mu_{\text{high discount}} < \mu_{\text{low discount}}$
> 
> We performed a **Welch's two-sample independent t-test** (accounting for unequal sample sizes and variances) and obtained $t = -100.57, p < 0.001$, and a large Cohen's $d$ effect size of $-1.32$.  
> **Critical Interpretation**: We emphasized to management that *correlation does not establish causation*. Discounts stimulate order velocity, but without setting minimum gross margin floors, aggressive discounting actively cannibalizes unit margins and turns high-volume products into loss-makers."

---

### Q7: Why did you choose Power BI, and what DAX best practices did you follow?
**Answer**:
> "Power BI was chosen for its enterprise-grade VertiPaq in-memory engine, rich interactive filtering, and dynamic time-intelligence capabilities.  
> Key DAX best practices followed:
> 1. **`DIVIDE()` over `/`**: Handled zero denominators safely with default return values.
> 2. **Explicit Measures over Implicit Aggregations**: Created a structured Measure Table with display folders.
> 3. **Variables (`VAR / RETURN`)**: Stored intermediate filter calculations to eliminate redundant scalar computations and improve DAX readability.
> 4. **Marked Date Table**: Explicitly marked `dim_date` to disable hidden auto-date hierarchies, maximizing performance."

---

## 2. Business & Strategic Interview Questions

### Q8: What was the single biggest business problem you uncovered in the data?
**Answer**:
> "The single largest financial leak was **uncontrolled promotional discounting on low-margin products**. Orders with discounts of 30% or higher generated **-$84K in direct losses** at an average realized profit margin of **-4.2%**. This occurred because discount codes were applied as flat sitewide percentages without taking into account individual SKU margin baselines. Capping discounts and implementing a 15% margin floor is projected to recover **+$985,000 in annual profit**."

---

### Q9: If management could only execute one recommendation next quarter, which should it be?
**Answer**:
> "I would recommend immediately implementing **Tier 1 Quick Win #1: Hard Margin Floors on Promotional Codes**.  
> This requires zero software development capital, zero additional marketing spend, and can be configured within our e-commerce checkout rules in less than 2 weeks. It immediately halts negative-margin transactions and preserves cash flow while we work on longer-term logistics and retention initiatives."

---

### Q10: How would you prioritize marketing spend between acquiring new customers vs retaining existing ones?
**Answer**:
> "Our data demonstrates that **repeat customers spend 60% more per order ($1,420 vs $890 AOV)** and carry significantly lower acquisition friction than first-time buyers. Furthermore, our RFM analysis identified **480 high-value customers who spent $3.2M historically but are currently at risk of churning**.  
> Therefore, I would reallocate 25% of top-of-funnel acquisition ad spend toward automated CRM win-back workflows and loyalty incentives for the *Potential Loyalists* and *At-Risk High Value* cohorts."
