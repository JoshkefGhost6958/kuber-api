# Kuber API

Django REST backend for the Kuber ride-hailing platform (Kirinyaga, Kenya):
phone+OTP auth, driver onboarding/compliance, vehicle catalog (Boda electric /
Boda / Tuktuk / Cab), and admin/field map markers for data collection.

## Local development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_drivers   # demo online drivers (Kirinyaga)
python manage.py seed_markers   # demo data-collection markers
python manage.py createsuperuser   # phone +2547..., for admin + field collection
python manage.py runserver
```

Tests: `pytest`

## Configuration (environment variables)

| Var | Purpose | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Production secret key | (random 50+ chars) |
| `DJANGO_DEBUG` | `True`/`False` | `False` in prod |
| `DJANGO_ALLOWED_HOSTS` | Comma list of hosts | `kuber-api.onrender.com` |
| `DATABASE_URL` | Postgres URL (falls back to SQLite) | `postgres://user:pass@host/db` |
| `CORS_ALLOWED_ORIGINS` | Comma list of app origins | `https://app.kuber.co.ke` |
| `CSRF_TRUSTED_ORIGINS` | Comma list for admin POSTs | `https://kuber-api.onrender.com` |
| `OTP_REQUEST_RATE` | Throttle (dev only loosen) | `5/hour` (default) |

OTP delivery and M-Pesa are stubbed; `dev_code` is only returned when `DEBUG`.

## Deploy

Static files are served by WhiteNoise; the DB uses `DATABASE_URL` (Postgres in
prod). The `Procfile` runs `collectstatic` + `migrate` on release and serves via
gunicorn.

**Render / Railway / Heroku**
- Build: `pip install -r requirements.txt`
- Start: `gunicorn config.wsgi --bind 0.0.0.0:$PORT` (or use the `Procfile`)
- Add a Postgres instance and set `DATABASE_URL`, plus the env vars above.
- After first deploy, create an admin: `python manage.py createsuperuser`.

Point the mobile app at the deployed URL via `EXPO_PUBLIC_API_URL`
(e.g. `https://kuber-api.onrender.com/v1`).
