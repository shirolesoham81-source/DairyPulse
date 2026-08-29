# DairyPulse Backend Foundation

DairyPulse is a digital growth and finance-readiness platform for small rural dairy-processing MSMEs. This is the **Task 1 Backend Foundation & Data Contract**.

---

## 1. Local Development Setup (PostgreSQL)

To run the application locally with PostgreSQL, you do not need to manually install Postgres. A Docker Compose configuration is provided.

### Prerequisites
- [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)
- Python 3.10+

### Steps
1. **Start PostgreSQL Container:**
   ```bash
   docker-compose up -d
   ```
2. **Setup Environment Variables:**
   Copy the template environment file:
   ```bash
   cp .env.example .env
   ```
3. **Install Dependencies:**
   Create and activate a virtual environment, then install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   pip install psycopg2-binary
   ```
4. **Run Migrations:**
   Ensure database tables are generated using Alembic:
   ```bash
   alembic upgrade head
   ```
5. **Seed the Database:**
   Populate the database with synthetic dairy MSME data (Kopargaon Fresh Dairy):
   ```bash
   python -m app.seed
   ```
6. **Start Dev Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Access the interactive Swagger documentation at: `http://127.0.0.1:8000/docs`

---

## 2. Person 1 (Frontend / UX) Integration Guide

### Authentication
DairyPulse uses JWT Bearer Tokens.
- **Login Endpoint:** `POST /api/v1/auth/login`
- **Request Format (form-data):**
  - `username`: Email/Phone (e.g. `admin@kopargaon.com`)
  - `password`: Password (e.g. `password123`)
- **Response:**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```
- Pass this token in the header of all subsequent API requests:
  `Authorization: Bearer <access_token>`

### Common Response format
Success:
```json
{
  "success": true,
  "data": { ... },
  "message": "Action completed successfully"
}
```
Error:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Quantity must be greater than zero"
  }
}
```

### Key Transaction Endpoints
- **Create Invoice:** `POST /api/v1/invoices/`
  Creates billing records, adds stock OUT inventory transaction, logs audit trail and business history atomically.
- **Create Purchase:** `POST /api/v1/purchases/`
  Creates raw material purchases and increases stock IN.
- **Record Production:** `POST /api/v1/production/`
  Records finished product yields and decreases corresponding raw materials.

---

## 3. Person 3 (Analytics / Intelligence) Integration Guide

You do not need to access the database directly or write SQL queries. Clean historical timelines are provided via versioned endpoints.

### Endpoints
- **Sales History:** `GET /api/v1/analytics/sales-history`
- **Procurement History:** `GET /api/v1/analytics/procurement-history`
- **Production History:** `GET /api/v1/analytics/production-history`
- **Inventory Ledger:** `GET /api/v1/analytics/inventory-history`
  Contains ledger transaction history showing: `quantity_in`, `quantity_out`, `item_type`, and `transaction_type`.
- **Business Timeline:** `GET /api/v1/analytics/business-history`
  Chronological log of events (e.g., invoice created, production recorded) with associated metadata.

### Consent & Sharing Enforcement
Lenders and third parties cannot retrieve data without explicit business consent.
- **Verify Consent:** `GET /api/v1/consent/verify/{recipient_name}` checks if the current business has granted active, approved access.
