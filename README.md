# Swaad - Food Ordering Website

Swaad is a Django web application that connects people who want to order food with restaurant owners who want to manage a restaurant menu and customer orders.

This repository contains the source code for a local development project. It is not a deployed, public ordering service.

## How the project works

### Customer journey

1. A visitor creates an account. Registration includes a profile form and a reCAPTCHA check.
2. The customer signs in and browses approved restaurants. They can search and filter the restaurant list.
3. The customer opens a restaurant, browses available food, and can save the restaurant as a favorite or leave a review.
4. The customer adds food to their cart, changes quantities, and can apply an eligible coupon.
5. The customer places an order. If the cart contains items from multiple restaurants, the application creates a separate order for each restaurant.
6. The customer can view their profile and order details, including each order's current status.

### Restaurant owner journey

1. A restaurant owner creates a customer account and submits a restaurant application.
2. A site administrator reviews the application and approves the restaurant.
3. Once approved, the owner can edit restaurant details, add and edit menu items, and hide or restore menu items.
4. New orders appear on the owner's dashboard. The owner can view an order and update its status.

### Site administration

The Django admin site is available at `/admin/` for an administrator account. Create one locally with:

```powershell
python manage.py createsuperuser
```

Administrators can use Django's admin tools to manage records, including restaurant approval.

## Main features

- Customer registration, login, profile editing, and password reset
- Restaurant search and category filtering
- Restaurant details, menu items, favorites, and reviews
- Vendor registration, restaurant approval workflow, and owner dashboard
- Menu creation, editing, and availability controls
- Per-customer cart with quantity changes and removal
- Coupon validation and discounts
- Orders with separate restaurant fulfillment and status tracking
- Django admin interface

The cart offers Cash on Delivery and an Online Payment selection. **An online payment gateway is not integrated**, so selecting online payment does not process a real payment. Password-reset emails use Django's console email backend in the current settings.

## Technology

- Python
- Django
- SQLite for local development
- HTML, CSS, Bootstrap, and JavaScript
- Django Crispy Forms with Bootstrap 5
- `django-recaptcha` for the registration CAPTCHA

## Run the project locally on Windows

Open PowerShell in the folder containing `manage.py`. Create and activate a virtual environment, then install the packages:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The application has local development defaults and can start without a `.env` file. To set your own Django and reCAPTCHA keys, copy the example and edit it:

```powershell
Copy-Item .env.example .env
```

Keep `.env` private. It is excluded from Git by `.gitignore`. If you create a `.env` file, install the requirements above so `python-dotenv` can load it.

Apply database migrations and start the development server:

```powershell
python manage.py migrate
python manage.py runserver
```

Visit <http://127.0.0.1:8000/> in your browser. The development server is intended for local testing, not public hosting.

### Local reCAPTCHA note

When no real keys are provided, the project uses Google's published test keys. These keys allow local CAPTCHA testing but always pass verification; they do **not** prevent spam on a public website. Before deploying or relying on CAPTCHA protection, configure your own keys in `.env` and set up production Django security settings.

## Run the tests

With the project's virtual environment activated:

```powershell
python manage.py test
```

The test suite checks selected account/profile, cart, and order behavior. A passing test suite does not replace manually trying the full customer and restaurant-owner journeys.

## Project layout

```text
accounts/    Customer and restaurant-owner accounts, restaurants, menus, and reviews
cart/        Customer shopping cart
orders/      Coupons, order creation, and order status
module3/     Django project settings and main URL configuration
templates/   HTML pages rendered by Django
static/      CSS and other static assets
manage.py   Django command-line entry point
```

Database migrations are stored in each app's `migrations/` folder. Uploaded images are stored in the local `media/` folder during development.

## GitHub and security

The repository includes `.gitignore` rules to keep `.env`, the local SQLite database, uploaded media, and virtual environments out of GitHub. `.env.example` contains example development values; never copy real secrets into that file.

Before pushing changes, review what Git will upload:

```powershell
git status
```

Confirm `.env`, `db.sqlite3`, `media`, `.venv`, and `.venv-1` are not listed. Then commit and push:

```powershell
git add .
git commit -m "Describe your change"
git push
```

The local development secret, debug setting, and test reCAPTCHA keys are not production security settings. Do not deploy this configuration publicly as-is. The repository also contains a `create_test_users` management command with preset demo passwords; use it only in a local test database, never on a public or production site.
