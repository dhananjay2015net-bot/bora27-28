# Flask Online Project

## Local run
1. Install Python 3.
2. Open terminal in this folder.
3. Run: `pip install -r requirements.txt`
4. Run: `python app.py`
5. Open: http://127.0.0.1:5000

## Render
Build Command:
`pip install -r requirements.txt`

Start Command:
`gunicorn app:app`

Environment variables:
- SECRET_KEY = कोई लंबी random secret
- ADMIN_USERNAME = आपका admin username
- ADMIN_PASSWORD = आपका मजबूत admin password
- DATABASE_URL = Render PostgreSQL की Internal Database URL

Do not publish your real SECRET_KEY or ADMIN_PASSWORD in source code.
