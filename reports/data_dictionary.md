# E-Commerce Data Dictionary & Metadata Reference

This data dictionary documents the complete schema for both raw transactional ingestion feeds and the transformed Star Schema relational database.

---

## 1. Raw Transactional Data Dictionary (`data/raw/ecommerce_raw_transactions.csv`)

| Column Name | Data Type | Nullable | Description | Example Values |
| :--- | :--- | :--- | :--- | :--- |
| `Order_ID` | String | No | Unique business identifier for customer order | `ORD-100001`, `ORD-100045` |
| `Order_Date` | Date (String) | No | Date on which the customer submitted the order | `2023-11-14` |
| `Ship_Date` | Date (String) | No | Date on which the order was dispatched from fulfillment center | `2023-11-17` |
| `Ship_Mode` | String | No | Delivery service level chosen by customer | `Standard Class`, `First Class`, `Same Day` |
| `Customer_ID` | String | No | Unique business identifier for the customer | `CUST-10482` |
| `Customer_Name` | String | Yes (Imputed) | Full name of the purchasing customer | `Robert Miller`, `Sarah Davis` |
| `Customer_Segment` | String | No | Customer account classification tier | `Consumer`, `Corporate`, `Home Office` |
| `Customer_City` | String | No | Destination delivery city | `New York`, `Chicago`, `San Francisco` |
| `Customer_State` | String | No | Destination delivery state | `California`, `New York`, `Texas` |
| `Customer_Country` | String | No | Destination country | `United States` |
| `Region` | String | No | Macro geographic territory | `East`, `West`, `Central`, `South` |
| `Customer_Age` | Integer | Yes (Imputed) | Age of the customer in years | `34`, `52`, `28` |
| `Customer_Gender` | String | No | Customer gender code | `M`, `F` |
| `Product_ID` | String | No | Unique SKU identifier | `PROD-TEC-1012`, `PROD-FUR-1140` |
| `Product_Name` | String | No | Marketing name of the product line item | `Apple Phones Model M40` |
| `Category` | String | No | High-level merchandise category | `Technology`, `Furniture`, `Office Supplies`, `Apparel` |
| `Sub_Category` | String | No | Detailed merchandise sub-division | `Phones`, `Chairs`, `Binders`, `Footwear` |
| `Brand` | String | No | Manufacturer brand name | `Apple`, `Logitech`, `Herman Miller`, `Nike` |
| `Quantity` | Integer | No | Number of product units ordered in line item | `1`, `2`, `5`, `8` |
| `Unit_Price` | Float | No | Standard list retail price per single unit ($) | `849.99`, `45.00` |
| `Discount` | Float | No | Percentage discount rate applied ($0.00 - 0.50$) | `0.00`, `0.15`, `0.30` |
| `Sales` | Float | No | Realized gross transaction revenue after discount ($) | `1444.98`, `76.50` |
| `Cost` | Float | No | Total COGS (Cost of Goods Sold) for line item ($) | `1120.00`, `42.00` |
| `Profit` | Float | No | Net profit generated ($Sales - Cost$) | `324.98`, `34.50` |
| `Shipping_Cost` | Float | No | Fulfillment shipping cost incurred ($) | `14.20`, `4.80` |
| `Payment_Method` | String | Yes (Imputed) | Payment instrument used for settlement | `Credit Card`, `PayPal`, `Debit Card` |
| `Return_Flag` | Integer | No | Flag indicating if item was returned (1 = Yes, 0 = No) | `0`, `1` |
| `Rating` | Integer | Yes (Imputed) | Post-purchase customer review rating (1 to 5 stars) | `5`, `4`, `1` |

---

## 2. Processed Star Schema Data Dictionary

### Table: `dim_customer`
| Field Name | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `customer_id` | VARCHAR(50) | Primary Key | Unique customer ID |
| `customer_name` | VARCHAR(150) | Standard | Standardized customer name |
| `customer_segment` | VARCHAR(50) | Standard | Standardized customer segment (`Consumer`, `Corporate`, `Home Office`) |
| `gender` | VARCHAR(10) | Standard | Customer gender (`M`, `F`) |
| `age` | INTEGER | Standard | Imputed integer age |

### Table: `dim_product`
| Field Name | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `product_id` | VARCHAR(50) | Primary Key | Unique product SKU ID |
| `product_name` | VARCHAR(255) | Standard | Standardized product title |
| `category` | VARCHAR(100) | Standard | Product macro category |
| `sub_category` | VARCHAR(100) | Standard | Product sub-category |
| `brand` | VARCHAR(100) | Standard | Manufacturer brand name |
| `standard_retail_price` | NUMERIC(10,2)| Standard | Catalog standard unit price |

### Table: `dim_location`
| Field Name | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `location_id` | VARCHAR(50) | Primary Key | Synthetic surrogate key (`LOC-1001`) |
| `city` | VARCHAR(100) | Standard | City name |
| `state` | VARCHAR(100) | Standard | US state name |
| `country` | VARCHAR(100) | Standard | Country name |
| `region` | VARCHAR(50) | Standard | Geographic macro region |

### Table: `dim_date`
| Field Name | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `date_key` | VARCHAR(10) | Primary Key | ISO Date key (`YYYY-MM-DD`) |
| `full_date` | DATE | Standard | Calendar date object |
| `year` | INTEGER | Standard | Calendar year (`2022`, `2023`, `2024`, `2025`) |
| `quarter` | INTEGER | Standard | Quarter number (`1`, `2`, `3`, `4`) |
| `quarter_name` | VARCHAR(10) | Standard | Formatted quarter (`Q1`, `Q2`, `Q3`, `Q4`) |
| `month` | INTEGER | Standard | Month number ($1 - 12$) |
| `month_name` | VARCHAR(20) | Standard | Month name (`January` to `December`) |
| `week_of_year` | INTEGER | Standard | ISO week number ($1 - 53$) |
| `day_of_month` | INTEGER | Standard | Calendar day ($1 - 31$) |
| `day_name` | VARCHAR(20) | Standard | Day of week (`Monday` to `Sunday`) |
| `is_weekend` | INTEGER | Standard | Weekend indicator ($1 = \text{Sat/Sun}, 0 = \text{Weekday}$) |

### Table: `fact_sales`
| Field Name | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `order_id` | VARCHAR(50) | Degenerate | Business order ID grouping multiple line items |
| `order_item_id` | VARCHAR(50) | Primary Key | Unique line item surrogate key |
| `order_date` | VARCHAR(10) | Foreign Key | References `dim_date(date_key)` |
| `ship_date` | VARCHAR(10) | Foreign Key | References `dim_date(date_key)` |
| `customer_id` | VARCHAR(50) | Foreign Key | References `dim_customer(customer_id)` |
| `product_id` | VARCHAR(50) | Foreign Key | References `dim_product(product_id)` |
| `location_id` | VARCHAR(50) | Foreign Key | References `dim_location(location_id)` |
| `ship_mode` | VARCHAR(50) | Standard | Delivery service tier |
| `payment_method` | VARCHAR(50) | Standard | Payment instrument |
| `quantity` | INTEGER | Metric | Number of units purchased |
| `unit_price` | NUMERIC(10,2)| Metric | Base unit price ($) |
| `discount_rate` | NUMERIC(5,4)| Metric | Applied discount fraction ($0.0 - 0.50$) |
| `gross_sales` | NUMERIC(12,2)| Metric | List price volume before discounts ($Quantity \times UnitPrice$) |
| `net_sales` | NUMERIC(12,2)| Metric | Net realized revenue ($GrossSales \times (1 - Discount)$) |
| `cost_amount` | NUMERIC(12,2)| Metric | Total cost of goods sold ($COGS$) |
| `profit` | NUMERIC(12,2)| Metric | Realized net profit ($NetSales - Cost$) |
| `profit_margin_pct` | NUMERIC(6,2)| Metric | Gross margin percentage ($\frac{Profit}{NetSales} \times 100$) |
| `shipping_cost` | NUMERIC(10,2)| Metric | Fulfillment shipping charge |
| `shipping_duration_days` | INTEGER | Metric | Elapsed fulfillment duration in days |
| `discount_bracket` | VARCHAR(50) | Standard | Discount tier (`None (0%)`, `Low`, `Medium`, `High`) |
| `return_flag` | INTEGER | Flag | Product return flag ($1 = \text{Returned}, 0 = \text{Kept}$) |
| `rating` | INTEGER | Metric | Customer satisfaction rating ($1 - 5$) |
| `is_profitable` | INTEGER | Flag | Binary profit flag ($1 = \text{Profit} > 0, 0 = \text{Loss}$) |

### Table: `rfm_customer_segments`
| Field Name | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `customer_id` | VARCHAR(50) | Primary Key / FK | References `dim_customer(customer_id)` |
| `recency_days` | INTEGER | Metric | Days since customer's most recent order |
| `frequency` | INTEGER | Metric | Total distinct orders placed over lifetime |
| `monetary` | NUMERIC(12,2)| Metric | Total cumulative lifetime net spend ($) |
| `total_profit` | NUMERIC(12,2)| Metric | Total cumulative profit generated ($) |
| `avg_order_value` | NUMERIC(10,2)| Metric | Historical average order spend |
| `r_score` | INTEGER | Score ($1-5$) | Recency quintile score ($5 = \text{Most recent}$) |
| `f_score` | INTEGER | Score ($1-5$) | Frequency quintile score ($5 = \text{Most frequent}$) |
| `m_score` | INTEGER | Score ($1-5$) | Monetary spend quintile score ($5 = \text{Highest spend}$) |
| `rfm_composite` | VARCHAR(10) | Code | Three-digit composite code (e.g. `555`, `111`) |
| `rfm_score_avg` | NUMERIC(4,2)| Score ($1.0-5.0$) | Unweighted average of R, F, and M scores |
| `customer_segment_rfm` | VARCHAR(50)| Categorical | Assigned segment (`Champions`, `Loyal`, `At-Risk`, etc.) |
