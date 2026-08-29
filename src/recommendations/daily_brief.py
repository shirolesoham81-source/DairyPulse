def generate_daily_business_brief(sales_today: float, expected_demand: float, 
                                  inventory_days: float, main_risk_str: str, 
                                  action_rec: str, price_trend: str, pending_orders: int) -> str:
    
    brief = f"""TODAY'S BUSINESS BRIEF

Sales:
₹{sales_today:,.2f}

Expected demand:
{expected_demand} units

Inventory:
{inventory_days} days

Main risk:
{main_risk_str}

Recommended action:
{action_rec}

Important trend:
{price_trend}

Orders:
{pending_orders} pending
"""
    return brief
