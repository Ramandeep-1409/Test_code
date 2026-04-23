# Event Management System

A full-stack web application built with **Python Flask** and **SQLite**, covering
Admin, Vendor, and User roles as specified in the assignment wireframes.

---

## Project Structure

```
event_management/
├── app.py                  ← Main Flask application (routes, models, logic)
├── requirements.txt        ← Python dependencies
├── static/
│   └── uploads/            ← Vendor product images
└── templates/
    ├── base.html           ← Shared layout (navbar, flash messages, footer)
    ├── index.html          ← Landing page (role selection)
    ├── admin_login.html
    ├── admin_dashboard.html
    ├── maintain_user.html
    ├── maintain_vendor.html
    ├── vendor_login.html
    ├── vendor_signup.html
    ├── vendor_dashboard.html
    ├── add_item.html
    ├── update_item.html
    ├── product_status.html
    ├── requested_items_vendor.html
    ├── user_login.html
    ├── user_signup.html
    ├── user_portal.html
    ├── vendor_page.html
    ├── products.html
    ├── cart.html
    ├── checkout.html
    ├── success.html
    ├── order_status_user.html
    ├── request_item.html
    └── guest_list.html
```

---

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app (creates DB & default admin automatically)
python app.py
```

Open http://127.0.0.1:5000 in your browser.

---

## Default Admin Credentials

| Field    | Value      |
|----------|------------|
| User ID  | `admin`    |
| Password | `admin123` |

---

## Role Flow (as per flowchart)

```
START → INDEX
  ├── Admin Login   → Admin Dashboard → Maintain Users / Maintain Vendors
  ├── Vendor Login  → Vendor Dashboard → Add Item / Your Items / Transaction / Logout
  │    └── Vendor Signup (new vendors)
  └── User Login    → User Portal → Vendors → Products → Cart → Checkout → Success
       └── User Signup (new users)       ↳ Request Item
                                         ↳ Order Status
                                         ↳ Guest List
```

---

## Features Implemented

### Admin
- Login with hidden password
- Dashboard (Maintenance Menu – Admin only)
- Maintain Users – view & delete registered users
- Maintain Vendors – view & delete vendors (cascades to products)

### Vendor
- Sign Up with Name, User ID, Email, Password, Category (dropdown: Catering / Florist / Decoration / Lighting)
- Login with hidden password + show/hide toggle
- Dashboard: view all own products with Update / Delete
- Add Item: name, price, image upload
- Update Item: pre-filled form
- Product Status: view orders containing own products; update status (Received → Ready for Shipping → Out For Delivery)
- Requested Items: view item requests submitted by users

### User
- Sign Up with Name, User ID, Email, Password
- Login with hidden password
- User Portal with category filter (Catering / Florist / Decoration / Lighting)
- Browse Vendors by category
- Browse Products per vendor; Add to Cart
- Cart: view, adjust quantity (+/−), remove item, clear all
- Checkout: delivery details form (Name, Email, Address, City, State, Pin Code, Number, Payment: Cash/UPI)
- Success popup with full order summary
- Order Status: track all own orders and their delivery status
- Request Item: submit custom item requests to vendors
- Guest List: view all registered users

### General
- Session management (role-based: admin / vendor / user)
- Form validations (all required fields, email, numeric price, file type)
- Flash messages for all actions
- Password hashing (Werkzeug)
- Image upload with secure filename
- Fully responsive UI (Bootstrap 5)

---

## Technology Stack

| Layer      | Technology           |
|------------|----------------------|
| Backend    | Python 3, Flask      |
| Database   | SQLite + SQLAlchemy  |
| Frontend   | Bootstrap 5, Jinja2  |
| Auth       | Werkzeug (hashing)   |
| File Upload| Werkzeug utils       |
