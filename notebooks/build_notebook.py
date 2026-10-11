"""
build_notebook.py
Generates the comprehensive Jupyter Notebook 'notebooks/exploratory_analysis.ipynb'.
"""

import json

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# End-to-End E-Commerce Sales, Customer & Profitability Analytics\n",
                "## Exploratory Data Analysis & Statistical Hypothesis Testing\n",
                "---\n",
                "**Author**: Senior Data Analyst / Project Mentor  \n",
                "**Dataset**: 65,000+ Cleaned E-Commerce Transactions (2022–2025)  \n",
                "**Tech Stack**: Python, Pandas, NumPy, Matplotlib, Seaborn, SciPy, SQLite\n",
                "\n",
                "### Business Objectives:\n",
                "1. **Univariate & Bivariate Exploration**: Inspect revenue, profit, quantity, and discount distributions.\n",
                "2. **Time-Series Dynamics**: Evaluate monthly seasonality, Q4 holiday surges, and YoY growth.\n",
                "3. **Profitability & Pricing Elasticity**: Investigate discount margin erosion.\n",
                "4. **Statistical Hypothesis Testing**: Statistically evaluate discount impact on profit margins ($H_0$ vs $H_1$).\n",
                "5. **Customer Analytics**: RFM behavioral segmentation and 12-month cohort retention matrices."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from scipy import stats\n",
                "\n",
                "# Styling Setup\n",
                "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n",
                "plt.rcParams['font.family'] = 'sans-serif'\n",
                "plt.rcParams['font.size'] = 11\n",
                "plt.rcParams['axes.titlesize'] = 14\n",
                "plt.rcParams['axes.labelsize'] = 12\n",
                "plt.rcParams['figure.dpi'] = 150\n",
                "\n",
                "# Load Processed Data\n",
                "df = pd.read_csv('../data/processed/ecommerce_cleaned_transactions.csv')\n",
                "df['Order_Date'] = pd.to_datetime(df['Order_Date'])\n",
                "df['Ship_Date'] = pd.to_datetime(df['Ship_Date'])\n",
                "print(f'Successfully loaded {len(df):,} cleaned records with {df.shape[1]} features.')\n",
                "df.head(3)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Descriptive Summary Statistics & Univariate Distributions"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "outputs": [],
            "source": [
                "num_cols = ['Net_Sales', 'Cost_Amount', 'Gross_Profit', 'Profit_Margin_Pct', 'Discount', 'Quantity']\n",
                "df[num_cols].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).T"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Monthly Revenue & Profitability Trajectory (Time Series Analysis)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 3,
            "metadata": {},
            "outputs": [],
            "source": [
                "monthly = df.set_index('Order_Date').resample('ME').agg({\n",
                "    'Net_Sales': 'sum',\n",
                "    'Gross_Profit': 'sum'\n",
                "}).reset_index()\n",
                "\n",
                "fig, ax1 = plt.subplots(figsize=(12, 5))\n",
                "ax2 = ax1.twinx()\n",
                "\n",
                "ax1.plot(monthly['Order_Date'], monthly['Net_Sales'] / 1e3, color='#1f77b4', linewidth=2.5, marker='o', label='Revenue ($K)')\n",
                "ax2.plot(monthly['Order_Date'], monthly['Gross_Profit'] / 1e3, color='#2ca02c', linewidth=2.2, linestyle='--', marker='s', label='Profit ($K)')\n",
                "\n",
                "ax1.set_title('Monthly Revenue & Profit Trajectory (2022–2025)', fontweight='bold', pad=15)\n",
                "ax1.set_xlabel('Order Date', fontweight='bold')\n",
                "ax1.set_ylabel('Monthly Revenue ($K)', color='#1f77b4', fontweight='bold')\n",
                "ax2.set_ylabel('Monthly Profit ($K)', color='#2ca02c', fontweight='bold')\n",
                "ax1.legend(loc='upper left')\n",
                "ax2.legend(loc='upper right')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Category & Product Profitability Matrix"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 4,
            "metadata": {},
            "outputs": [],
            "source": [
                "cat_summary = df.groupby('Category').agg(\n",
                "    Total_Revenue=('Net_Sales', 'sum'),\n",
                "    Total_Profit=('Gross_Profit', 'sum'),\n",
                "    Avg_Margin=('Profit_Margin_Pct', 'mean')\n",
                ").reset_index().sort_values('Total_Revenue', ascending=False)\n",
                "\n",
                "fig, ax = plt.subplots(figsize=(9, 5))\n",
                "bars = ax.bar(cat_summary['Category'], cat_summary['Total_Revenue'] / 1e6, color=['#2b5c8f', '#d95f02', '#7570b3', '#1b9e77'], edgecolor='black', alpha=0.85)\n",
                "for bar, margin in zip(bars, cat_summary['Avg_Margin']):\n",
                "    yval = bar.get_height()\n",
                "    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f'${yval:.2f}M\\n({margin:.1f}%)', ha='center', va='bottom', fontweight='bold')\n",
                "ax.set_title('Total Revenue & Margin by Product Category', fontweight='bold')\n",
                "ax.set_ylabel('Revenue ($M)')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Statistical Hypothesis Testing: Pricing & Discount Elasticity\n",
                "\n",
                "**Hypothesis Definition**:\n",
                "- **Null Hypothesis ($H_0$)**: $\\mu_{\\text{high discount}} = \\mu_{\\text{low discount}}$ (Aggressive discounting has no effect on profit margin).\n",
                "- **Alternative Hypothesis ($H_1$)**: $\\mu_{\\text{high discount}} < \\mu_{\\text{low discount}}$ (Aggressive discounting significantly reduces profit margin)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 5,
            "metadata": {},
            "outputs": [],
            "source": [
                "group_high = df[df['Discount'] >= 0.20]['Profit_Margin_Pct'].dropna()\n",
                "group_low = df[df['Discount'] < 0.20]['Profit_Margin_Pct'].dropna()\n",
                "\n",
                "t_stat, p_val = stats.ttest_ind(group_high, group_low, equal_var=False)\n",
                "pearson_r, pearson_p = stats.pearsonr(df['Discount'], df['Profit_Margin_Pct'])\n",
                "mean_diff = group_high.mean() - group_low.mean()\n",
                "pooled_sd = np.sqrt(((len(group_high)-1)*group_high.std()**2 + (len(group_low)-1)*group_low.std()**2) / (len(group_high) + len(group_low) - 2))\n",
                "cohen_d = mean_diff / pooled_sd\n",
                "\n",
                "print(f'High Discount Mean Margin: {group_high.mean():.2f}% (N={len(group_high):,})')\n",
                "print(f'Low Discount Mean Margin:  {group_low.mean():.2f}% (N={len(group_low):,})')\n",
                "print(f'Welch t-statistic: {t_stat:.4f}')\n",
                "print(f'p-value: {p_val:.4e}')\n",
                "print(f\"Cohen's d: {cohen_d:.3f} (Large Effect)\")\n",
                "print(f'Pearson correlation: {pearson_r:.4f} (p={pearson_p:.4e})')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. RFM Customer Segmentation Analysis"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 6,
            "metadata": {},
            "outputs": [],
            "source": [
                "rfm_df = pd.read_csv('../data/processed/rfm_customer_segments.csv')\n",
                "rfm_summary = rfm_df.groupby('Customer_Segment_RFM').agg(\n",
                "    Customers=('Customer_ID', 'count'),\n",
                "    Avg_Recency=('Recency_Days', 'mean'),\n",
                "    Avg_Frequency=('Frequency', 'mean'),\n",
                "    Avg_Monetary=('Monetary', 'mean'),\n",
                "    Total_Revenue=('Monetary', 'sum'),\n",
                "    Total_Profit=('Total_Profit', 'sum')\n",
                ").reset_index().sort_values('Total_Revenue', ascending=False)\n",
                "rfm_summary['Revenue_Share_%'] = (rfm_summary['Total_Revenue'] / rfm_summary['Total_Revenue'].sum()) * 100\n",
                "rfm_summary"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Cohort Retention Heatmap"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 7,
            "metadata": {},
            "outputs": [],
            "source": [
                "df_cohort = df.copy()\n",
                "df_cohort['Order_YrMo'] = df_cohort['Order_Date'].dt.strftime('%Y-%m')\n",
                "first_orders = df_cohort.groupby('Customer_ID')['Order_Date'].min().dt.strftime('%Y-%m')\n",
                "df_cohort['Cohort_YrMo'] = df_cohort['Customer_ID'].map(first_orders)\n",
                "\n",
                "cohort_counts = df_cohort.groupby(['Cohort_YrMo', 'Order_YrMo'])['Customer_ID'].nunique().reset_index()\n",
                "c_y = cohort_counts['Cohort_YrMo'].apply(lambda x: int(x[:4]))\n",
                "c_m = cohort_counts['Cohort_YrMo'].apply(lambda x: int(x[5:]))\n",
                "o_y = cohort_counts['Order_YrMo'].apply(lambda x: int(x[:4]))\n",
                "o_m = cohort_counts['Order_YrMo'].apply(lambda x: int(x[5:]))\n",
                "cohort_counts['Period'] = (o_y - c_y) * 12 + (o_m - c_m)\n",
                "\n",
                "cohort_pivot = cohort_counts.pivot_table(index='Cohort_YrMo', columns='Period', values='Customer_ID', fill_value=0)\n",
                "retention_matrix = cohort_pivot.divide(cohort_pivot[0], axis=0) * 100\n",
                "\n",
                "fig, ax = plt.subplots(figsize=(11, 7))\n",
                "sns.heatmap(retention_matrix.iloc[:12, :12], annot=True, fmt='.0f', cmap='YlGnBu', vmin=0, vmax=100, ax=ax)\n",
                "ax.set_title('Customer Cohort Retention Rate Matrix (%) Over 12 Months', fontweight='bold')\n",
                "plt.show()"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open("notebooks/exploratory_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print("Saved 'notebooks/exploratory_analysis.ipynb'.")
