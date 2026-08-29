import pandas as pd
import json
import random
from datetime import datetime, timedelta
import os
import uuid

# Configuration
DAYS_TO_SIMULATE = 180
START_DATE = datetime.now() - timedelta(days=DAYS_TO_SIMULATE)

def load_config():
    with open('config/business_rules.json', 'r') as f:
        return json.load(f)

def generate_data():
    config = load_config()
    products = config['products']
    materials = config['raw_materials']
    
    # Initialize basic entities
    customers = [
        {"customer_id": f"CUST-{i:03d}", "customer_name": f"Customer {i}", "customer_type": random.choice(["Retail", "Hotel", "Direct"]), "location": "Kopargaon", "payment_terms": "Net 15"} for i in range(1, 21)
    ]
    suppliers = [
        {"supplier_id": f"SUP-{i:03d}", "supplier_name": f"Supplier {i}", "location": "Kopargaon", "typical_lead_time_days": config['lead_times']['supplier_default_days'], "historical_reliability": random.uniform(0.8, 1.0)} for i in range(1, 6)
    ]

    # Generate historical data structure
    sales = []
    purchases = []
    production = []
    inventory_transactions = []
    orders = []
    expenses = []

    inventory = {
        "MAT-RMLK": 0,
        "PRD-MLK": 0,
        "PRD-CRD": 0,
        "PRD-PNR": 0,
        "PRD-BMLK": 0
    }

    current_date = START_DATE
    milk_price = materials['Raw Milk']['baseline_procurement_price']
    
    for day in range(DAYS_TO_SIMULATE):
        date_str = current_date.strftime('%Y-%m-%d')
        is_weekend = current_date.weekday() >= 5
        
        # 1. Price Fluctuation (gradual)
        milk_price += random.uniform(-0.5, 0.5)
        milk_price = max(40, min(50, milk_price)) # Keep between 40 and 50

        # 2. Purchase Milk (Targeting inventory based on recent demand + safety stock)
        target_milk = 1500 if is_weekend else 1200
        qty_to_buy = max(0, target_milk - inventory["MAT-RMLK"])
        
        if qty_to_buy > 0:
            supplier = random.choice(suppliers)
            purchase_id = f"PUR-{day:04d}"
            purchases.append({
                "purchase_id": purchase_id,
                "date": date_str,
                "supplier_id": supplier["supplier_id"],
                "material_id": "MAT-RMLK",
                "quantity": qty_to_buy,
                "unit_price": round(milk_price, 2),
                "total_amount": round(qty_to_buy * milk_price, 2),
                "expected_delivery_date": date_str,
                "actual_delivery_date": date_str,
                "payment_status": "Paid"
            })
            inventory["MAT-RMLK"] += qty_to_buy
            inventory_transactions.append({
                "transaction_id": f"TXN-P-{day:04d}",
                "date": date_str,
                "item_type": "Material",
                "item_id": "MAT-RMLK",
                "transaction_type": "In",
                "quantity": qty_to_buy,
                "source_type": "Purchase",
                "source_id": purchase_id
            })

        # 3. Production
        # Try to produce according to capacity and available milk
        for prod_name, prod_details in products.items():
            target_production = prod_details['production_capacity_per_day'] * (1.2 if is_weekend and prod_name in ["Paneer", "Curd"] else 1.0)
            target_production = int(target_production)
            
            milk_needed = target_production * prod_details['conversion_ratio']
            
            if inventory["MAT-RMLK"] >= milk_needed:
                actual_production = target_production
                actual_milk_used = milk_needed
            else:
                # Produce what we can
                actual_production = int(inventory["MAT-RMLK"] / prod_details['conversion_ratio'])
                actual_milk_used = actual_production * prod_details['conversion_ratio']

            if actual_production > 0:
                prod_id = f"PROD-{day:04d}-{prod_details['id']}"
                wastage = actual_production * (prod_details['wastage_percent'] / 100)
                net_production = actual_production - wastage

                production.append({
                    "production_id": prod_id,
                    "date": date_str,
                    "product_id": prod_details['id'],
                    "quantity_produced": round(net_production, 2),
                    "raw_material_used": round(actual_milk_used, 2),
                    "production_hours": 4,
                    "production_status": "Completed",
                    "wastage_quantity": round(wastage, 2)
                })
                
                # Update Inventory
                inventory["MAT-RMLK"] -= actual_milk_used
                inventory_transactions.append({
                    "transaction_id": f"TXN-M-OUT-{day:04d}-{prod_details['id']}",
                    "date": date_str,
                    "item_type": "Material",
                    "item_id": "MAT-RMLK",
                    "transaction_type": "Out",
                    "quantity": actual_milk_used,
                    "source_type": "Production",
                    "source_id": prod_id
                })

                inventory[prod_details['id']] += net_production
                inventory_transactions.append({
                    "transaction_id": f"TXN-P-IN-{day:04d}-{prod_details['id']}",
                    "date": date_str,
                    "item_type": "Product",
                    "item_id": prod_details['id'],
                    "transaction_type": "In",
                    "quantity": net_production,
                    "source_type": "Production",
                    "source_id": prod_id
                })

        # 4. Sales & Orders
        num_sales = random.randint(10, 30)
        for s in range(num_sales):
            customer = random.choice(customers)
            prod_name = random.choice(list(products.keys()))
            prod_details = products[prod_name]
            
            qty = random.randint(1, 20)
            
            if inventory[prod_details['id']] >= qty:
                sale_id = f"SALE-{day:04d}-{s:03d}"
                amount = qty * prod_details['selling_price_per_unit']
                
                sales.append({
                    "sale_id": sale_id,
                    "date": date_str,
                    "customer_id": customer['customer_id'],
                    "product_id": prod_details['id'],
                    "quantity": qty,
                    "unit_price": prod_details['selling_price_per_unit'],
                    "total_amount": amount,
                    "payment_status": "Paid"
                })

                inventory[prod_details['id']] -= qty
                inventory_transactions.append({
                    "transaction_id": f"TXN-S-OUT-{day:04d}-{s:03d}",
                    "date": date_str,
                    "item_type": "Product",
                    "item_id": prod_details['id'],
                    "transaction_type": "Out",
                    "quantity": qty,
                    "source_type": "Sale",
                    "source_id": sale_id
                })
        
        # 5. Expenses
        expenses.append({
            "expense_id": f"EXP-{day:04d}-1",
            "date": date_str,
            "expense_category": "Electricity",
            "amount": random.uniform(500, 1000),
            "description": "Daily power usage"
        })

        current_date += timedelta(days=1)

    # Save to files
    os.makedirs('data/raw', exist_ok=True)
    pd.DataFrame(customers).to_csv('data/raw/customers.csv', index=False)
    pd.DataFrame(suppliers).to_csv('data/raw/suppliers.csv', index=False)
    
    prod_df = pd.DataFrame([{"product_id": v['id'], "product_name": k, "unit": v['unit'], "standard_selling_price": v['selling_price_per_unit'], "production_capacity_per_day": v['production_capacity_per_day']} for k, v in products.items()])
    prod_df.to_csv('data/raw/products.csv', index=False)
    
    mat_df = pd.DataFrame([{"material_id": v['id'], "material_name": k, "unit": v['unit'], "reorder_level": 500, "safety_stock": 200, "typical_lead_time_days": 1} for k, v in materials.items()])
    mat_df.to_csv('data/raw/materials.csv', index=False)

    pd.DataFrame(sales).to_csv('data/raw/sales.csv', index=False)
    pd.DataFrame(purchases).to_csv('data/raw/purchases.csv', index=False)
    pd.DataFrame(production).to_csv('data/raw/production.csv', index=False)
    pd.DataFrame(inventory_transactions).to_csv('data/raw/inventory_transactions.csv', index=False)
    pd.DataFrame(orders).to_csv('data/raw/orders.csv', index=False)
    pd.DataFrame(expenses).to_csv('data/raw/expenses.csv', index=False)

if __name__ == "__main__":
    generate_data()
    print("Data generation complete.")
