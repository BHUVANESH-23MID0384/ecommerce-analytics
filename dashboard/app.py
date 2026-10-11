"""
app.py
Standalone Interactive Web Dashboard Server for E-Commerce Analytics Platform.
Serves a responsive 5-page enterprise dashboard with interactive Plotly charts,
dynamic KPI cards, and multi-dimensional filtering using Flask and SQLite.
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)
DB_PATH = "ecommerce.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Sales & Profitability Analytics Dashboard</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Plotly.js CDN -->
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .tab-btn.active { border-bottom: 3px solid #2563eb; color: #2563eb; font-weight: 600; }
        .card-shadow { box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); }
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
                    <h1 class="text-xl font-bold tracking-tight">E-Commerce Executive Intelligence Platform</h1>
                    <p class="text-xs text-slate-400">Sales, Customer Lifetime Value & Profitability Engine (2022–2025)</p>
                </div>
            </div>
            
            <!-- Global Interactive Filter Bar -->
            <div class="flex flex-wrap items-center gap-3 mt-2 sm:mt-0 text-sm">
                <div>
                    <label class="text-xs text-slate-400 block mb-0.5">Fiscal Year</label>
                    <select id="filter-year" onchange="updateDashboard()" class="bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-blue-500">
                        <option value="All">All Years (2022-2025)</option>
                        <option value="2022">2022</option>
                        <option value="2023">2023</option>
                        <option value="2024">2024</option>
                        <option value="2025">2025</option>
                    </select>
                </div>
                <div>
                    <label class="text-xs text-slate-400 block mb-0.5">Region</label>
                    <select id="filter-region" onchange="updateDashboard()" class="bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-blue-500">
                        <option value="All">All Regions</option>
                        <option value="East">East</option>
                        <option value="West">West</option>
                        <option value="Central">Central</option>
                        <option value="South">South</option>
                    </select>
                </div>
                <div>
                    <label class="text-xs text-slate-400 block mb-0.5">Segment</label>
                    <select id="filter-segment" onchange="updateDashboard()" class="bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-blue-500">
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
                    <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Revenue</p>
                    <h3 id="kpi-revenue" class="text-xl font-bold text-slate-900">$48.45M</h3>
                </div>
            </div>
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3">
                <div class="p-3 bg-emerald-50 text-emerald-600 rounded-lg"><i data-lucide="trending-up" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Profit</p>
                    <h3 id="kpi-profit" class="text-xl font-bold text-slate-900">$7.76M</h3>
                </div>
            </div>
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3">
                <div class="p-3 bg-purple-50 text-purple-600 rounded-lg"><i data-lucide="pie-chart" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Profit Margin</p>
                    <h3 id="kpi-margin" class="text-xl font-bold text-slate-900">16.03%</h3>
                </div>
            </div>
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3">
                <div class="p-3 bg-indigo-50 text-indigo-600 rounded-lg"><i data-lucide="shopping-bag" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Orders</p>
                    <h3 id="kpi-orders" class="text-xl font-bold text-slate-900">36,120</h3>
                </div>
            </div>
            <div class="bg-white rounded-xl p-4 card-shadow border border-slate-100 flex items-center space-x-3 col-span-2 sm:col-span-1">
                <div class="p-3 bg-amber-50 text-amber-600 rounded-lg"><i data-lucide="credit-card" class="w-6 h-6"></i></div>
                <div>
                    <p class="text-xs font-medium text-slate-500 uppercase tracking-wider">Avg Order Value</p>
                    <h3 id="kpi-aov" class="text-xl font-bold text-slate-900">$1,341</h3>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 1: EXECUTIVE OVERVIEW -->
        <!-- ============================================================== -->
        <div id="page1" class="tab-content space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Revenue & Profit Trend -->
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100 lg:col-span-2">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Monthly Revenue & Profit Margin Trajectory</h2>
                    <p class="text-xs text-slate-500 mb-4">Historical performance showing revenue volume and realized margin %</p>
                    <div id="chart-monthly-trend" class="h-80 w-full"></div>
                </div>
                <!-- Category Revenue & Margin -->
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Category Revenue Breakdown</h2>
                    <p class="text-xs text-slate-500 mb-4">Total revenue and realized margin percentage</p>
                    <div id="chart-category-perf" class="h-80 w-full"></div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Customer Segment Donut -->
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Revenue Share by Customer Segment</h2>
                    <p class="text-xs text-slate-500 mb-4">Consumer vs Corporate vs Home Office</p>
                    <div id="chart-segment-donut" class="h-72 w-full"></div>
                </div>
                <!-- Regional Revenue -->
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Regional Performance & Profitability</h2>
                    <p class="text-xs text-slate-500 mb-4">Total revenue and profit by territory</p>
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
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Monthly Seasonality Heatmap</h2>
                    <p class="text-xs text-slate-500 mb-4">Identifying Q4 surge patterns</p>
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
                    <h2 class="text-base font-semibold text-slate-900 mb-1">RFM Segment Revenue Contribution ($)</h2>
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
                        <tbody id="top-customers-tbody" class="divide-y divide-slate-100">
                            <!-- Populated dynamically via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ============================================================== -->
        <!-- TAB 4: PRODUCT & PROFITABILITY -->
        <!-- ============================================================== -->
        <div id="page4" class="tab-content hidden space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- 4-Quadrant Scatter -->
                <div class="bg-white p-5 rounded-xl card-shadow border border-slate-100 lg:col-span-2">
                    <h2 class="text-base font-semibold text-slate-900 mb-1">Product Profitability 4-Quadrant Matrix</h2>
                    <p class="text-xs text-slate-500 mb-4">Revenue vs Profit Margin % across all catalog SKUs</p>
                    <div id="chart-quadrant-scatter" class="h-80 w-full"></div>
                </div>
                <!-- Discount Margin Erosion -->
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
                        <tbody id="loss-skus-tbody" class="divide-y divide-slate-100">
                            <!-- Populated dynamically via JS -->
                        </tbody>
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

    <!-- Client-Side Dashboard JS Logic -->
    <script>
        lucide.createIcons();

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.remove('hidden');
            document.getElementById('tab-' + tabId).classList.add('active');
            
            // Trigger Plotly resize for newly visible charts
            window.dispatchEvent(new Event('resize'));
        }

        async function updateDashboard() {
            const year = document.getElementById('filter-year').value;
            const region = document.getElementById('filter-region').value;
            const segment = document.getElementById('filter-segment').value;

            const response = await fetch(`/api/data?year=${year}&region=${region}&segment=${segment}`);
            const data = await response.json();

            // Update KPI cards
            document.getElementById('kpi-revenue').innerText = '$' + (data.kpis.revenue / 1e6).toFixed(2) + 'M';
            document.getElementById('kpi-profit').innerText = '$' + (data.kpis.profit / 1e6).toFixed(2) + 'M';
            document.getElementById('kpi-margin').innerText = data.kpis.margin.toFixed(2) + '%';
            document.getElementById('kpi-orders').innerText = data.kpis.orders.toLocaleString();
            document.getElementById('kpi-aov').innerText = '$' + data.kpis.aov.toLocaleString(undefined, {maximumFractionDigits: 0});

            // 1. Monthly Revenue & Margin Trend
            Plotly.newPlot('chart-monthly-trend', [
                {
                    x: data.monthly_trend.dates,
                    y: data.monthly_trend.revenue.map(v => v / 1e3),
                    name: 'Revenue ($K)',
                    type: 'bar',
                    marker: { color: '#3b82f6' }
                },
                {
                    x: data.monthly_trend.dates,
                    y: data.monthly_trend.margin,
                    name: 'Margin %',
                    type: 'scatter',
                    yaxis: 'y2',
                    mode: 'lines+markers',
                    line: { color: '#10b981', width: 2.5 }
                }
            ], {
                margin: { t: 20, r: 40, l: 50, b: 40 },
                yaxis: { title: 'Revenue ($K)' },
                yaxis2: { title: 'Margin %', overlaying: 'y', side: 'right', showgrid: false },
                legend: { orientation: 'h', y: -0.2 }
            }, { responsive: true, displayModeBar: false });

            // 2. Category Performance
            Plotly.newPlot('chart-category-perf', [{
                x: data.category_perf.revenue.map(v => v / 1e6),
                y: data.category_perf.categories,
                type: 'bar',
                orientation: 'h',
                marker: { color: ['#1e40af', '#ea580c', '#7c3aed', '#059669'] }
            }], {
                margin: { t: 10, r: 20, l: 110, b: 40 },
                xaxis: { title: 'Revenue ($M)' }
            }, { responsive: true, displayModeBar: false });

            // 3. Segment Donut
            Plotly.newPlot('chart-segment-donut', [{
                values: data.segment_perf.revenue,
                labels: data.segment_perf.segments,
                type: 'pie',
                hole: 0.55,
                marker: { colors: ['#2563eb', '#f59e0b', '#10b981'] }
            }], {
                margin: { t: 10, r: 10, l: 10, b: 10 },
                legend: { orientation: 'h', y: -0.1 }
            }, { responsive: true, displayModeBar: false });

            // 4. Regional Bar
            Plotly.newPlot('chart-regional-bar', [{
                x: data.regional_perf.regions,
                y: data.regional_perf.revenue.map(v => v / 1e6),
                type: 'bar',
                marker: { color: '#6366f1' }
            }], {
                margin: { t: 10, r: 20, l: 50, b: 40 },
                yaxis: { title: 'Revenue ($M)' }
            }, { responsive: true, displayModeBar: false });

            // 5. Top 15 Sub-Categories
            Plotly.newPlot('chart-subcat-rank', [{
                x: data.subcat_perf.revenue.map(v => v / 1e3),
                y: data.subcat_perf.subcats,
                type: 'bar',
                orientation: 'h',
                marker: { color: '#3b82f6' }
            }], {
                margin: { t: 10, r: 20, l: 100, b: 40 },
                xaxis: { title: 'Revenue ($K)' }
            }, { responsive: true, displayModeBar: false });

            // 6. Seasonality Heatmap
            Plotly.newPlot('chart-seasonality-heat', [{
                z: data.seasonality.z,
                x: data.seasonality.years,
                y: data.seasonality.months,
                type: 'heatmap',
                colorscale: 'Blues'
            }], {
                margin: { t: 10, r: 10, l: 50, b: 30 }
            }, { responsive: true, displayModeBar: false });

            // 7. RFM Counts & Revenue
            Plotly.newPlot('chart-rfm-counts', [{
                x: data.rfm.counts,
                y: data.rfm.segments,
                type: 'bar',
                orientation: 'h',
                marker: { color: '#10b981' }
            }], {
                margin: { t: 10, r: 20, l: 130, b: 40 },
                xaxis: { title: 'Customer Count' }
            }, { responsive: true, displayModeBar: false });

            Plotly.newPlot('chart-rfm-revenue', [{
                x: data.rfm.revenue.map(v => v / 1e6),
                y: data.rfm.segments,
                type: 'bar',
                orientation: 'h',
                marker: { color: '#3b82f6' }
            }], {
                margin: { t: 10, r: 20, l: 130, b: 40 },
                xaxis: { title: 'Revenue ($M)' }
            }, { responsive: true, displayModeBar: false });

            // 8. Top Customers Table
            const custTbody = document.getElementById('top-customers-tbody');
            custTbody.innerHTML = '';
            data.top_customers.forEach(c => {
                custTbody.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="py-2.5 px-3 font-mono text-slate-500">${c.customer_id}</td>
                        <td class="py-2.5 px-3 font-medium text-slate-900">${c.customer_name}</td>
                        <td class="py-2.5 px-3">${c.segment}</td>
                        <td class="py-2.5 px-3 text-slate-500">${c.city}, ${c.state}</td>
                        <td class="py-2.5 px-3 font-semibold text-slate-900">$${c.revenue.toLocaleString()}</td>
                        <td class="py-2.5 px-3 font-semibold text-emerald-600">$${c.profit.toLocaleString()}</td>
                        <td class="py-2.5 px-3">${c.margin.toFixed(1)}%</td>
                    </tr>
                `;
            });

            // 9. Profitability 4-Quadrant Scatter
            Plotly.newPlot('chart-quadrant-scatter', [{
                x: data.scatter.revenue,
                y: data.scatter.margin,
                text: data.scatter.names,
                mode: 'markers',
                type: 'scatter',
                marker: { size: 7, color: '#2563eb', opacity: 0.6 }
            }], {
                margin: { t: 10, r: 20, l: 50, b: 40 },
                xaxis: { title: 'Total Revenue ($)' },
                yaxis: { title: 'Margin %' }
            }, { responsive: true, displayModeBar: false });

            // 10. Discount Erosion Bar
            Plotly.newPlot('chart-discount-erosion', [{
                x: data.discount_erosion.brackets,
                y: data.discount_erosion.margins,
                type: 'bar',
                marker: { color: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'] }
            }], {
                margin: { t: 10, r: 20, l: 40, b: 40 },
                yaxis: { title: 'Realized Margin %' }
            }, { responsive: true, displayModeBar: false });

            // 11. Loss SKUs Table
            const lossTbody = document.getElementById('loss-skus-tbody');
            lossTbody.innerHTML = '';
            data.loss_skus.forEach(p => {
                lossTbody.innerHTML += `
                    <tr class="hover:bg-slate-50">
                        <td class="py-2.5 px-3 font-medium text-slate-900">${p.product_name}</td>
                        <td class="py-2.5 px-3">${p.category}</td>
                        <td class="py-2.5 px-3">${p.sub_category}</td>
                        <td class="py-2.5 px-3">$${p.revenue.toLocaleString()}</td>
                        <td class="py-2.5 px-3 font-semibold text-red-600">-$${Math.abs(p.profit).toLocaleString()}</td>
                        <td class="py-2.5 px-3 font-semibold text-red-600">${p.margin.toFixed(1)}%</td>
                        <td class="py-2.5 px-3">${p.discount.toFixed(1)}%</td>
                    </tr>
                `;
            });

            // 12. Shipping Performance
            Plotly.newPlot('chart-shipping-perf', [{
                x: data.shipping_perf.modes,
                y: data.shipping_perf.delivery_days,
                type: 'bar',
                marker: { color: '#8b5cf6' }
            }], {
                margin: { t: 10, r: 20, l: 40, b: 40 },
                yaxis: { title: 'Avg Delivery Days' }
            }, { responsive: true, displayModeBar: false });

            // 13. Return Rates by Sub-Cat
            Plotly.newPlot('chart-return-rates', [{
                x: data.return_rates.rates,
                y: data.return_rates.subcats,
                type: 'bar',
                orientation: 'h',
                marker: { color: '#f43f5e' }
            }], {
                margin: { t: 10, r: 20, l: 100, b: 40 },
                xaxis: { title: 'Return Rate %' }
            }, { responsive: true, displayModeBar: false });
        }

        // Initialize dashboard on page load
        window.addEventListener('DOMContentLoaded', updateDashboard);
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/data")
def api_data():
    year_filter = request.args.get("year", "All")
    region_filter = request.args.get("region", "All")
    segment_filter = request.args.get("segment", "All")

    conn = get_db_connection()
    
    # Build filter clauses
    where_clauses = []
    params = []
    if year_filter != "All":
        where_clauses.append("d.year = ?")
        params.append(int(year_filter))
    if region_filter != "All":
        where_clauses.append("l.region = ?")
        params.append(region_filter)
    if segment_filter != "All":
        where_clauses.append("c.customer_segment = ?")
        params.append(segment_filter)

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql

    # 1. Summary KPIs
    kpi_query = f"""
    SELECT 
        COALESCE(SUM(f.net_sales), 0) AS total_revenue,
        COALESCE(SUM(f.profit), 0) AS total_profit,
        COUNT(DISTINCT f.order_id) AS total_orders,
        COUNT(DISTINCT f.customer_id) AS total_customers
    FROM fact_sales f
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql};
    """
    kpi_res = conn.execute(kpi_query, params).fetchone()
    rev = float(kpi_res["total_revenue"])
    prof = float(kpi_res["total_profit"])
    orders = int(kpi_res["total_orders"])
    margin = (prof / rev * 100) if rev > 0 else 0.0
    aov = (rev / orders) if orders > 0 else 0.0

    # 2. Monthly Trend
    monthly_query = f"""
    SELECT 
        d.year || '-' || SUBSTR('0' || d.month, -2, 2) AS yr_mo,
        SUM(f.net_sales) AS revenue,
        SUM(f.profit) AS profit
    FROM fact_sales f
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY yr_mo
    ORDER BY yr_mo;
    """
    m_rows = conn.execute(monthly_query, params).fetchall()
    monthly_dates = [r["yr_mo"] for r in m_rows]
    monthly_rev = [round(float(r["revenue"]), 2) for r in m_rows]
    monthly_margin = [round((float(r["profit"]) / float(r["revenue"]) * 100) if float(r["revenue"]) > 0 else 0.0, 2) for r in m_rows]

    # 3. Category Performance
    cat_query = f"""
    SELECT 
        p.category,
        SUM(f.net_sales) AS revenue,
        SUM(f.profit) AS profit
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY p.category
    ORDER BY revenue ASC;
    """
    cat_rows = conn.execute(cat_query, params).fetchall()
    cats = [r["category"] for r in cat_rows]
    cat_rev = [round(float(r["revenue"]), 2) for r in cat_rows]

    # 4. Segment Performance
    seg_query = f"""
    SELECT 
        c.customer_segment,
        SUM(f.net_sales) AS revenue
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    {where_sql}
    GROUP BY c.customer_segment;
    """
    seg_rows = conn.execute(seg_query, params).fetchall()
    segments = [r["customer_segment"] for r in seg_rows]
    seg_rev = [round(float(r["revenue"]), 2) for r in seg_rows]

    # 5. Regional Performance
    reg_query = f"""
    SELECT 
        l.region,
        SUM(f.net_sales) AS revenue
    FROM fact_sales f
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY l.region
    ORDER BY revenue DESC;
    """
    reg_rows = conn.execute(reg_query, params).fetchall()
    regions = [r["region"] for r in reg_rows]
    reg_rev = [round(float(r["revenue"]), 2) for r in reg_rows]

    # 6. Top Sub-Categories
    subcat_query = f"""
    SELECT 
        p.sub_category,
        SUM(f.net_sales) AS revenue
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY p.sub_category
    ORDER BY revenue ASC
    LIMIT 15;
    """
    sub_rows = conn.execute(subcat_query, params).fetchall()
    subcats = [r["sub_category"] for r in sub_rows]
    sub_rev = [round(float(r["revenue"]), 2) for r in sub_rows]

    # 7. Seasonality Grid
    season_query = f"""
    SELECT 
        d.year,
        d.month,
        SUM(f.net_sales) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY d.year, d.month;
    """
    s_rows = conn.execute(season_query, params).fetchall()
    years = [2022, 2023, 2024, 2025] if year_filter == "All" else [int(year_filter)]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    z_matrix = [[0 for _ in years] for _ in months]
    for r in s_rows:
        y_idx = years.index(int(r["year"])) if int(r["year"]) in years else -1
        m_idx = int(r["month"]) - 1
        if y_idx != -1 and 0 <= m_idx < 12:
            z_matrix[m_idx][y_idx] = round(float(r["revenue"]) / 1e3, 1)

    # 8. RFM Summary
    rfm_query = """
    SELECT 
        customer_segment_rfm,
        COUNT(customer_id) AS cust_count,
        SUM(monetary) AS total_revenue
    FROM rfm_customer_segments
    GROUP BY customer_segment_rfm
    ORDER BY total_revenue ASC;
    """
    rfm_rows = conn.execute(rfm_query).fetchall()
    rfm_segs = [r["customer_segment_rfm"] for r in rfm_rows]
    rfm_counts = [int(r["cust_count"]) for r in rfm_rows]
    rfm_rev = [round(float(r["total_revenue"]), 2) for r in rfm_rows]

    # 9. Top Customers Table
    top_cust_query = f"""
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_segment AS segment,
        l.city,
        l.state,
        SUM(f.net_sales) AS revenue,
        SUM(f.profit) AS profit,
        (SUM(f.profit) / SUM(f.net_sales)) * 100 AS margin
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_date d ON f.order_date = d.date_key
    {where_sql}
    GROUP BY c.customer_id, c.customer_name, c.customer_segment, l.city, l.state
    ORDER BY revenue DESC
    LIMIT 10;
    """
    top_cust_rows = conn.execute(top_cust_query, params).fetchall()
    top_customers = [
        {
            "customer_id": r["customer_id"],
            "customer_name": r["customer_name"],
            "segment": r["segment"],
            "city": r["city"],
            "state": r["state"],
            "revenue": round(float(r["revenue"]), 2),
            "profit": round(float(r["profit"]), 2),
            "margin": round(float(r["margin"]), 2)
        } for r in top_cust_rows
    ]

    # 10. Scatter Plot (Product Revenue vs Margin)
    scatter_query = f"""
    SELECT 
        p.product_name,
        SUM(f.net_sales) AS revenue,
        (SUM(f.profit) / SUM(f.net_sales)) * 100 AS margin
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY p.product_id, p.product_name
    LIMIT 200;
    """
    scat_rows = conn.execute(scatter_query, params).fetchall()
    scatter_data = {
        "names": [r["product_name"] for r in scat_rows],
        "revenue": [round(float(r["revenue"]), 2) for r in scat_rows],
        "margin": [round(float(r["margin"]), 2) for r in scat_rows]
    }

    # 11. Discount Margin Erosion
    disc_query = f"""
    SELECT 
        f.discount_bracket,
        (SUM(f.profit) / SUM(f.net_sales)) * 100 AS margin
    FROM fact_sales f
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY f.discount_bracket;
    """
    disc_rows = conn.execute(disc_query, params).fetchall()
    bracket_order = ["None (0%)", "Low (1-15%)", "Medium (16-30%)", "High (31%+)"]
    disc_map = {r["discount_bracket"]: round(float(r["margin"]), 2) for r in disc_rows}
    disc_data = {
        "brackets": bracket_order,
        "margins": [disc_map.get(b, 0.0) for b in bracket_order]
    }

    # 12. Loss-making SKUs
    loss_query = f"""
    SELECT 
        p.product_name,
        p.category,
        p.sub_category,
        SUM(f.net_sales) AS revenue,
        SUM(f.profit) AS profit,
        (SUM(f.profit) / SUM(f.net_sales)) * 100 AS margin,
        AVG(f.discount_rate) * 100 AS avg_discount
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY p.product_id, p.product_name, p.category, p.sub_category
    HAVING profit < 0
    ORDER BY profit ASC
    LIMIT 10;
    """
    loss_rows = conn.execute(loss_query, params).fetchall()
    loss_skus = [
        {
            "product_name": r["product_name"],
            "category": r["category"],
            "sub_category": r["sub_category"],
            "revenue": round(float(r["revenue"]), 2),
            "profit": round(float(r["profit"]), 2),
            "margin": round(float(r["margin"]), 2),
            "discount": round(float(r["avg_discount"]), 2)
        } for r in loss_rows
    ]

    # 13. Shipping Performance
    ship_query = f"""
    SELECT 
        f.ship_mode,
        AVG(f.shipping_duration_days) AS avg_days
    FROM fact_sales f
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY f.ship_mode;
    """
    ship_rows = conn.execute(ship_query, params).fetchall()
    ship_data = {
        "modes": [r["ship_mode"] for r in ship_rows],
        "delivery_days": [round(float(r["avg_days"]), 1) for r in ship_rows]
    }

    # 14. Return Rates by Subcategory
    ret_query = f"""
    SELECT 
        p.sub_category,
        (CAST(SUM(f.return_flag) AS REAL) / COUNT(*)) * 100 AS return_rate
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_date d ON f.order_date = d.date_key
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    {where_sql}
    GROUP BY p.sub_category
    ORDER BY return_rate ASC;
    """
    ret_rows = conn.execute(ret_query, params).fetchall()
    ret_data = {
        "subcats": [r["sub_category"] for r in ret_rows],
        "rates": [round(float(r["return_rate"]), 2) for r in ret_rows]
    }

    conn.close()

    return jsonify({
        "kpis": {
            "revenue": rev,
            "profit": prof,
            "margin": margin,
            "orders": orders,
            "aov": aov
        },
        "monthly_trend": {
            "dates": monthly_dates,
            "revenue": monthly_rev,
            "margin": monthly_margin
        },
        "category_perf": {
            "categories": cats,
            "revenue": cat_rev
        },
        "segment_perf": {
            "segments": segments,
            "revenue": seg_rev
        },
        "regional_perf": {
            "regions": regions,
            "revenue": reg_rev
        },
        "subcat_perf": {
            "subcats": subcats,
            "revenue": sub_rev
        },
        "seasonality": {
            "years": years,
            "months": months,
            "z": z_matrix
        },
        "rfm": {
            "segments": rfm_segs,
            "counts": rfm_counts,
            "revenue": rfm_rev
        },
        "top_customers": top_customers,
        "scatter": scatter_data,
        "discount_erosion": disc_data,
        "loss_skus": loss_skus,
        "shipping_perf": ship_data,
        "return_rates": ret_data
    })

if __name__ == "__main__":
    port = 5050
    print(f"\n=======================================================")
    print(f"  Starting E-Commerce Analytics Web Dashboard...")
    print(f"  Access URL: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
