# Multi-Page Power BI Dashboard Design Specifications

This specification document outlines the comprehensive UI/UX layout, visual component mapping, filter interactions, and page-by-page design blueprints for the **E-Commerce Sales, Customer & Profitability Analytics Platform**.

---

## Global Design System & Theme

- **Color Palette**:
  - Primary Accent (Navy / Blue): `#1F4E79` / `#2B5C8F`
  - Positive / Profit Green: `#2CA02C` / `#2E7D32`
  - Warning / Moderate Orange: `#FF7F0E` / `#E65100`
  - Negative / Alert Red: `#D62728` / `#C62828`
  - Neutral Background: `#F8F9FA`
  - Card Backgrounds: `#FFFFFF` (Drop shadow 2px, radius 6px)
  - Typography: Segoe UI (Standard Power BI enterprise font), 10pt labels, 12pt axis, 20pt KPI callouts.
- **Global Slicer Panel (Top / Collapsible Left)**:
  - **Date Hierarchy Slicer**: Year (`2022`, `2023`, `2024`, `2025`) & Month Range slider.
  - **Region Slicer**: Multi-select dropdown (`East`, `West`, `Central`, `South`).
  - **Category Slicer**: Multi-select pill buttons (`Technology`, `Furniture`, `Office Supplies`, `Apparel`).
  - **Customer Segment Slicer**: Radio button (`Consumer`, `Corporate`, `Home Office`, `All`).

---

## Page 1: Executive Overview

**Target Audience**: Chief Executive Officer (CEO), Chief Commercial Officer (CCO), VP of Sales.  
**Core Purpose**: High-level business pulse check, overall revenue, profit, margin health, and top-level variance.

### Layout Grid:
```
+---------------------------------------------------------------------------------------------------+
|  [Header: Executive Sales & Profitability Dashboard] | [Filters: Date Range | Region | Segment]   |
+---------------------------------------------------------------------------------------------------+
| [Card 1: Total Revenue]  | [Card 2: Total Profit]  | [Card 3: Margin %] | [Card 4: Total Orders]  | [Card 5: AOV]  |
|     $48.45M (+14.2% YoY) |    $7.76M (+11.8% YoY)  |       16.03%       |      36,120 Orders      |     $1,341     |
+----------------------------------------------------+----------------------------------------------+
| Visual 1: Monthly Revenue & Profit Trajectory      | Visual 2: Revenue & Margin by Category       |
| (Combo Chart: Line on secondary axis)              | (Clustered Bar Chart with data labels)       |
| - X-Axis: Order Date (Month/Year)                  | - Y-Axis: Category (Technology, Furn., etc.) |
| - Column Series: Total Revenue ($)                 | - X-Axis: Revenue ($)                        |
| - Line Series: Profit Margin (%)                   | - Tooltip: Total Profit, Profit Margin %     |
+----------------------------------------------------+----------------------------------------------+
| Visual 3: Geographic Revenue & Profit Matrix       | Visual 4: Customer Segment Contribution      |
| (Filled Map / Regional Treemap)                    | (Donut Chart with Center KPI)                |
| - Location: State / Region                         | - Values: Revenue by Customer Segment        |
| - Color Saturation: Profit Margin %                | - Legend: Consumer (52%), Corp (30%), HO(18%)|
+---------------------------------------------------------------------------------------------------+
```

---

## Page 2: Sales & Growth Dynamics

**Target Audience**: Head of Sales, Revenue Operations Managers.  
**Core Purpose**: In-depth analysis of sales acceleration, product lines, seasonality spikes, and YoY/MoM trends.

### Visual Components:
1. **YoY Revenue Growth Gauge / KPI Indicators**:
   - Visualizing `[YoY Revenue Growth %]` against internal growth target (12.0%).
2. **Decomposition Tree (Root Cause Analysis)**:
   - Root Metric: `[Total Revenue]`
   - Split Dimensions: `Category` $\rightarrow$ `Sub_Category` $\rightarrow$ `Region` $\rightarrow$ `Ship_Mode`.
3. **Monthly Seasonality Matrix (Heatmap Table)**:
   - Rows: Calendar Month (`Jan` to `Dec`)
   - Columns: Fiscal Year (`2022`, `2023`, `2024`, `2025`)
   - Values: `[Total Revenue]` with conditional color gradient highlighting Q4 surge.
4. **Top 15 Sub-Categories Waterfall Chart**:
   - Illustrating revenue build-up across sub-categories (Phones, Laptops, Chairs, Footwear, etc.).

---

## Page 3: Customer Intelligence & RFM Segmentation

**Target Audience**: VP of Marketing, CRM Lead, Customer Retention Specialists.  
**Core Purpose**: Customer lifecycle tracking, retention health, RFM cohort value, and churn risk mitigation.

### Visual Components:
1. **RFM Segment Matrix (Scatter / Bubble Chart)**:
   - X-Axis: Average Recency Days
   - Y-Axis: Average Frequency (Lifetime Orders)
   - Bubble Size: Total Segment Revenue ($)
   - Color: RFM Segment (`Champions`, `Loyal Customers`, `At-Risk High Value`, `Lost Inactive`).
2. **New vs Repeat Customer Revenue Contribution**:
   - Stacked 100% Bar Chart tracking month-over-month share of revenue derived from new acquisitions vs repeat purchasers.
3. **Top 20 High-Value VIP Customer Table**:
   - Columns: `Customer_Name`, `Customer_Segment`, `Region`, `Lifetime_Orders`, `Total_Spend`, `Total_Profit`, `Customer_Margin_%`.
4. **Customer Cohort 12-Month Retention Matrix**:
   - Matrix Visual: Acquisition Cohort Month (Rows) vs Months Since Acquisition 0–12 (Columns) formatted with heatmap rules.

---

## Page 4: Product Profitability & Discount Optimization

**Target Audience**: Chief Financial Officer (CFO), Pricing Analysts, Category Managers.  
**Core Purpose**: Diagnosing profit margin leakage, discount elasticity, and identifying unprofitable SKUs.

### Visual Components:
1. **Product Profitability 4-Quadrant Scatter Plot**:
   - X-Axis: `[Total Revenue]` (Log scale or Linear)
   - Y-Axis: `[Profit Margin %]`
   - Quadrant Reference Lines: Median Revenue & 15% Profit Margin Target.
   - **Quadrant 1 (Top-Right)**: High Revenue + High Margin (Core Drivers - Nurture).
   - **Quadrant 2 (Top-Left)**: Low Revenue + High Margin (Niche Growth Opportunities).
   - **Quadrant 3 (Bottom-Right)**: High Revenue + Low Margin (High Risk / Excessive Discounts - Urgent Fix).
   - **Quadrant 4 (Bottom-Left)**: Low Revenue + Low Margin (Candidates for Review / Delisting).
2. **Discount Bracket Margin Erosion Bar Chart**:
   - Categories: `None (0%)`, `Low (1-15%)`, `Medium (16-30%)`, `High (31%+)`
   - Metric: `[Profit Margin %]` displaying dramatic margin decline at >20% discounts.
3. **Bottom 15 Loss-Making Products Table**:
   - Table with conditional red text formatting on negative profit, highlighting average discount rates.

---

## Page 5: Regional Operations & Logistics Efficiency

**Target Audience**: Chief Operating Officer (COO), Supply Chain Director, Logistics Managers.  
**Core Purpose**: Fulfillment speed, shipping tier economics, regional logistics cost ratio, and return rates.

### Visual Components:
1. **Shipping Mode Economics Table**:
   - Columns: `Ship_Mode`, `Total_Orders`, `Total_Revenue`, `Avg_Shipping_Cost`, `Avg_Delivery_Days`, `Return_Rate_%`, `Net_Profit_Margin_%`.
2. **Regional Shipping Cost-to-Revenue Ratio Bar Chart**:
   - Identifying geographic zones with disproportionately high logistics costs eating into gross margins.
3. **Return Rate by Sub-Category Bar Chart**:
   - Highlighting categories with high return rates (e.g. Apparel, Footwear, Furniture).
4. **Geographic State-by-State Drilldown Map**:
   - Visualizing total sales volume and profitability across US states.
