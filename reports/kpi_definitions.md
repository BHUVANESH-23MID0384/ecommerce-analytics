# Business KPI Definitions & Calculation Rules

This document establishes the official enterprise business metrics, mathematical definitions, SQL implementations, and DAX calculations used across the **E-Commerce Sales, Customer & Profitability Analytics Platform**.

---

## 1. Core Financial & Volume KPIs

### 1.1 Net Sales (Revenue)
- **Business Meaning**: The net dollar inflow generated from customer orders after subtracting applied discounts.
- **Mathematical Formula**:
  $$\text{Net Sales} = \sum (\text{Quantity} \times \text{Unit Price} \times (1 - \text{Discount Rate}))$$
- **SQL Implementation**:
  ```sql
  SUM(net_sales)
  ```
- **DAX Formula**:
  ```dax
  [Total Revenue] = SUM(fact_sales[net_sales])
  ```

---

### 1.2 Gross Profit
- **Business Meaning**: The total dollar earnings remaining after deducting the Cost of Goods Sold (COGS) from Net Sales.
- **Mathematical Formula**:
  $$\text{Gross Profit} = \text{Net Sales} - \text{Cost of Goods Sold}$$
- **SQL Implementation**:
  ```sql
  SUM(profit) -- where profit = net_sales - cost_amount
  ```
- **DAX Formula**:
  ```dax
  [Total Profit] = SUM(fact_sales[profit])
  ```

---

### 1.3 Gross Profit Margin (%)
- **Business Meaning**: The percentage of revenue converted into gross profit. Indicates pricing power, manufacturing efficiency, and discount discipline.
- **Mathematical Formula**:
  $$\text{Profit Margin \%} = \left( \frac{\text{Total Profit}}{\text{Total Net Sales}} \right) \times 100$$
- **SQL Implementation**:
  ```sql
  ROUND((SUM(profit) / NULLIF(SUM(net_sales), 0)) * 100, 2)
  ```
- **DAX Formula**:
  ```dax
  [Profit Margin %] = DIVIDE([Total Profit], [Total Revenue], 0.0)
  ```

---

### 1.4 Average Order Value (AOV)
- **Business Meaning**: The average net revenue captured across distinct order transactions.
- **Mathematical Formula**:
  $$\text{AOV} = \frac{\text{Total Net Revenue}}{\text{Distinct Order Count}}$$
- **SQL Implementation**:
  ```sql
  ROUND(SUM(net_sales) / COUNT(DISTINCT order_id), 2)
  ```
- **DAX Formula**:
  ```dax
  [Average Order Value] = DIVIDE([Total Revenue], [Total Orders], 0.0)
  ```

---

## 2. Customer Analytics & Retention KPIs

### 2.1 Repeat Customer Rate (%)
- **Business Meaning**: The proportion of unique customers who have completed more than 1 distinct order within the observation window.
- **Mathematical Formula**:
  $$\text{Repeat Customer Rate \%} = \left( \frac{\text{Customers with Orders} > 1}{\text{Total Unique Customers}} \right) \times 100$$
- **SQL Implementation**:
  ```sql
  WITH customer_orders AS (
      SELECT customer_id, COUNT(DISTINCT order_id) AS total_orders
      FROM fact_sales
      GROUP BY customer_id
  )
  SELECT 
      ROUND((COUNT(CASE WHEN total_orders > 1 THEN 1 END) * 100.0 / COUNT(*)), 2) AS repeat_rate_pct
  FROM customer_orders;
  ```
- **DAX Formula**:
  ```dax
  [Repeat Customer Rate %] = 
  VAR _RepeatCust = COUNTROWS(FILTER(VALUES(fact_sales[customer_id]), CALCULATE(DISTINCTCOUNT(fact_sales[order_id])) > 1))
  RETURN DIVIDE(_RepeatCust, [Total Customers], 0.0)
  ```

---

### 2.2 Historical Customer Lifetime Value (CLV)
- **Business Meaning**: The cumulative historical revenue generated per unique acquired customer.
- **Mathematical Formula**:
  $$\text{Historical CLV} = \frac{\text{Total Lifetime Revenue}}{\text{Total Customer Count}}$$
- **SQL Implementation**:
  ```sql
  ROUND(SUM(net_sales) / COUNT(DISTINCT customer_id), 2)
  ```
- **DAX Formula**:
  ```dax
  [Customer Lifetime Spend] = DIVIDE([Total Revenue], [Total Customers], 0.0)
  ```

---

### 2.3 Cohort Retention Rate (%)
- **Business Meaning**: The percentage of customers acquired in a specific month ($M_0$) who return to make at least one purchase in a subsequent elapsed month ($M_n$).
- **Mathematical Formula**:
  $$\text{Retention Rate}(M_n) = \left( \frac{\text{Active Customers in } M_n \text{ from Cohort } M_0}{\text{Total Initial Customers in Cohort } M_0} \right) \times 100$$

---

## 3. Operational, Logistics & Pricing KPIs

### 3.1 Return Rate (%)
- **Business Meaning**: The percentage of purchased line items that are returned by customers.
- **Mathematical Formula**:
  $$\text{Return Rate \%} = \left( \frac{\text{Returned Line Items (Return\_Flag = 1)}}{\text{Total Line Items}} \right) \times 100$$
- **SQL Implementation**:
  ```sql
  ROUND((SUM(return_flag) * 100.0 / COUNT(*)), 2)
  ```
- **DAX Formula**:
  ```dax
  [Return Rate %] = 
  DIVIDE(
      CALCULATE(COUNTROWS(fact_sales), fact_sales[return_flag] = 1),
      COUNTROWS(fact_sales),
      0.0
  )
  ```

---

### 3.2 Shipping Cost to Revenue Ratio (%)
- **Business Meaning**: The proportion of gross merchandise revenue consumed by logistics and fulfillment expenses.
- **Mathematical Formula**:
  $$\text{Shipping Cost Ratio \%} = \left( \frac{\text{Total Incurred Shipping Cost}}{\text{Total Net Revenue}} \right) \times 100$$
- **DAX Formula**:
  ```dax
  [Shipping to Revenue %] = DIVIDE(SUM(fact_sales[shipping_cost]), [Total Revenue], 0.0)
  ```

---

### 3.3 Average Delivery Duration (Days)
- **Business Meaning**: The average elapsed calendar days from customer order placement to warehouse dispatch / delivery confirmation.
- **Mathematical Formula**:
  $$\text{Average Delivery Days} = \text{Average}(\text{Ship Date} - \text{Order Date})$$
- **SQL Implementation**:
  ```sql
  ROUND(AVG(shipping_duration_days), 1)
  ```
- **DAX Formula**:
  ```dax
  [Average Delivery Days] = AVERAGE(fact_sales[shipping_duration_days])
  ```
