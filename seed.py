import os
import uuid
import random
from datetime import datetime, timezone, timedelta, date
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models import Business, User, Product, RawMaterial, Customer, Supplier, InventoryTransaction, ProductRecipe, Invoice, InvoiceItem, Purchase, PurchaseItem, ProductionRecord, Expense

def seed():
    db = SessionLocal()
    # Reset db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # 1. Create Business
    b_id = str(uuid.uuid4())
    b = Business(
        id=b_id,
        business_name="Kopargaon Fresh Dairy",
        legal_name="Kopargaon Fresh Dairy Pvt Ltd",
        location="Kopargaon, Maharashtra",
        district="Ahmednagar",
        state="Maharashtra",
        pincode="423601",
        industry="Dairy Processing",
        enterprise_size="Micro",
        udyam_number="UDYAM-MH-01-1234567",
        contact_information="info@kopargaonfresh.com",
        status="active"
    )
    db.add(b)
    
    # 2. Create Owner User
    u_id = str(uuid.uuid4())
    u = User(
        id=u_id,
        business_id=b_id,
        name="Sunil Patil",
        phone_email="admin@kopargaon.com",
        hashed_password=get_password_hash("password123"),
        role="owner",
        language="Marathi"
    )
    db.add(u)
    
    # 3. Create Products & Raw Materials
    products_def = [
        {"name": "Milk", "unit": "L", "price": 60.0},
        {"name": "Curd", "unit": "kg", "price": 80.0},
        {"name": "Paneer", "unit": "kg", "price": 320.0},
        {"name": "Buttermilk", "unit": "L", "price": 40.0}
    ]
    materials_def = [
        {"name": "Raw Milk", "unit": "L"},
        {"name": "Cream", "unit": "L"},
        {"name": "Packaging", "unit": "pcs"},
        {"name": "Culture", "unit": "g"}
    ]
    
    products = {}
    for pd in products_def:
        p = Product(id=str(uuid.uuid4()), business_id=b_id, name=pd["name"], unit=pd["unit"], selling_price=pd["price"])
        db.add(p)
        products[pd["name"]] = p
        
    materials = {}
    for md in materials_def:
        m = RawMaterial(id=str(uuid.uuid4()), business_id=b_id, name=md["name"], unit=md["unit"])
        db.add(m)
        materials[md["name"]] = m
        
    db.commit()
    
    # 4. Recipes
    # 1 kg Paneer = 8 L Milk
    recipe_paneer = ProductRecipe(
        id=str(uuid.uuid4()), business_id=b_id, product_id=products["Paneer"].id,
        material_id=materials["Raw Milk"].id, quantity_required=8.0, unit="L"
    )
    # 1 kg Curd = 1.05 L Milk
    recipe_curd = ProductRecipe(
        id=str(uuid.uuid4()), business_id=b_id, product_id=products["Curd"].id,
        material_id=materials["Raw Milk"].id, quantity_required=1.05, unit="L"
    )
    db.add_all([recipe_paneer, recipe_curd])
    
    # 5. Partners
    custs = [
        Customer(id=str(uuid.uuid4()), business_id=b_id, name="Sharma Hotel", phone_email="sharma@hotels.com"),
        Customer(id=str(uuid.uuid4()), business_id=b_id, name="Local Retailer A", phone_email="retailerA@dairy.com"),
        Customer(id=str(uuid.uuid4()), business_id=b_id, name="Direct Customer Sunil", phone_email="sunil@patil.com")
    ]
    supps = [
        Supplier(id=str(uuid.uuid4()), business_id=b_id, name="Village Milk Coop Union", contact="9876543210"),
        Supplier(id=str(uuid.uuid4()), business_id=b_id, name="Apex Packaging Ltd", contact="info@apexpack.com")
    ]
    db.add_all(custs + supps)
    db.commit()
    
    # 6. Generate 90 Days of Sales, Procurement, Production, Expenses
    # Start date 90 days ago
    start_date = date.today() - timedelta(days=90)
    
    # Opening Stock
    db.add(InventoryTransaction(
        id=str(uuid.uuid4()), business_id=b_id, item_type="raw_material", item_id=materials["Raw Milk"].id,
        transaction_type="opening_balance", quantity_in=1000.0, quantity_out=0.0, unit="L",
        transaction_date=datetime.combine(start_date - timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc),
        created_by=u_id
    ))
    db.commit()
    
    print("Generating 90 days of synthetic transactional history...")
    
    for i in range(90):
        current_date = start_date + timedelta(days=i)
        dt_utc = datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc)
        
        # 6.1 Procurement (Every 2 days)
        if i % 2 == 0:
            raw_milk_qty = 1000.0 + random.uniform(-100, 200) # Seasonal variation simulation
            price_per_l = 38.0 + random.uniform(-1.0, 1.5)
            purchase_total = raw_milk_qty * price_per_l
            
            p_id = str(uuid.uuid4())
            purchase = Purchase(
                id=p_id, business_id=b_id, supplier_id=supps[0].id,
                purchase_date=current_date, reference_number=f"PO-{current_date.strftime('%Y%m%d')}",
                total_amount=purchase_total, payment_status="paid", lead_time_days=1.0, created_by=u_id,
                created_at=dt_utc
            )
            db.add(purchase)
            db.add(PurchaseItem(
                id=str(uuid.uuid4()), purchase_id=p_id, material_id=materials["Raw Milk"].id,
                quantity=raw_milk_qty, unit="L", unit_price=price_per_l, line_total=purchase_total
            ))
            # Stock IN
            db.add(InventoryTransaction(
                id=str(uuid.uuid4()), business_id=b_id, item_type="raw_material", item_id=materials["Raw Milk"].id,
                transaction_type="purchase", quantity_in=raw_milk_qty, quantity_out=0.0, unit="L",
                reference_type="purchase", reference_id=p_id, transaction_date=dt_utc, created_by=u_id
            ))
            
        # 6.2 Production (Daily curd/paneer)
        paneer_qty = 20.0 + random.uniform(-5, 10)
        curd_qty = 50.0 + random.uniform(-10, 20)
        
        # Record production paneer
        prod_paneer_id = str(uuid.uuid4())
        db.add(ProductionRecord(
            id=prod_paneer_id, business_id=b_id, product_id=products["Paneer"].id,
            date=current_date, quantity_produced=paneer_qty, unit="kg", created_by=u_id, created_at=dt_utc
        ))
        db.add(InventoryTransaction(
            id=str(uuid.uuid4()), business_id=b_id, item_type="product", item_id=products["Paneer"].id,
            transaction_type="production_output", quantity_in=paneer_qty, quantity_out=0.0, unit="kg",
            reference_type="production", reference_id=prod_paneer_id, transaction_date=dt_utc, created_by=u_id
        ))
        # Raw milk consumed for Paneer (8 L per kg)
        db.add(InventoryTransaction(
            id=str(uuid.uuid4()), business_id=b_id, item_type="raw_material", item_id=materials["Raw Milk"].id,
            transaction_type="production_consumption", quantity_in=0.0, quantity_out=paneer_qty * 8.0, unit="L",
            reference_type="production", reference_id=prod_paneer_id, transaction_date=dt_utc, created_by=u_id
        ))
        
        # 6.3 Sales (Daily invoices to customers)
        for c in custs:
            if random.random() > 0.3: # 70% chance daily sale to each customer
                qty_sold = 5.0 + random.uniform(0, 10) if c.name == "Sharma Hotel" else 2.0 + random.uniform(0, 5)
                unit_price = products["Paneer"].selling_price
                line_total = qty_sold * unit_price
                
                inv_id = str(uuid.uuid4())
                invoice = Invoice(
                    id=inv_id, business_id=b_id, invoice_number=f"INV-{current_date.strftime('%Y%m%d')}-{c.name[:3].upper()}",
                    invoice_date=current_date, customer_id=c.id, subtotal=line_total, tax=0.0, total=line_total,
                    payment_status="paid" if random.random() > 0.15 else "pending", payment_method="upi" if random.random() > 0.5 else "bank",
                    created_by=u_id, created_at=dt_utc, updated_at=dt_utc
                )
                db.add(invoice)
                db.add(InvoiceItem(
                    id=str(uuid.uuid4()), invoice_id=inv_id, product_id=products["Paneer"].id,
                    quantity=qty_sold, unit="kg", unit_price=unit_price, line_total=line_total
                ))
                # Stock OUT
                db.add(InventoryTransaction(
                    id=str(uuid.uuid4()), business_id=b_id, item_type="product", item_id=products["Paneer"].id,
                    transaction_type="sale", quantity_in=0.0, quantity_out=qty_sold, unit="kg",
                    reference_type="invoice", reference_id=inv_id, transaction_date=dt_utc, created_by=u_id
                ))
                
        # 6.4 Expenses (Weekly electricity, transport)
        if current_date.weekday() == 6: # Every Sunday
            db.add(Expense(
                id=str(uuid.uuid4()), business_id=b_id, date=current_date, category="electricity",
                amount=1500.0 + random.uniform(-100, 300), payment_method="bank", reference="BILL-ELEC",
                notes="Weekly power bill", created_at=dt_utc
            ))
            db.add(Expense(
                id=str(uuid.uuid4()), business_id=b_id, date=current_date, category="transport",
                amount=800.0, payment_method="cash", reference="FUEL-TRANS",
                notes="Weekly delivery fuel", created_at=dt_utc
            ))
            
    db.commit()
    print("Database successfully populated with rich 90-day synthetic history.")
    print("User: admin@kopargaon.com")
    print("Password: password123")

if __name__ == "__main__":
    os.environ["TESTING"] = "1"
    seed()
