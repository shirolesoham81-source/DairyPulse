import pandas as pd
import os

def validate_data():
    issues = []
    
    # Load data
    sales = pd.read_csv('data/raw/sales.csv')
    inventory = pd.read_csv('data/raw/inventory_transactions.csv')
    
    # 1. Duplicate check
    if sales['sale_id'].duplicated().any():
        issues.append("Duplicate sale_ids found.")
        
    # 2. Negative quantity check
    if (sales['quantity'] < 0).any():
        issues.append("Negative quantities found in sales.")
        
    # 3. Orphan check
    products = pd.read_csv('data/raw/products.csv')
    if not sales['product_id'].isin(products['product_id']).all():
        issues.append("Sales contain unknown product_ids.")
        
    # Validation summary
    total_sales = len(sales)
    
    print(f"Validation complete. Rows: {total_sales}")
    for issue in issues:
        print(f"ISSUE: {issue}")
        
    return issues

if __name__ == "__main__":
    validate_data()
