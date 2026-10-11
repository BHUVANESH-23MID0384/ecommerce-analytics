# Power BI Star Schema Data Model Architecture

This document defines the relational data modeling architecture implemented in Power BI for the **E-Commerce Sales, Customer & Profitability Analytics Platform**.

---

## 1. Data Model Topology: Star Schema

The data model is engineered as a pure **Star Schema**, ensuring optimal VertiPaq engine compression, sub-second query evaluation, and unambiguous filter context propagation.

```
       +---------------------------------------------+
       |                  dim_date                   |
       |---------------------------------------------|
       | PK: date_key (YYYY-MM-DD)                   |
       |     full_date, year, quarter, month, etc.   |
       +---------------------------------------------+
                              | 1
                              |
                              | * (Single Direction)
       +---------------------------------------------+
       |                 fact_sales                  |
       |---------------------------------------------|
       | PK: order_item_id                           |
       | FK: order_date ----------> dim_date         |
       | FK: customer_id ---------> dim_customer     |
       | FK: product_id ----------> dim_product      |
       | FK: location_id ---------> dim_location     |
       |     quantity, unit_price, discount_rate     |
       |     net_sales, cost_amount, profit          |
       |     shipping_cost, return_flag, rating      |
       +---------------------------------------------+
          /                  |                  \
       * / 1              *  | 1              *  \ 1
+--------------------+  +--------------------+  +--------------------+
|    dim_customer    |  |    dim_product     |  |    dim_location    |
|--------------------|  |--------------------|  |--------------------|
| PK: customer_id    |  | PK: product_id     |  | PK: location_id    |
|     customer_name  |  |     product_name   |  |     city, state    |
|     segment        |  |     category       |  |     country        |
|     gender, age    |  |     sub_category   |  |     region         |
+--------------------+  |     brand, price   |  +--------------------+
          | 1           +--------------------+
          |
          | 1 (Optional 1:1 Bridge)
+--------------------+
| rfm_customer_seg   |
|--------------------|
| PK: customer_id    |
|     recency_days   |
|     frequency      |
|     monetary       |
|     rfm_segment    |
+--------------------+
```

---

## 2. Table Relationships & Cardinality

| From Table (Dimension) | Primary Key | To Table (Fact) | Foreign Key | Cardinality | Cross Filter Direction | Security Filtering |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dim_date` | `date_key` | `fact_sales` | `order_date` | `1 : Many (*)` | Single (`dim_date` $\rightarrow$ `fact_sales`) | None |
| `dim_customer` | `customer_id` | `fact_sales` | `customer_id` | `1 : Many (*)` | Single (`dim_customer` $\rightarrow$ `fact_sales`) | None |
| `dim_product` | `product_id` | `fact_sales` | `product_id` | `1 : Many (*)` | Single (`dim_product` $\rightarrow$ `fact_sales`) | None |
| `dim_location` | `location_id` | `fact_sales` | `location_id` | `1 : Many (*)` | Single (`dim_location` $\rightarrow$ `fact_sales`) | None |
| `dim_customer` | `customer_id` | `rfm_customer_segments` | `customer_id` | `1 : 1` | Both / Single | None |

---

## 3. VertiPaq Storage & Modeling Best Practices

1. **Surrogate Keys vs High-Cardinality Strings**:
   - Dates are formatted as ISO strings (`YYYY-MM-DD`) or Integer keys (`YYYYMMDD`) to minimize dictionary encoding size.
   - Text fields in `dim_product` and `dim_customer` have clean string boundaries with no leading/trailing whitespace.
2. **Mark as Date Table**:
   - In Power BI Desktop, navigate to `dim_date`, right-click $\rightarrow$ **Mark as Date Table**, and select `full_date` as the primary unique date column.
   - This disables Power BI's automatic hidden auto-date/time hierarchies, drastically reducing `.pbix` file size and enabling performant time-intelligence DAX functions (`SAMEPERIODLASTYEAR`, `DATESYTD`, `DATEADD`).
3. **Cross-Filtering Discipline**:
   - All relationships are strictly set to **Single** direction filtering from Dimension to Fact.
   - Bi-directional cross-filtering is avoided on core tables to eliminate ambiguous query paths and maintain lightning-fast DAX execution.
4. **Hiding Foreign Key Columns**:
   - Hide all foreign keys in `fact_sales` (`customer_id`, `product_id`, `location_id`, `order_date`) from report view. Direct report consumers to slice strictly through dimension tables to preserve star-schema integrity.
