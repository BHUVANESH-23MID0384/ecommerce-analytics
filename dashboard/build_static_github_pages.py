"""
build_static_github_pages.py
Generates a 100% standalone, serverless HTML dashboard at 'docs/index.html'
containing all 5 pages, Plotly charts, interactive filters, tables, and KPIs.
Ready to be hosted permanently 24/7 on GitHub Pages for free!
"""

import os
import json
import sqlite3
import pandas as pd

DB_PATH = "ecommerce.db"
DOCS_DIR = "docs"
os.makedirs(DOCS_DIR, exist_ok=True)

def generate_static_html():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Extract all pre-aggregated data slices for client-side instant filtering
    # 1. Base transactions aggregation
    df = pd.read_sql_query("""
        SELECT 
            f.order_id,
            f.customer_id,
            f.product_id,
            f.net_sales,
            f.profit,
            f.discount_rate,
            f.discount_bracket,
            f.ship_mode,
            f.shipping_duration_days,
            f.return_flag,
            d.year,
            d.month,
            d.month_name,
            d.year || '-' || SUBSTR('0' || d.month, -2, 2) AS yr_mo,
            l.region,
            l.state,
            l.city,
            c.customer_name,
            c.customer_segment,
            p.product_name,
            p.category,
            p.sub_category
        FROM fact_sales f
        JOIN dim_date d ON f.order_date = d.date_key
        JOIN dim_location l ON f.location_id = l.location_id
        JOIN dim_customer c ON f.customer_id = c.customer_id
        JOIN dim_product p ON f.product_id = p.product_id;
    """, conn)

    rfm_df = pd.read_sql_query("""
        SELECT 
            customer_segment_rfm,
            COUNT(customer_id) AS cust_count,
            SUM(monetary) AS total_revenue
        FROM rfm_customer_segments
        GROUP BY customer_segment_rfm;
    """, conn)

    conn.close()

    # Pre-calculate aggregates for All, by Year, by Region, by Segment
    # To keep the static HTML lightweight and fast (under 300KB), we embed multi-dimensional pre-aggregates!
    slices = {}
    
    years = ["All"] + sorted([str(y) for y in df["year"].unique()])
    regions = ["All"] + sorted(list(df["region"].unique()))
    segments = ["All"] + sorted(list(df["customer_segment"].unique()))

    print(f"Building pre-aggregated data slices across {len(years)} years x {len(regions)} regions x {len(segments)} segments...")

    for y in years:
        for r in regions:
            for s in segments:
                sub = df.copy()
                if y != "All":
                    sub = sub[sub["year"] == int(y)]
                if r != "All":
                    sub = sub[sub["region"] == r]
                if s != "All":
                    sub = sub[sub["customer_segment"] == s]

                key = f"{y}_{r}_{s}"
                
                rev = float(sub["net_sales"].sum())
                prof = float(sub["profit"].sum())
                orders = int(sub["order_id"].nunique())
                margin = (prof / rev * 100) if rev > 0 else 0.0
                aov = (rev / orders) if orders > 0 else 0.0

                # Monthly
                m_agg = sub.groupby("yr_mo").agg(revenue=("net_sales", "sum"), profit=("profit", "sum")).reset_index()
                m_dates = list(m_agg["yr_mo"])
                m_rev = [round(float(v), 2) for v in m_agg["revenue"]]
                m_margin = [round((float(p) / float(v) * 100) if float(v) > 0 else 0.0, 2) for p, v in zip(m_agg["profit"], m_agg["revenue"])]

                # Category
                cat_agg = sub.groupby("category")["net_sales"].sum().sort_values(ascending=True)
                cats = list(cat_agg.index)
                cat_rev = [round(float(v), 2) for v in cat_agg.values]

                # Segment
                seg_agg = sub.groupby("customer_segment")["net_sales"].sum()
                segs = list(seg_agg.index)
                seg_rev = [round(float(v), 2) for v in seg_agg.values]

                # Region
                reg_agg = sub.groupby("region")["net_sales"].sum().sort_values(ascending=False)
                regs = list(reg_agg.index)
                reg_rev = [round(float(v), 2) for v in reg_agg.values]

                # Subcat
                subcat_agg = sub.groupby("sub_category")["net_sales"].sum().sort_values(ascending=True).tail(15)
                subcats = list(subcat_agg.index)
                subcat_rev = [round(float(v), 2) for v in subcat_agg.values]

                # Seasonality
                s_agg = sub.groupby(["year", "month"])["net_sales"].sum().reset_index()
                z_years = [2022, 2023, 2024, 2025] if y == "All" else [int(y)]
                z_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                z_mat = [[0 for _ in z_years] for _ in z_months]
                for _, row in s_agg.iterrows():
                    yr_val = int(row["year"])
                    mo_val = int(row["month"]) - 1
                    if yr_val in z_years and 0 <= mo_val < 12:
                        z_mat[mo_val][z_years.index(yr_val)] = round(float(row["net_sales"]) / 1e3, 1)

                # Top Customers (Top 10)
                cust_agg = sub.groupby(["customer_id", "customer_name", "customer_segment", "city", "state"]).agg(
                    revenue=("net_sales", "sum"),
                    profit=("profit", "sum")
                ).reset_index().sort_values("revenue", ascending=False).head(10)
                
                top_cust = []
                for _, c_row in cust_agg.iterrows():
                    c_rev = float(c_row["revenue"])
                    c_prof = float(c_row["profit"])
                    top_cust.append({
                        "customer_id": c_row["customer_id"],
                        "customer_name": c_row["customer_name"],
                        "segment": c_row["customer_segment"],
                        "city": c_row["city"],
                        "state": c_row["state"],
                        "revenue": round(c_rev, 2),
                        "profit": round(c_prof, 2),
                        "margin": round((c_prof / c_rev * 100) if c_rev > 0 else 0.0, 2)
                    })

                # Loss SKUs
                prod_agg = sub.groupby(["product_name", "category", "sub_category"]).agg(
                    revenue=("net_sales", "sum"),
                    profit=("profit", "sum"),
                    avg_discount=("discount_rate", "mean")
                ).reset_index()
                loss_df = prod_agg[prod_agg["profit"] < 0].sort_values("profit", ascending=True).head(10)
                loss_skus = []
                for _, l_row in loss_df.iterrows():
                    l_rev = float(l_row["revenue"])
                    l_prof = float(l_row["profit"])
                    loss_skus.append({
                        "product_name": l_row["product_name"],
                        "category": l_row["category"],
                        "sub_category": l_row["sub_category"],
                        "revenue": round(l_rev, 2),
                        "profit": round(l_prof, 2),
                        "margin": round((l_prof / l_rev * 100) if l_rev > 0 else 0.0, 2),
                        "discount": round(float(l_row["avg_discount"]) * 100, 2)
                    })

                # Scatter sample
                sample_prod = prod_agg.sample(n=min(120, len(prod_agg)), random_state=42) if len(prod_agg) > 0 else prod_agg
                scatter_data = {
                    "names": list(sample_prod["product_name"]),
                    "revenue": [round(float(v), 2) for v in sample_prod["revenue"]],
                    "margin": [round((float(p)/float(v)*100) if float(v)>0 else 0.0, 2) for p, v in zip(sample_prod["profit"], sample_prod["revenue"])]
                }

                # Discount Erosion
                disc_agg = sub.groupby("discount_bracket").agg(revenue=("net_sales", "sum"), profit=("profit", "sum"))
                bracket_order = ["None (0%)", "Low (1-15%)", "Medium (16-30%)", "High (31%+)"]
                disc_margins = []
                for b in bracket_order:
                    if b in disc_agg.index:
                        b_rev = disc_agg.loc[b, "revenue"]
                        b_prof = disc_agg.loc[b, "profit"]
                        disc_margins.append(round((b_prof / b_rev * 100) if b_rev > 0 else 0.0, 2))
                    else:
                        disc_margins.append(0.0)

                # Shipping performance
                ship_agg = sub.groupby("ship_mode")["shipping_duration_days"].mean()
                ship_modes = list(ship_agg.index)
                ship_days = [round(float(v), 1) for v in ship_agg.values]

                # Return rates
                ret_agg = sub.groupby("sub_category")["return_flag"].mean().sort_values(ascending=True)
                ret_subcats = list(ret_agg.index)
                ret_rates = [round(float(v) * 100, 2) for v in ret_agg.values]

                slices[key] = {
                    "kpis": {"revenue": rev, "profit": prof, "margin": margin, "orders": orders, "aov": aov},
                    "monthly_trend": {"dates": m_dates, "revenue": m_rev, "margin": m_margin},
                    "category_perf": {"categories": cats, "revenue": cat_rev},
                    "segment_perf": {"segments": segs, "revenue": seg_rev},
                    "regional_perf": {"regions": regs, "revenue": reg_rev},
                    "subcat_perf": {"subcats": subcats, "revenue": subcat_rev},
                    "seasonality": {"years": z_years, "months": z_months, "z": z_mat},
                    "top_customers": top_cust,
                    "scatter": scatter_data,
                    "discount_erosion": {"brackets": bracket_order, "margins": disc_margins},
                    "loss_skus": loss_skus,
                    "shipping_perf": {"modes": ship_modes, "delivery_days": ship_days},
                    "return_rates": {"subcats": ret_subcats, "rates": ret_rates}
                }

    # RFM global data
    rfm_data = {
        "segments": list(rfm_df["customer_segment_rfm"]),
        "counts": [int(v) for v in rfm_df["cust_count"]],
        "revenue": [round(float(v), 2) for v in rfm_df["total_revenue"]]
    }

    embedded_json = json.dumps({"slices": slices, "rfm": rfm_data})

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Executive Analytics Dashboard | Live 24/7</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Plotly.js CDN -->
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; background-color: #f8fafc; }}
        .tab-btn.active {{ border-bottom: 3px solid #2563eb; color: #2563eb; font-weight: 600; }}
        .card-shadow {{ box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); }}
    </style>
</head>
<body class="text-slate-800 antialiased">

    <!-- Top Navigation Header -->
    <header class="bg-slate-900 text-white shadow-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="bg-blue-600 p-2 rounded-lg text-white">
                    <i data-lucide="bar-chart-3" class="w-6 h-6"></i>
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <h1 class="text-lg sm:text-xl font-bold tracking-tight">E-Commerce Executive Intelligence Platform</h1>
                        <span class="bg-emerald-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full animate-pulse">LIVE 24/7</span>
                    </div>
                    <p class="text-xs text-slate-400">Sales, Customer Lifetime Value & Profitability Engine (2022–2025)</p>
                </div>
            </div>
            
            <!-- Global Interactive Filter Bar -->
            <div class="flex flex-wrap items-center gap-3 mt-2 sm:mt-0 text-sm">
                <div>
                    <label class="text-[11px] text-slate-400 block mb-0.5">Fiscal Year</label>
                    <select id="filter-year" onchange="renderDashboard()" class="bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-blue-500">
                        <option value="All">All Years (2022-2025)</option>
                        <option value="2022">2022</option>
                        <option value="2023">2023</option>
                        <option value="2024">2024</option>
                        <option value="2025">2025</option>
                    </select>
                </div>
                <div>
                    <label class="text-[11px] text-slate-400 block mb-0.5">Region</label>
                    <select id="filter-region" onchange="renderDashboard()" class="bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-blue-500">
                        <option value="All">All Regions</option>
                        <option value="East">East</option>
                        <option value="West">West</option>
                        <option value="Central">Central</option>
                        <option value="South">South</option>
                    </select>
                </div>
                <div>
                    <label class="text-[11px] text-slate-400 block mb-0.5">Segment</label>
                    <select id="filter-segment" onchange="renderDashboard()" class="bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-blue-500">
                        <option value="All">All Segments</option>
                        <option value="Consumer">Consumer</option>
                        <option value="Corporate">Corporate</option>
                        <option value="Home Office">Home Office</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Tab Navigation Navigation -->
        <nav class="bg-slate-800 border-t border-slate-700">
            <div class="max-w-7xl mx-auto px-4 flex space-x-6 overflow-x-auto text-xs sm:text-sm">
                <button onclick="switchTab('page1')" id="tab-page1" class="tab-btn active py-2.5 text-slate-300 hover:text-white flex items-center space-x-2">
                    <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
                    <span>1. Executive Overview</span>
                </button>
                <button onclick="switchTab('page2')" id="tab-page2" class="tab-btn py-2.5 text-slate-300 hover:text-white flex items-center space-x-2">
                    <i data-lucide="trending-up" class="w-4 h-4"></i>
                    <span>2. Sales & Seasonality</span>
                </button>
                <button onclick="switchTab('page3')" id="tab-page3" class="tab-btn py-2.5 text-slate-300 hover:text-white flex items-center space-x-2">
                    <i data-lucide="users" class="w-4 h-4"></i>
                    <span>3. Customer & RFM</span>
                </button>
                <button onclick="switchTab('page4')" id="tab-page4" class="tab-btn py-2.5 text-slate-300 hover:text-white flex items-center space-x-2">
                    <i data-lucide="percent" class="w-4 h-4"></i>
                    <span>4. Product & Profitability</span>
                </button>
                <button onclick="switchTab('page5')" id="tab-page5" class="tab-btn py-2.5 text-slate-300 hover:text-white flex items-center space-x-2">
                    <i data-lucide="truck" class="w-4 h-4"></i>
                    <span>5. Regional & Logistics</span>
                </button>
            </div>
        </nav>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

        <!-- Top KPI Cards Row -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3">
                <div class="p-3 bg-blue-50 text-blue-600 rounded-lg"><i data-lucide="dollar-sign" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Total Revenue</p>
                    <h3 id="kpi-revenue" class="text-xl font-bold text-slate-900">$48.45M</h3>
                </div>
            </div>
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3">
                <div class="p-3 bg-emerald-50 text-emerald-600 rounded-lg"><i data-lucide="trending-up" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Total Profit</p>
                    <h3 id="kpi-profit" class="text-xl font-bold text-slate-900">$7.76M</h3>
                </div>
            </div>
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3">
                <div class="p-3 bg-purple-50 text-purple-600 rounded-lg"><i data-lucide="pie-chart" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Profit Margin</p>
                    <h3 id="kpi-margin" class="text-xl font-bold text-slate-900">16.03%</h3>
                </div>
            </div>
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3">
                <div class="p-3 bg-indigo-50 text-indigo-600 rounded-lg"><i data-lucide="shopping-bag" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Total Orders</p>
                    <h3 id="kpi-orders" class="text-xl font-bold text-slate-900">36,120</h3>
                </div>
            </div>
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3 col-span-2 sm:col-span-1">
                <div class="p-3 bg-amber-50 text-amber-600 rounded-lg"><i data-lucide="credit-card" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Avg Order Value</p>
                    <h3 id="kpi-aov" class="text-xl font-bold text-slate-900">$1,341</h3>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 1: EXECUTIVE OVERVIEW -->
        <!-- ============================================================== -->
        <div id="page1" class="tab-content space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100 lg:col-span-2">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Monthly Revenue & Profit Margin Trajectory</h2>
                    <p class="text-xs text-slate-500 mb-4">Historical monthly performance showing revenue volume and realized margin %</p>
                    <div id="chart-monthly-trend" class="h-80 w-full"></div>
                </div>
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Category Revenue Breakdown</h2>
                    <p class="text-xs text-slate-500 mb-4">Total revenue across product categories</p>
                    <div id="chart-category-perf" class="h-80 w-full"></div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Revenue Share by Customer Segment</h2>
                    <p class="text-xs text-slate-500 mb-4">Consumer vs Corporate vs Home Office</p>
                    <div id="chart-segment-donut" class="h-72 w-full"></div>
                </div>
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Regional Performance & Profitability</h2>
                    <p class="text-xs text-slate-500 mb-4">Total revenue across geographic territories</p>
                    <div id="chart-regional-bar" class="h-72 w-full"></div>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 2: SALES & SEASONALITY -->
        <!-- ============================================================== -->
        <div id="page2" class="tab-content hidden space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100 lg:col-span-2">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Top 15 Sub-Categories by Revenue</h2>
                    <p class="text-xs text-slate-500 mb-4">Ranking product lines across all categories</p>
                    <div id="chart-subcat-rank" class="h-96 w-full"></div>
                </div>
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Monthly Seasonality Heatmap ($K)</h2>
                    <p class="text-xs text-slate-500 mb-4">Identifying Q4 holiday surge patterns</p>
                    <div id="chart-seasonality-heat" class="h-96 w-full"></div>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 3: CUSTOMER & RFM -->
        <!-- ============================================================== -->
        <div id="page3" class="tab-content hidden space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">RFM Customer Segment Distribution</h2>
                    <p class="text-xs text-slate-500 mb-4">Customer count across behavioral RFM tiers</p>
                    <div id="chart-rfm-counts" class="h-80 w-full"></div>
                </div>
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">RFM Segment Revenue Contribution ($M)</h2>
                    <p class="text-xs text-slate-500 mb-4">Dollar volume generated by each customer cohort</p>
                    <div id="chart-rfm-revenue" class="h-80 w-full"></div>
                </div>
            </div>

            <!-- Top Customers Table -->
            <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                <h2 class="text-base font-semibold text-slate-900 mb-1">Top 10 High-Value VIP Customers (Lifetime Spend)</h2>
                <p class="text-xs text-slate-500 mb-4">Key accounts generating significant lifetime profit</p>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs border-collapse">
                        <thead>
                            <tr class="bg-slate-50 border-b border-slate-200 text-slate-600">
                                <th class="py-2.5 px-3">Customer ID</th>
                                <th class="py-2.5 px-3">Customer Name</th>
                                <th class="py-2.5 px-3">Segment</th>
                                <th class="py-2.5 px-3">City, State</th>
                                <th class="py-2.5 px-3">Total Spend</th>
                                <th class="py-2.5 px-3">Total Profit</th>
                                <th class="py-2.5 px-3">Margin %</th>
                            </tr>
                        </thead>
                        <tbody id="top-customers-tbody" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 4: PRODUCT & PROFITABILITY -->
        <!-- ============================================================== -->
        <div id="page4" class="tab-content hidden space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100 lg:col-span-2">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Product Profitability 4-Quadrant Matrix</h2>
                    <p class="text-xs text-slate-500 mb-4">Revenue vs Profit Margin % across catalog SKUs</p>
                    <div id="chart-quadrant-scatter" class="h-80 w-full"></div>
                </div>
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Discount Margin Erosion</h2>
                    <p class="text-xs text-slate-500 mb-4">Realized margin % across discount brackets</p>
                    <div id="chart-discount-erosion" class="h-80 w-full"></div>
                </div>
            </div>

            <!-- Loss-Making SKUs Table -->
            <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                <h2 class="text-base font-semibold text-slate-900 mb-1 text-red-600 flex items-center space-x-2">
                    <i data-lucide="alert-triangle" class="w-4 h-4"></i>
                    <span>Loss-Making Products Requiring Pricing Review</span>
                </h2>
                <p class="text-xs text-slate-500 mb-4">SKUs generating negative profit due to deep discounting</p>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs border-collapse">
                        <thead>
                            <tr class="bg-slate-50 border-b border-slate-200 text-slate-600">
                                <th class="py-2.5 px-3">Product Name</th>
                                <th class="py-2.5 px-3">Category</th>
                                <th class="py-2.5 px-3">Sub-Category</th>
                                <th class="py-2.5 px-3">Revenue ($)</th>
                                <th class="py-2.5 px-3">Net Profit ($)</th>
                                <th class="py-2.5 px-3">Realized Margin</th>
                                <th class="py-2.5 px-3">Avg Discount</th>
                            </tr>
                        </thead>
                        <tbody id="loss-skus-tbody" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 5: REGIONAL & LOGISTICS -->
        <!-- ============================================================== -->
        <div id="page5" class="tab-content hidden space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Shipping Tier Performance & Delivery Days</h2>
                    <p class="text-xs text-slate-500 mb-4">Standard vs Second Class vs First Class vs Same Day</p>
                    <div id="chart-shipping-perf" class="h-80 w-full"></div>
                </div>
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Return Rate by Product Sub-Category</h2>
                    <p class="text-xs text-slate-500 mb-4">Identifying lines with highest return rates (Apparel & Furniture)</p>
                    <div id="chart-return-rates" class="h-80 w-full"></div>
                </div>
            </div>
        </div>

    </main>

    <!-- Embedded High-Performance Pre-Calculated Data Store -->
    <script>
        const DATASTORE = {embedded_json};

        lucide.createIcons();

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.remove('hidden');
            document.getElementById('tab-' + tabId).classList.add('active');
            
            window.dispatchEvent(new Event('resize'));
        }}

        function renderDashboard() {{
            const y = document.getElementById('filter-year').value;
            const r = document.getElementById('filter-region').value;
            const s = document.getElementById('filter-segment').value;

            const key = `${{y}}_${{r}}_${{s}}`;
            const data = DATASTORE.slices[key] || DATASTORE.slices['All_All_All'];
            const rfm = DATASTORE.rfm;

            // 1. Update KPI Cards
            document.getElementById('kpi-revenue').innerText = '$' + (data.kpis.revenue / 1e6).toFixed(2) + 'M';
            document.getElementById('kpi-profit').innerText = '$' + (data.kpis.profit / 1e6).toFixed(2) + 'M';
            document.getElementById('kpi-margin').innerText = data.kpis.margin.toFixed(2) + '%';
            document.getElementById('kpi-orders').innerText = data.kpis.orders.toLocaleString();
            document.getElementById('kpi-aov').innerText = '$' + data.kpis.aov.toLocaleString(undefined, {{maximumFractionDigits: 0}});

            // 2. Monthly Revenue & Margin Trend
            Plotly.newPlot('chart-monthly-trend', [
                {{
                    x: data.monthly_trend.dates,
                    y: data.monthly_trend.revenue.map(v => v / 1e3),
                    name: 'Revenue ($K)',
                    type: 'bar',
                    marker: {{ color: '#3b82f6' }}
                }},
                {{
                    x: data.monthly_trend.dates,
                    y: data.monthly_trend.margin,
                    name: 'Margin %',
                    type: 'scatter',
                    yaxis: 'y2',
                    mode: 'lines+markers',
                    line: {{ color: '#10b981', width: 2.5 }}
                }}
            ], {{
                margin: {{ t: 20, r: 40, l: 50, b: 40 }},
                yaxis: {{ title: 'Revenue ($K)' }},
                yaxis2: {{ title: 'Margin %', overlaying: 'y', side: 'right', showgrid: false }},
                legend: {{ orientation: 'h', y: -0.2 }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 3. Category Performance
            Plotly.newPlot('chart-category-perf', [{{
                x: data.category_perf.revenue.map(v => v / 1e6),
                y: data.category_perf.categories,
                type: 'bar',
                orientation: 'h',
                marker: {{ color: ['#1e40af', '#ea580c', '#7c3aed', '#059669'] }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 110, b: 40 }},
                xaxis: {{ title: 'Revenue ($M)' }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 4. Segment Donut
            Plotly.newPlot('chart-segment-donut', [{{
                values: data.segment_perf.revenue,
                labels: data.segment_perf.segments,
                type: 'pie',
                hole: 0.55,
                marker: {{ colors: ['#2563eb', '#f59e0b', '#10b981'] }}
            }}], {{
                margin: {{ t: 10, r: 10, l: 10, b: 10 }},
                legend: {{ orientation: 'h', y: -0.1 }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 5. Regional Bar
            Plotly.newPlot('chart-regional-bar', [{{
                x: data.regional_perf.regions,
                y: data.regional_perf.revenue.map(v => v / 1e6),
                type: 'bar',
                marker: {{ color: '#6366f1' }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 50, b: 40 }},
                yaxis: {{ title: 'Revenue ($M)' }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 6. Top 15 Sub-Categories
            Plotly.newPlot('chart-subcat-rank', [{{
                x: data.subcat_perf.revenue.map(v => v / 1e3),
                y: data.subcat_perf.subcats,
                type: 'bar',
                orientation: 'h',
                marker: {{ color: '#3b82f6' }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 100, b: 40 }},
                xaxis: {{ title: 'Revenue ($K)' }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 7. Seasonality Heatmap
            Plotly.newPlot('chart-seasonality-heat', [{{
                z: data.seasonality.z,
                x: data.seasonality.years,
                y: data.seasonality.months,
                type: 'heatmap',
                colorscale: 'Blues'
            }}], {{
                margin: {{ t: 10, r: 10, l: 50, b: 30 }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 8. RFM Charts
            Plotly.newPlot('chart-rfm-counts', [{{
                x: rfm.counts,
                y: rfm.segments,
                type: 'bar',
                orientation: 'h',
                marker: {{ color: '#10b981' }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 130, b: 40 }},
                xaxis: {{ title: 'Customer Count' }}
            }}, {{ responsive: true, displayModeBar: false }});

            Plotly.newPlot('chart-rfm-revenue', [{{
                x: rfm.revenue.map(v => v / 1e6),
                y: rfm.segments,
                type: 'bar',
                orientation: 'h',
                marker: {{ color: '#3b82f6' }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 130, b: 40 }},
                xaxis: {{ title: 'Revenue ($M)' }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 9. Top Customers Table
            const custTbody = document.getElementById('top-customers-tbody');
            custTbody.innerHTML = '';
            data.top_customers.forEach(c => {{
                custTbody.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="py-2.5 px-3 font-mono text-slate-500">${{c.customer_id}}</td>
                        <td class="py-2.5 px-3 font-medium text-slate-900">${{c.customer_name}}</td>
                        <td class="py-2.5 px-3">${{c.segment}}</td>
                        <td class="py-2.5 px-3 text-slate-500">${{c.city}}, ${{c.state}}</td>
                        <td class="py-2.5 px-3 font-semibold text-slate-900">$${{c.revenue.toLocaleString()}}</td>
                        <td class="py-2.5 px-3 font-semibold text-emerald-600">$${{c.profit.toLocaleString()}}</td>
                        <td class="py-2.5 px-3">${{c.margin.toFixed(1)}}%</td>
                    </tr>
                `;
            }});

            // 10. Scatter Plot
            Plotly.newPlot('chart-quadrant-scatter', [{{
                x: data.scatter.revenue,
                y: data.scatter.margin,
                text: data.scatter.names,
                mode: 'markers',
                type: 'scatter',
                marker: {{ size: 7, color: '#2563eb', opacity: 0.6 }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 50, b: 40 }},
                xaxis: {{ title: 'Total Revenue ($)' }},
                yaxis: {{ title: 'Margin %' }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 11. Discount Erosion
            Plotly.newPlot('chart-discount-erosion', [{{
                x: data.discount_erosion.brackets,
                y: data.discount_erosion.margins,
                type: 'bar',
                marker: {{ color: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'] }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 40, b: 40 }},
                yaxis: {{ title: 'Realized Margin %' }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 12. Loss SKUs Table
            const lossTbody = document.getElementById('loss-skus-tbody');
            lossTbody.innerHTML = '';
            data.loss_skus.forEach(p => {{
                lossTbody.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="py-2.5 px-3 font-medium text-slate-900">${{p.product_name}}</td>
                        <td class="py-2.5 px-3">${{p.category}}</td>
                        <td class="py-2.5 px-3">${{p.sub_category}}</td>
                        <td class="py-2.5 px-3">$${{p.revenue.toLocaleString()}}</td>
                        <td class="py-2.5 px-3 font-semibold text-red-600">-$${{Math.abs(p.profit).toLocaleString()}}</td>
                        <td class="py-2.5 px-3 font-semibold text-red-600">${{p.margin.toFixed(1)}}%</td>
                        <td class="py-2.5 px-3">${{p.discount.toFixed(1)}}%</td>
                    </tr>
                `;
            }});

            // 13. Shipping Performance
            Plotly.newPlot('chart-shipping-perf', [{{
                x: data.shipping_perf.modes,
                y: data.shipping_perf.delivery_days,
                type: 'bar',
                marker: {{ color: '#8b5cf6' }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 40, b: 40 }},
                yaxis: {{ title: 'Avg Delivery Days' }}
            }}, {{ responsive: true, displayModeBar: false }});

            // 14. Return Rates
            Plotly.newPlot('chart-return-rates', [{{
                x: data.return_rates.rates,
                y: data.return_rates.subcats,
                type: 'bar',
                orientation: 'h',
                marker: {{ color: '#f43f5e' }}
            }}], {{
                margin: {{ t: 10, r: 20, l: 100, b: 40 }},
                xaxis: {{ title: 'Return Rate %' }}
            }}, {{ responsive: true, displayModeBar: false }});
        }}

        window.addEventListener('DOMContentLoaded', renderDashboard);
    </script>
</body>
</html>
"""

    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Also copy to root index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Successfully generated standalone 24/7 static dashboard at: '{out_path}' and 'index.html'.")

if __name__ == "__main__":
    generate_static_html()
