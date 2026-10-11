# Data Quality & Audit Report

## 1. Executive Summary

- **Total Raw Records Ingested**: 65,975
- **Exact Duplicate Rows**: 975 (1.48%)
- **Invalid Date Records**: 15
- **Numerical Value Anomalies**: 20
- **Columns with Missing Data**: 4

## 2. Missing Value Analysis

| Column | Missing Records | Missing Percentage (%) |
| :--- | :--- | :--- |
| `Customer_Name` | 352 | 0.53% |
| `Customer_Age` | 1,601 | 2.43% |
| `Payment_Method` | 971 | 1.47% |
| `Rating` | 1,341 | 2.03% |

## 3. Data Cleaning Audit Trail (Problem → Decision → Reason)

### Decision #1
- **Problem**: Detected 975 exact duplicate rows (1.48% of dataset) caused by repeated batch uploads.
- **Decision**: Deduplicate records keeping the first occurrence.
- **Reason**: Prevents artificial inflation of total order volume, sales revenue, and customer counts in executive reporting.

### Decision #2
- **Problem**: Identified 15 records with unparseable or out-of-bounds order dates (e.g. leap day anomalies).
- **Decision**: Filter out corrupted date records where business timestamp cannot be reconstructed.
- **Reason**: Time-series integrity is critical for accurate MoM, YoY, and cohort retention calculations.

### Decision #3
- **Problem**: Found 12 records with non-positive quantities (<= 0) and 8 invalid discounts (> 100%).
- **Decision**: Exclude corrupted transaction line items from analysis tables and log them in the audit exception trail.
- **Reason**: Negative quantities without return codes distort unit pricing and AOV; discounts > 1.0 represent telemetry ingestion errors.

### Decision #4
- **Problem**: Missing values detected in Customer_Age (2.5%), Rating (2.0%), and Payment_Method (1.5%).
- **Decision**: Impute Customer_Age using segment-specific median; impute missing categorical fields with 'Unknown' category.
- **Reason**: Preserves valuable transactional and revenue data without introducing arbitrary demographic bias.

### Decision #5
- **Problem**: Inconsistent casing and whitespace padding across Category and Customer_Segment columns.
- **Decision**: Apply `.str.strip().str.title()` standard transformations across all categorical dimensions.
- **Reason**: Ensures accurate grouping, aggregation, and relational joins in SQL and Power BI without duplicate category buckets.

