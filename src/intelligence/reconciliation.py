def reconcile_inventory(opening: float, purchases: float, production: float, 
                        sales: float, wastage: float, expected_closing: float) -> dict:
    
    calculated_closing = opening + purchases + production - sales - wastage
    difference = round(abs(calculated_closing - expected_closing), 2)
    
    if difference > 0.01:
        return {
            "status": "WARNING",
            "message": "INVENTORY RECONCILIATION WARNING",
            "expected_closing": calculated_closing,
            "recorded_closing": expected_closing,
            "difference": difference,
            "recommendation": "Do not silently change historical records. Flag discrepancy."
        }
        
    return {
        "status": "OK",
        "message": "Inventory reconciled.",
        "expected_closing": calculated_closing,
        "recorded_closing": expected_closing,
        "difference": 0.0
    }
