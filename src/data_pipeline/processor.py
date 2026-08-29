import pandas as pd
import os

def process_data():
    os.makedirs('data/processed', exist_ok=True)
    
    # Just copying over as "clean" for this basic demo setup, would apply filters in real life
    sales = pd.read_csv('data/raw/sales.csv')
    sales.to_csv('data/processed/clean_sales.csv', index=False)
    
    purchases = pd.read_csv('data/raw/purchases.csv')
    purchases.to_csv('data/processed/clean_purchases.csv', index=False)
    
    production = pd.read_csv('data/raw/production.csv')
    production.to_csv('data/processed/clean_production.csv', index=False)

    inventory = pd.read_csv('data/raw/inventory_transactions.csv')
    inventory.to_csv('data/processed/clean_inventory.csv', index=False)
    
    expenses = pd.read_csv('data/raw/expenses.csv')
    expenses.to_csv('data/processed/clean_expenses.csv', index=False)
    
    # Create daily snapshot
    snapshot = pd.DataFrame()
    
    sales['date'] = pd.to_datetime(sales['date'])
    daily_sales = sales.groupby('date').agg({'total_amount': 'sum', 'quantity': 'sum'}).rename(columns={'total_amount': 'total_sales', 'quantity': 'total_units_sold'})
    
    purchases['date'] = pd.to_datetime(purchases['date'])
    daily_purchases = purchases.groupby('date').agg({'quantity': 'sum', 'unit_price': 'mean'}).rename(columns={'quantity': 'milk_purchased', 'unit_price': 'milk_purchase_price'})

    production['date'] = pd.to_datetime(production['date'])
    daily_production = production.groupby('date').agg({'quantity_produced': 'sum', 'raw_material_used': 'sum', 'wastage_quantity': 'sum'}).rename(columns={'quantity_produced': 'total_production', 'raw_material_used': 'milk_used', 'wastage_quantity': 'wastage'})
    
    snapshot = pd.concat([daily_sales, daily_purchases, daily_production], axis=1).fillna(0)
    snapshot.reset_index(inplace=True)
    snapshot.to_csv('data/processed/daily_business_snapshot.csv', index=False)
    
if __name__ == "__main__":
    process_data()
    print("Processing complete.")
