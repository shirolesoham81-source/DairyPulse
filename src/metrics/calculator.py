import pandas as pd

def calculate_inventory_days(inventory_qty, average_daily_sales):
    if average_daily_sales == 0:
        return 0
    return inventory_qty / average_daily_sales

def calculate_wastage_rate(wastage_qty, total_production):
    if total_production == 0:
        return 0
    return wastage_qty / total_production

def get_kpis(snapshot_df):
    total_sales = snapshot_df['total_sales'].sum()
    avg_procurement_cost = snapshot_df['milk_purchase_price'].mean()
    total_wastage = snapshot_df['wastage'].sum()
    total_production = snapshot_df['total_production'].sum()
    
    return {
        "Total Sales": total_sales,
        "Average Milk Price": avg_procurement_cost,
        "Wastage Rate": calculate_wastage_rate(total_wastage, total_production)
    }
