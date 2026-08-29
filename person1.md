# Person 1 (Frontend / UX) Integration Guide

This document describes how the Flutter/mobile frontend integrates with the backend API endpoints.

## Base API URL
All API requests must prefix:
`/api/v1/`

---

## 1. Authentication Workflow
DairyPulse uses JWT Bearer Token validation.
- **Login Endpoint:** `POST /auth/login`
- **Request Parameters (Form Data):**
  - `username`: Phone or email (e.g., `admin@kopargaon.com`)
  - `password`: Hashed or plain text (e.g., `password123`)
- **Response Format:**
  ```json
  {
    "access_token": "<jwt_string>",
    "token_type": "bearer"
  }
  ```
- **Authorization Header:** For all subsequent requests, append:
  `Authorization: Bearer <access_token>`

---

## 2. Invoicing (Billing Screen)
Enables creating a customer invoice. The backend automatically manages inventory OUT transactions and records the event in the history timeline.
- **Endpoint:** `POST /invoices/`
- **Body payload:**
  ```json
  {
    "customer_id": "cust-uuid-here",
    "invoice_date": "2026-08-29",
    "payment_status": "paid",
    "payment_method": "upi",
    "items": [
      {
        "product_id": "prod-uuid-here",
        "quantity": 5.0,
        "unit": "kg",
        "unit_price": 320.0
      }
    ],
    "notes": "Delivered to reception"
  }
  ```

---

## 3. Inventory Management
Retrieves the real-time stock levels of finished products and raw materials.
- **Endpoint:** `GET /inventory/`
- **Response Format:**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "item-uuid",
        "name": "Paneer",
        "type": "product",
        "current_quantity": 42.5,
        "unit": "kg"
      }
    ]
  }
  ```
