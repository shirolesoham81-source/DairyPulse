# Person 3 (Analytics / Intelligence) Integration Guide

This document describes how the Analytics/ML layer consumes clean structured datasets without interacting with SQL queries or DB models directly.

## Base API URL
`/api/v1/analytics/`

---

## 1. History Timelines
- **Sales History:** `GET /analytics/sales-history`
  - Optional Query Params: `from_date` (YYYY-MM-DD), `to_date` (YYYY-MM-DD)
  - Returns invoice dates, totals, and payment configurations.
- **Procurement History:** `GET /analytics/procurement-history`
  - Returns purchase items, purchase date, total amount, and actual lead time in days.
- **Production History:** `GET /analytics/production-history`
  - Daily yields of finished products.
- **Inventory Ledger:** `GET /analytics/inventory-history`
  - List of raw stock movements. Useful for detecting anomalies, waste, and stock levels.

---

## 2. Customer & Supplier Profiling
For customer ledgers and supplier metrics:
- **Customer Ledger:** `GET /analytics/customers/{customer_id}`
  - Returns: `total_purchases`, `invoices_count`, `paid_amount`, `pending_amount`, `last_transaction_date`.
- **Supplier Ledger:** `GET /analytics/suppliers/{supplier_id}`
  - Returns: `total_purchased`, `average_purchase_price`, `number_of_purchases`, `typical_lead_time_days`.

---

## 3. Business Timeline
- **Timeline Endpoint:** `GET /analytics/business-history`
  - Optional Query Param: `event_type` (e.g., `invoice_created`, `production_recorded`).
  - Returns chronological logging event list.
