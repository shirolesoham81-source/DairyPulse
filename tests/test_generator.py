import pytest
import pandas as pd
import json

def test_business_rules_exist():
    with open('config/business_rules.json', 'r') as f:
        rules = json.load(f)
    assert 'products' in rules
    assert 'raw_materials' in rules

def test_inventory_balance():
    # If data generated, read and check
    try:
        inventory = pd.read_csv('data/raw/inventory_transactions.csv')
        assert (inventory['quantity'] >= 0).all(), "Negative quantities found in transactions"
    except FileNotFoundError:
        pytest.skip("Data not generated yet")

def test_sales_positive():
    try:
        sales = pd.read_csv('data/raw/sales.csv')
        assert (sales['quantity'] >= 0).all()
        assert (sales['total_amount'] >= 0).all()
    except FileNotFoundError:
        pytest.skip("Data not generated yet")
