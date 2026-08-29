import pandas as pd
import os

class HistoricalImporter:
    def __init__(self):
        self.column_map = {
            "Date": "date",
            "Product": "product_name",
            "Qty Sold": "quantity",
            "Price": "unit_price",
            "Customer": "customer_name"
        }
        
    def import_file(self, filepath):
        print(f"Importing {filepath}...")
        
        # Load file
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            raise ValueError("Unsupported file format")
            
        # Map columns
        df.rename(columns=self.column_map, inplace=True)
        
        # Validate
        issues = []
        if df['quantity'].min() < 0:
            issues.append("Negative quantities found in import.")
            
        if not issues:
            print("Import successful. No major issues detected.")
            return df
        else:
            print("Import failed validation:")
            for i in issues:
                print(i)
            return None

if __name__ == "__main__":
    importer = HistoricalImporter()
    # importer.import_file("data/examples/historical_shop_example.csv")
