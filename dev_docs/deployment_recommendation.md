# Deployment Recommendations: 100% Free Hosting for Django & PostgreSQL

This guide outlines the best architecture, platform comparisons, required codebase adjustments, and a step-by-step walkthrough to deploy the **House Management (HouseSync)** application along with a PostgreSQL database completely free of charge.

---

## 1. Recommended Architecture

| Component | Platform | Free Tier Specifications | Permanence |
|---|---|---|---|
| **Web Service (Compute)** | **[Render.com](https://render.com)** | 512 MB RAM, 0.1 CPU, auto-deploys from GitHub, free automated SSL | Perpetual free tier |
| **Database (PostgreSQL)** | **[Neon.tech](https://neon.tech)** | Serverless PostgreSQL 16, 0.5 GB storage, connection pooling, automated backups | Perpetual free tier |

### Why not Render's built-in PostgreSQL?
While Render provides a built-in PostgreSQL database on its free plan, **Render's free database automatically expires and is deleted after 30 days**.

By pairing **Render (for the Django web service)** with **Neon (for managed PostgreSQL)**:
1. Your database **never expires** or gets deleted after 30 days.
2. Both platforms offer native GitHub login and generous free resource limits.
3. Your deployment remains **100% free permanently**.

---

## 2. Free Hosting Platform Comparison

| Option | Web App Tier | Database Tier | Pros | Considerations |
|---|---|---|---|---|
| **Render + Neon.tech** *(Recommended)* | Free (512 MB RAM, spins down on 15m inactivity) | Free (0.5 GB storage, serverless compute) | Extremely easy setup, automated GitHub CD, zero cost, reliable Postgres | Spins down when idle (takes ~30-45s on first request after inactivity) |
| **Koyeb + Neon.tech** | Free (512 MB RAM, global edge network) | Free (0.5 GB storage) | Fast deployments, modern UI, low latency | Slightly fewer tutorials than Render |
| **Supabase (Alternative DB)** | — | Free (500 MB storage, Postgres 15/16) | Excellent database GUI, automated backups | Free databases pause if inactive for 7 days (can be restored with 1 click) |
| **PythonAnywhere** | Free (512 MB RAM, beginner friendly) | Free (MySQL only) | Built specifically for Python | **Does not support PostgreSQL on free tier**; restricted outbound internet access |
| **Fly.io / Railway** | Credit-based / Paid trial | Managed Postgres | High performance | **No longer offer perpetual free tiers**; requires credit card and charges after trial credits run out |

---

## 3. Required Code Adjustments for Production

Before pushing to production, the repository needs four small configuration enhancements:

### A. Production Dependencies (`requirements.txt`)
Add the following packages:
```text
django
psycopg2-binary
gunicorn>=21.2.0
whitenoise>=6.6.0
dj-database-url>=2.1.0
python-dotenv>=1.0.0
```

- **`gunicorn`**: Production WSGI HTTP server to serve the Django application.
- **`whitenoise`**: Enables Django to serve its own static files (CSS, JS, images) efficiently in production without needing AWS S3 or Nginx.
- **`dj-database-url`**: Parses the cloud `DATABASE_URL` connection string dynamically.
- **`python-dotenv`**: Loads local `.env` variables cleanly in development.

---

### B. Production Settings (`config/settings.py`)

Update `config/settings.py` to support environment variables while preserving local development:

```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Secret Key & Debug from Environment
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-fallback-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# 2. Allowed Hosts & CSRF
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://*.koyeb.app',
]

# 3. WhiteNoise Middleware (inserted right after SecurityMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- Add WhiteNoise here
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of middleware
]

# 4. Database configuration (Neon in Production, Docker/Local in Development)
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://dev_user:dev_password@localhost:5433/main_db',
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# 5. Static Files with WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

### C. Build Script (`build.sh`)
Create an executable build script in the root directory:

```bash
#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static assets
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
```

---

### D. Git Ignore (`.gitignore`)
Ensure the following entries exist in `.gitignore` so secrets and build artifacts are not committed:

```gitignore
.env
__pycache__/
*.pyc
db.sqlite3
staticfiles/
.venv/
```

---

## 4. Step-by-Step Deployment Walkthrough

### Step 1: Create Free Database on Neon.tech
1. Visit **[neon.tech](https://neon.tech)** and click **Sign Up** (sign in with GitHub).
2. Click **Create Project**:
   - **Name**: `housesync-db` (or any preferred name)
   - **Postgres Version**: 16 (default)
   - **Region**: Choose the region closest to you (e.g., `AWS - Singapore` or `AWS - Frankfurt`).
3. Under the **Connection Details** dashboard panel:
   - Select **Connection string**
   - Choose **Django** or **URI** format
   - It will look like:
     ```
     postgresql://<username>:<password>@ep-xyz-123456.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
     ```
   - Copy and save this connection string.

---

### Step 2: Push Repository to GitHub
If your repository is not yet hosted on GitHub:
1. Initialize git and commit:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit with production settings"
   ```
2. Create a new repository on **[github.com](https://github.com)** (private or public).
3. Push your code:
   ```powershell
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 3: Deploy Web App on Render.com
1. Go to **[render.com](https://render.com)** and log in with GitHub.
2. Click **New +** at the top right and select **Web Service**.
3. Select your GitHub repository (`House Management`).
4. Configure the Web Service:
   - **Name**: `housesync` (your URL will be `https://housesync.onrender.com`)
   - **Region**: Pick the same region or nearest to your Neon database region.
   - **Branch**: `main`
   - **Root Directory**: Leave blank (root).
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`
   - **Instance Type**: Select **Free** ($0/month).
5. Add **Environment Variables** in the Environment section:
   | Key | Value | Notes |
   |---|---|---|
   | `DATABASE_URL` | `postgresql://...neon.tech/neondb?sslmode=require` | The connection string copied from Neon |
   | `SECRET_KEY` | *(generate a random 50-character string)* | Production Django secret key |
   | `DEBUG` | `False` | Must be False in production |
   | `PYTHON_VERSION` | `3.12.0` | Matches local environment |
6. Click **Create Web Service**.
   Render will automatically fetch the code, run `./build.sh` (installing dependencies, running `collectstatic`, and executing migrations on your Neon DB), and launch `gunicorn`.

---

### Step 4: Create Admin Superuser
Once deployment succeeds:
1. In the Render dashboard for your service, click on the **Shell** tab on the left sidebar.
2. Run:
   ```bash
   python manage.py createsuperuser
   ```
3. Enter your desired admin username, email, and password.
4. You can now log into your live site and access the Administrator Dashboard!

---

## 5. Important Tips for Free Cloud Hosting

1. **Spin-down / Inactivity Sleeping**:
   Free web services on Render spin down after 15 minutes of inactivity to conserve resources. When someone visits the site after it has slept, the initial request may take **30 to 50 seconds** to wake up the server. Subsequent requests will be instant.
   - *Optional Tip*: You can set up a free uptime monitor (like [UptimeRobot.com](https://uptimerobot.com) or [cron-job.org](https://cron-job.org)) to ping your site's URL every 14 minutes if you wish to keep it awake during waking hours.
2. **Database Connection Pooling**:
   Neon provides a pooled connection mode (`-pooler` in the host URL). For standard Django web applications with moderate household usage, either standard or pooled endpoints work smoothly.
3. **Data Backups**:
   Neon automatically retains backups and provides branch/restore functionality on the free tier, protecting household logs and records from accidental loss.
