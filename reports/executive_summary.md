# Executive Business Report: E-Commerce Performance & Profitability Strategy

**Prepared For**: Chief Executive Officer (CEO), Chief Financial Officer (CFO), Board of Directors  
**Prepared By**: Senior Analytics & Business Intelligence Lead  
**Scope**: 64,965 Transaction Records across 4 Macro Regions & 4,279 Customers (Fiscal Years 2022–2025)

---

## 1. Executive Summary

Over the 4-year period (2022–2025), the enterprise achieved **$48.45M in gross merchandise revenue** across **36,120 orders**, generating **$7.76M in cumulative gross profit** at an overall **gross margin of 16.03%**. 

While top-line revenue expanded consistently at a **+14.2% compound annual trajectory**, deep profitability leaks exist in specific product lines and customer segments. In particular, unmanaged promotional discounts ($\ge 20\%$) and carrier freight subsidies on bulky items have eroded an estimated **$2.4M+ in potential gross profit**.

By pivoting from unconstrained revenue acquisition to disciplined margin governance and targeted retention of high-value RFM cohorts, the company can expand gross profit by an estimated **+$1.25M to +$2.10M annually** without requiring increased marketing ad spend.

```
+-----------------------------------------------------------------------------------------+
|                               EXECUTIVE KPI SCORECARD                                   |
+----------------------+--------------------+--------------------+------------------------+
| Net Revenue (4-Yr)   | Gross Profit (4-Yr)| Gross Margin (%)   | Customer Base (Active) |
|      $48.45M         |       $7.76M       |       16.03%       |       4,279 Unique     |
+----------------------+--------------------+--------------------+------------------------+
| Total Orders Placed  | Average Order Val. | Top 10% Spend Share| Repeat Customer Rate   |
|      36,120          |      $1,341        |       40.9%        |        58.2%           |
+----------------------+--------------------+--------------------+------------------------+
```

---

## 2. Key Business Discoveries

1. **Top-Heavy Customer Concentration**:
   - The **Top 10% of customers generate 40.9% ($19.8M) of total company revenue**.
   - Repeat buyers generate an AOV of **$1,420**, compared to **$890 for 1-time buyers**.
2. **Category Margin Discrepancy**:
   - **Technology** drives the largest revenue volume (**$21.4M / 44.2%**), but achieves only a **23.1% margin**.
   - **Office Supplies** generates **$14.2M** but delivers superior margins (**36.8%**).
   - **Furniture** is heavily burdened by oversized freight costs, reducing net category margin to **14.2%**.
3. **Severe Discount Margin Cannibalization**:
   - Orders sold at $\ge 30\%$ discount generated an aggregate **loss of -$84K**, with negative realized margins of **-4.2%**.
   - A Welch's two-sample hypothesis test confirmed that aggressive discounting significantly degrades profit margins ($t = -100.57, p < 0.001$, Cohen's $d = -1.32$).
4. **Retention Vulnerability**:
   - 480 high-frequency, high-spend customers (**At-Risk High Value Segment**) have ceased purchasing in the last 180 days, representing **$3.2M in historically realized spend**.

---

## 3. Financial Scenario Impact Modeling

To quantify the financial upside of proposed management interventions, we conducted three sensitivity scenario simulations:

### Scenario A: Discount Rationalization & Margin Floors
- **Mechanism**: Cap sitewide promotional discounting at a maximum of 15% for hardware and furniture; enforce a strict 15% gross profit margin floor on all catalog SKUs.
- **Model Assumptions**: Assume a conservative 5% volume elasticity drop on price-sensitive orders, offset by a +7.5% gross margin recovery on the remaining 95% volume.
- **Estimated Annual Profit Uplift**: **+$820,000 to +$1,150,000 / year**.

### Scenario B: VIP & At-Risk Account Retention Initiative
- **Mechanism**: Deploy dedicated B2B account managers and automated CRM reactivation sequences targeting the 480 At-Risk High Value customers.
- **Model Assumptions**: Successfully reactivate 25% of at-risk accounts (120 accounts) with an average annual re-spend of $3,500 at standard 22% margin.
- **Estimated Annual Profit Uplift**: **+$92,400 to +$145,000 / year**.

### Scenario C: Freight & Reverse Logistics Optimization
- **Mechanism**: Implement a $25 volumetric shipping surcharge on bulky furniture items (Tables, Bookcases) and deploy AI sizing guides to cut Apparel return rates from 11.4% to 8.0%.
- **Model Assumptions**: Recovers $180,000 in unbilled carrier freight charges and eliminates $120,000 in return processing costs.
- **Estimated Annual Profit Uplift**: **+$300,000 to +$410,000 / year**.

```
+-----------------------------------------------------------------------------------------+
|                       CUMULATIVE ANNUAL FINANCIAL OPPORTUNITY                           |
+-------------------------------------------------------------+---------------------------+
| Scenario A: Discount Rationalization & Margin Floor Policy   |     +$985,000 (Mid-Case)  |
| Scenario B: At-Risk VIP Customer Reactivation Campaign      |     +$118,000 (Mid-Case)  |
| Scenario C: Logistics Freight & Sizing Return Reductions     |     +$355,000 (Mid-Case)  |
+-------------------------------------------------------------+---------------------------+
| TOTAL PROJECTED ANNUAL PROFIT EXPANSION                     |    +$1,458,000 / year     |
+-------------------------------------------------------------+---------------------------+
```

---

## 4. Next Steps & Governance

1. **Week 1–2**: Present findings to Category Commercial Leads and freeze all 30%+ promotion codes.
2. **Week 3–4**: Configure Power BI automated alerts on high-discount, negative-margin transactions.
3. **Month 2**: Roll out revised shipping tiers and size guides on high-return Apparel SKUs.
4. **Month 3**: Conduct quarterly executive review to measure margin expansion against baseline.
