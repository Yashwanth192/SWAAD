# Food Ordering Website

A Django web application for customers and restaurant owners. Customers can find restaurants, browse menus, add food to a cart, and place orders. Restaurant owners can register and manage their restaurant and menu.

## What it can do

- Customer registration, sign-in, profile, and password reset
- Restaurant browsing and food menus
- Vendor registration and restaurant/menu management
- Shopping cart, coupon codes, and order tracking
- Restaurant favorites and customer reviews
- Django admin site for site administration

## What you need

- Python 3.12 or newer
- pip
- Google reCAPTCHA keys only if you want to configure real captcha verification

## Run it on your computer

Open PowerShell in the project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in a text editor. Replace all three example values with your own credentials:

- `DJANGO_SECRET_KEY`: a new, private Django secret key
- `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY`: keys from your Google reCAPTCHA account

Without a `.env` file, the project uses Google's published test keys so the registration page can be tried locally. These test keys always pass verification and do **not** protect a public website from spam. Configure your own reCAPTCHA keys in `.env` before deploying or relying on captcha protection.

Do not post the contents of `.env` or commit it to GitHub. Then, in the same PowerShell window:

```powershell
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. The development server is for local testing, not public production hosting.

## Upload the project to GitHub

Create an empty repository on GitHub, then run these commands from the project folder. Replace the URL with the one for your repository:

```powershell
git init
git status
git add .
git status
git commit -m "Add Django food ordering project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Before committing, check `git status`: `.env`, `db.sqlite3`, `media`, and virtual environments should not be listed for commit. `.env.example` is safe to share because it contains example text, not working keys.

If a real secret or reCAPTCHA key was ever pushed to a public repository, remove it from the code **and rotate it with its provider**. Deleting it from a later commit does not make an exposed key safe again.
