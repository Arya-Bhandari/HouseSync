Set-Content -Path "d:\Arya\Django+Postgress\House Management\AGENTS.md" -Encoding UTF8 -Value @'
# AGENTS.md — House Management Project

This file provides AI coding assistants (e.g., Antigravity, Copilot, Claude) with the context, conventions, and constraints of this project.

---

## 📁 Project Overview

**House Management** is a Django 6.x web application backed by PostgreSQL. It helps manage household utilities, currently focused on daily milk consumption tracking and billing.

- **Framework**: Django 6.1.1
- **Database**: PostgreSQL 16 (via Docker)
- **Frontend**: Django Templates + TailwindCSS (via `tailwind.config.js`)
- **Auth**: Django's built-in auth system
- **Python deps**: `django`, `psycopg2-binary`

---

## 🗂️ Project Structure

```
House Management/
├── config/              # Django project config (settings, root urls, wsgi/asgi)
├── accounts/            # User authentication app (login, register, home)
├── milk/                # Milk tracking & billing app
│   ├── models.py        # MilkPrice, MilkEntry, MilkBill
│   ├── views.py         # add_milk_entry, milk_entry_list, calculate_milk_bill
│   ├── forms.py         # MilkEntryForm
│   ├── urls.py          # milk/ URL routes
│   └── templates/milk/  # HTML templates for milk views
├── templates/           # Global templates (base.html, accounts/)
├── static/              # Static assets (CSS, JS, images)
├── docker-compose.yml   # PostgreSQL service definition
├── manage.py
└── requirements.txt
```

---

## 🏗️ Apps

### `accounts`
Handles user authentication.
- Login page is the root `/` route (uses Django's built-in `LoginView`)
- After login, redirects to `home` (set via `LOGIN_REDIRECT_URL`)
- URLs prefixed at `/accounts/`

### `milk`
Tracks daily milk intake and calculates monthly bills.
- **Models**: `MilkPrice`, `MilkEntry`, `MilkBill`
- Milk types: `'cow'` and `'buffalo'` (defined in `MILK_CHOICES`)
- Pricing is date-effective: `get_price_for_entry()` finds the most recent price on or before an entry's date
- URLs prefixed at `/milk/`

---

## 🗄️ Database

- **Engine**: PostgreSQL (`django.db.backends.postgresql`)
- **Database name**: `main_db`
- **User**: `dev_user` / `dev_password`
- **Host**: `localhost`, **Port**: `5433` (Docker maps 5433→5432)

### Running the Database

```bash
docker-compose up -d
```

### Applying Migrations

```bash
python manage.py migrate
```

### Creating a Superuser

```bash
python manage.py createsuperuser
```

---

## 🚀 Running the Dev Server

Make sure the `.venv` is activated and the DB container is running:

```bash
# Activate virtualenv (Windows)
.venv\Scripts\activate

# Start the DB
docker-compose up -d

# Run Django dev server
python manage.py runserver
```

App is available at: http://127.0.0.1:8000

---

## 🧑‍💻 Coding Conventions

### General
- Use **function-based views (FBVs)** — the project uses `@login_required` decorators, not class-based views
- Keep views lean; business logic (like `get_price_for_entry`) should be in helper functions or model methods
- Use `commit=False` pattern when saving forms that need extra fields set (e.g., `logged_by`)

### Models
- Use `settings.AUTH_USER_MODEL` for ForeignKeys to the user model (not `auth.User` directly)
- Use `choices=` on fields wherever a fixed set of values applies
- `DecimalField` for all monetary and quantity values

### Templates
- Templates for an app live in `<app>/templates/<app>/` (e.g., `milk/templates/milk/`)
- Global/shared templates live in the root `templates/` directory
- TailwindCSS classes are used for styling

### URLs
- Use `name=` on every `path()` for reverse resolution
- Always use `redirect('url_name')` instead of hardcoded paths

### Forms
- Django's built-in `ModelForm` is preferred
- Form files live in `forms.py` within each app

---

## ⚠️ Important Notes

- `DEBUG = True` and `ALLOWED_HOSTS = ['*']` — **do not deploy as-is to production**
- `SECRET_KEY` is hardcoded in `settings.py` — move to environment variables before production
- The email backend is `console.EmailBackend` — emails print to stdout, not sent
- `TIME_ZONE` is set to `'UTC'`; consider changing to `'Asia/Kolkata'` if the app is India-specific

---

## 🔮 Planned / Potential Features

> Update this section as the project grows.

- [ ] Electricity bill tracking
- [ ] Water/gas utility tracking
- [ ] Monthly expense summary dashboard
- [ ] PDF bill generation
- [ ] Multi-household / tenant support

---

## 🤖 Agent Instructions

When working on this project:

1. **Always run migrations** after modifying models: `python manage.py makemigrations && python manage.py migrate`
2. **Preserve `@login_required`** on any view that handles user-specific data
3. **Don't add new dependencies** to `requirements.txt` without noting it explicitly
4. **Check `MILK_CHOICES`** in `models.py` before referencing milk type strings — always use `'cow'` or `'buffalo'`
5. **Use `MilkPrice` for billing** — pricing is date-effective, not a flat rate; always use `get_price_for_entry()` or equivalent logic
6. **Template naming**: follow the `<app>/templates/<app>/<template>.html` convention
7. **Do not modify** `docker-compose.yml` DB credentials without also updating `config/settings.py`
8. **Plan** Where every `/plan` command is used you should write a plan in a fie and store it here `D:\Arya\Django+Postgress\House Management\dev_docs` so user can read and improve it 
'@