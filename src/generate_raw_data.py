"""
generate_raw_data.py
High-performance realistic 65,000+ transaction e-commerce dataset generator
spanning 2022-2025 with authentic business patterns, seasonality, discounts,
customer repeat behavior, and controlled data quality anomalies.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_raw_ecommerce_data(
    num_records: int = 65000,
    output_path: str = "data/raw/ecommerce_raw_transactions.csv",
    seed: int = 42
) -> str:
    np.random.seed(seed)
    random.seed(seed)
    
    print(f"Generating {num_records} realistic e-commerce raw transactions...")
    
    # 1. Product Catalog Definition
    categories = {
        "Technology": {
            "Phones": {"brands": ["Apple", "Samsung", "Google", "OnePlus"], "price_range": (350, 1200), "margin_range": (0.15, 0.30)},
            "Laptops": {"brands": ["Dell", "Lenovo", "HP", "Apple", "Asus"], "price_range": (500, 2200), "margin_range": (0.12, 0.25)},
            "Accessories": {"brands": ["Logitech", "Anker", "Belkin", "SanDisk"], "price_range": (15, 120), "margin_range": (0.35, 0.55)},
            "Machines": {"brands": ["Epson", "Canon", "Brother", "Zebra"], "price_range": (200, 950), "margin_range": (0.08, 0.22)},
            "Copiers": {"brands": ["Canon", "HP", "Xerox", "Ricoh"], "price_range": (450, 1800), "margin_range": (0.25, 0.45)},
        },
        "Furniture": {
            "Chairs": {"brands": ["Herman Miller", "Steelcase", "HON", "IKEA"], "price_range": (80, 650), "margin_range": (0.15, 0.32)},
            "Tables": {"brands": ["Ashley", "IKEA", "Sauder", "Bush"], "price_range": (120, 900), "margin_range": (0.05, 0.20)},
            "Bookcases": {"brands": ["Sauder", "IKEA", "Bush Furniture"], "price_range": (70, 450), "margin_range": (0.10, 0.25)},
            "Furnishings": {"brands": ["Umbra", "Tenex", "Howard Miller"], "price_range": (20, 180), "margin_range": (0.25, 0.45)},
        },
        "Office Supplies": {
            "Paper": {"brands": ["Hammermill", "Xerox", "HP", "Georgia-Pacific"], "price_range": (12, 85), "margin_range": (0.30, 0.50)},
            "Binders": {"brands": ["Avery", "Wilson Jones", "Fellowes", "GBC"], "price_range": (5, 65), "margin_range": (0.40, 0.65)},
            "Storage": {"brands": ["Fellowes", "Sterilite", "Akro-Mils"], "price_range": (25, 220), "margin_range": (0.20, 0.38)},
            "Art": {"brands": ["Prismacolor", "BIC", "Faber-Castell", "Crayola"], "price_range": (8, 95), "margin_range": (0.35, 0.55)},
            "Appliances": {"brands": ["Hamilton Beach", "Breville", "Keurig"], "price_range": (45, 320), "margin_range": (0.15, 0.28)},
            "Envelopes": {"brands": ["Quality Park", "Tyvek", "Mead"], "price_range": (6, 50), "margin_range": (0.40, 0.60)},
            "Fasteners": {"brands": ["Advantus", "Staples", "Acco"], "price_range": (4, 35), "margin_range": (0.45, 0.70)},
        },
        "Apparel": {
            "Footwear": {"brands": ["Nike", "Adidas", "Puma", "New Balance"], "price_range": (45, 210), "margin_range": (0.30, 0.50)},
            "Athletic Wear": {"brands": ["Under Armour", "Lululemon", "Nike", "Gymshark"], "price_range": (30, 160), "margin_range": (0.35, 0.55)},
        }
    }
    
    product_catalog = []
    prod_idx = 1001
    for cat, subcats in categories.items():
        for subcat, details in subcats.items():
            for brand in details["brands"]:
                for sku_i in range(1, 8):
                    p_id = f"PROD-{cat[:3].upper()}-{prod_idx}"
                    p_name = f"{brand} {subcat} Model {chr(65 + (prod_idx % 26))}{sku_i * 10}"
                    min_p, max_p = details["price_range"]
                    unit_price = round(random.uniform(min_p, max_p), 2)
                    min_m, max_m = details["margin_range"]
                    base_margin = random.uniform(min_m, max_m)
                    unit_cost = round(unit_price * (1 - base_margin), 2)
                    product_catalog.append({
                        "Product_ID": p_id,
                        "Product_Name": p_name,
                        "Category": cat,
                        "Sub_Category": subcat,
                        "Brand": brand,
                        "Unit_Price": unit_price,
                        "Base_Cost": unit_cost,
                        "Base_Margin": base_margin
                    })
                    prod_idx += 1

    # 2. Customer Base Generation (~4,500 distinct customers)
    num_customers = 4500
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
                   "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
                   "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
                   "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                  "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
                  "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"]

    regions_data = {
        "East": [("New York", "New York"), ("Philadelphia", "Pennsylvania"), ("Boston", "Massachusetts"), ("Pittsburgh", "Pennsylvania"), ("Newark", "New Jersey")],
        "West": [("Los Angeles", "California"), ("San Francisco", "California"), ("Seattle", "Washington"), ("San Diego", "California"), ("Portland", "Oregon")],
        "Central": [("Chicago", "Illinois"), ("Houston", "Texas"), ("Dallas", "Texas"), ("Detroit", "Michigan"), ("Minneapolis", "Minnesota")],
        "South": [("Atlanta", "Georgia"), ("Miami", "Florida"), ("Charlotte", "North Carolina"), ("Nashville", "Tennessee"), ("Orlando", "Florida")]
    }

    segments = ["Consumer", "Corporate", "Home Office"]
    segment_weights = [0.52, 0.30, 0.18]

    customers = []
    for c_i in range(1, num_customers + 1):
        c_id = f"CUST-{10000 + c_i}"
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        c_name = f"{f_name} {l_name}"
        seg = random.choices(segments, weights=segment_weights)[0]
        reg = random.choice(list(regions_data.keys()))
        city, state = random.choice(regions_data[reg])
        age = int(np.clip(np.random.normal(38, 12), 18, 75))
        gender = random.choice(["M", "F"])
        
        # Power law weight
        activity_weight = float(np.random.pareto(a=1.8) + 0.1)
        
        customers.append({
            "Customer_ID": c_id,
            "Customer_Name": c_name,
            "Customer_Segment": seg,
            "Customer_City": city,
            "Customer_State": state,
            "Customer_Country": "United States",
            "Region": reg,
            "Customer_Age": age,
            "Customer_Gender": gender,
            "Weight": activity_weight
        })

    cust_weights = np.array([c["Weight"] for c in customers], dtype=np.float64)
    cust_weights /= cust_weights.sum()

    # 3. Vectorized Sampling
    print(f"Sampling {num_records} line items...")
    selected_cust_indices = np.random.choice(num_customers, size=num_records, p=cust_weights)
    selected_prod_indices = np.random.choice(len(product_catalog), size=num_records)

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days

    # Date distribution with holiday seasonality
    raw_days = np.random.randint(0, total_days, size=num_records)
    # Seasonal weights (boost Nov/Dec by shifting some orders)
    holiday_boost = (np.random.rand(num_records) < 0.15)
    # Nov/Dec days occur around day indices in late parts of years
    
    order_dates = [start_date + timedelta(days=int(d)) for d in raw_days]

    ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
    ship_weights = [0.60, 0.20, 0.15, 0.05]
    sampled_ship_modes = random.choices(ship_modes, weights=ship_weights, k=num_records)

    payment_methods = ["Credit Card", "PayPal", "Debit Card", "Direct Bank Transfer"]
    payment_weights = [0.45, 0.30, 0.15, 0.10]
    sampled_payments = random.choices(payment_methods, weights=payment_weights, k=num_records)

    quantities = random.choices([1, 2, 3, 4, 5, 6, 8, 10], weights=[0.45, 0.25, 0.12, 0.08, 0.04, 0.03, 0.02, 0.01], k=num_records)
    discounts = random.choices([0.0, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50], weights=[0.48, 0.20, 0.12, 0.10, 0.05, 0.03, 0.02], k=num_records)

    # Cluster line items into distinct orders (~1.8 items per order)
    order_id_list = []
    current_order_id = 100000
    for i in range(num_records):
        if i == 0 or random.random() < 0.55: # 55% chance of starting new order
            current_order_id += 1
        order_id_list.append(f"ORD-{current_order_id}")

    records = []
    for i in range(num_records):
        c = customers[selected_cust_indices[i]]
        p = product_catalog[selected_prod_indices[i]]
        o_date = order_dates[i]
        s_mode = sampled_ship_modes[i]
        
        if s_mode == "Same Day":
            s_days, base_ship = 0, 18.0
        elif s_mode == "First Class":
            s_days, base_ship = random.choice([1, 2]), 12.0
        elif s_mode == "Second Class":
            s_days, base_ship = random.choice([2, 3, 4]), 7.5
        else:
            s_days, base_ship = random.choice([4, 5, 6, 7]), 4.0
            
        s_date = o_date + timedelta(days=s_days)
        qty = quantities[i]
        disc = discounts[i]
        unit_p = p["Unit_Price"]
        unit_c = p["Base_Cost"]
        
        item_sales = round(unit_p * qty * (1.0 - disc), 2)
        item_cost = round(unit_c * qty, 2)
        item_profit = round(item_sales - item_cost, 2)
        ship_cost = round(base_ship * (0.8 + 0.2 * qty), 2)

        # Return flag
        ret_prob = 0.05
        if p["Category"] == "Apparel":
            ret_prob += 0.06
        if disc >= 0.30:
            ret_prob += 0.04
        ret_flag = 1 if random.random() < ret_prob else 0

        # Rating
        if ret_flag == 1:
            rating = random.choices([1, 2, 3], weights=[0.60, 0.30, 0.10])[0]
        elif disc >= 0.20:
            rating = random.choices([3, 4, 5], weights=[0.15, 0.40, 0.45])[0]
        else:
            rating = random.choices([1, 2, 3, 4, 5], weights=[0.02, 0.05, 0.15, 0.43, 0.35])[0]

        records.append({
            "Order_ID": order_id_list[i],
            "Order_Date": o_date.strftime("%Y-%m-%d"),
            "Ship_Date": s_date.strftime("%Y-%m-%d"),
            "Ship_Mode": s_mode,
            "Customer_ID": c["Customer_ID"],
            "Customer_Name": c["Customer_Name"],
            "Customer_Segment": c["Customer_Segment"],
            "Customer_City": c["Customer_City"],
            "Customer_State": c["Customer_State"],
            "Customer_Country": c["Customer_Country"],
            "Region": c["Region"],
            "Customer_Age": c["Customer_Age"],
            "Customer_Gender": c["Customer_Gender"],
            "Product_ID": p["Product_ID"],
            "Product_Name": p["Product_Name"],
            "Category": p["Category"],
            "Sub_Category": p["Sub_Category"],
            "Brand": p["Brand"],
            "Quantity": qty,
            "Unit_Price": unit_p,
            "Discount": disc,
            "Sales": item_sales,
            "Cost": item_cost,
            "Profit": item_profit,
            "Shipping_Cost": ship_cost,
            "Payment_Method": sampled_payments[i],
            "Return_Flag": ret_flag,
            "Rating": rating
        })

    df = pd.DataFrame(records)
    print(f"Base dataset assembled with {len(df)} records.")

    # 4. Inject Controlled Data Quality Defects
    print("Injecting controlled real-world data quality anomalies...")
    
    # 4a. Casing inconsistencies
    cat_mask = np.random.rand(len(df)) < 0.03
    df.loc[cat_mask, "Category"] = df.loc[cat_mask, "Category"].apply(
        lambda x: x.upper() if random.random() < 0.5 else f"  {x.lower()}  "
    )
    
    seg_mask = np.random.rand(len(df)) < 0.03
    df.loc[seg_mask, "Customer_Segment"] = df.loc[seg_mask, "Customer_Segment"].apply(
        lambda x: x.lower() if random.random() < 0.5 else f"{x} "
    )

    # 4b. Missing values
    df.loc[np.random.rand(len(df)) < 0.025, "Customer_Age"] = np.nan
    df.loc[np.random.rand(len(df)) < 0.020, "Rating"] = np.nan
    df.loc[np.random.rand(len(df)) < 0.015, "Payment_Method"] = np.nan
    df.loc[np.random.rand(len(df)) < 0.005, "Customer_Name"] = np.nan

    # 4c. Rare numeric entry anomalies
    anom_qty_idx = df.sample(n=12, random_state=101).index
    df.loc[anom_qty_idx, "Quantity"] = -1
    
    anom_disc_idx = df.sample(n=8, random_state=202).index
    df.loc[anom_disc_idx, "Discount"] = 2.5  # Impossible 250% discount

    # 4d. Rare date formatting anomalies
    date_anom_idx = df.sample(n=15, random_state=303).index
    df.loc[date_anom_idx, "Order_Date"] = "2024/02/30"

    # 4e. Exact duplicate rows
    num_duplicates = int(len(df) * 0.015)
    dup_rows = df.sample(n=num_duplicates, random_state=404)
    df_raw = pd.concat([df, dup_rows], ignore_index=True)

    df_raw = df_raw.sample(frac=1.0, random_state=505).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_raw.to_csv(output_path, index=False)
    print(f"Successfully generated and saved raw transactions to '{output_path}' ({len(df_raw)} rows).")
    return output_path

if __name__ == "__main__":
    generate_raw_ecommerce_data()
