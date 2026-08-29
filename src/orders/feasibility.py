def check_order_feasibility(product_id: str, order_qty: float, selling_price: float, 
                            current_fg_inventory: float, raw_material_inventory: float, 
                            conversion_ratio: float, raw_material_cost_per_unit: float,
                            processing_cost_per_unit: float = 5.0) -> dict:
    
    reasons = []
    decision = "ACCEPT"
    
    # 1. Check FG Inventory
    shortfall = max(0, order_qty - current_fg_inventory)
    if shortfall > 0:
        reasons.append(f"Insufficient finished goods. Production required: {shortfall} units.")
        decision = "ACCEPT_WITH_CONDITIONS"
    else:
        reasons.append("Sufficient finished goods inventory available.")
        shortfall = 0
        
    # 2. Check Raw Material for shortfall
    rm_required = shortfall * conversion_ratio
    rm_shortfall = max(0, rm_required - raw_material_inventory)
    
    if rm_shortfall > 0:
        reasons.append(f"Insufficient raw material. Procurement required: {rm_shortfall} units.")
        decision = "ACCEPT_WITH_CONDITIONS"
        delivery_risk = "HIGH" if rm_shortfall > (raw_material_inventory * 0.5) else "MEDIUM"
    else:
        delivery_risk = "LOW"
        
    # 3. Economics
    estimated_rm_cost = order_qty * conversion_ratio * raw_material_cost_per_unit
    estimated_proc_cost = order_qty * processing_cost_per_unit
    estimated_total_cost = estimated_rm_cost + estimated_proc_cost
    
    estimated_revenue = order_qty * selling_price
    estimated_margin = estimated_revenue - estimated_total_cost
    
    if estimated_margin <= 0:
        decision = "HIGH_RISK"
        reasons.append("Estimated margin is negative.")
    else:
        reasons.append("Expected margin is positive.")
        
    return {
        "decision": decision,
        "required_raw_material": rm_required,
        "procurement_quantity_needed": rm_shortfall,
        "estimated_cost": estimated_total_cost,
        "estimated_revenue": estimated_revenue,
        "estimated_margin": estimated_margin,
        "delivery_risk": delivery_risk,
        "recommendation": decision,
        "reasons": reasons
    }
