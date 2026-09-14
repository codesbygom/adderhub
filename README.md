# AdderHub

A small Instagram-style social network built with Django: image posts, likes,
comments, following, profile search — served both as server-rendered pages
and as a JWT-authenticated REST API (with Swagger/Redoc docs) on the same
codebase.

The name is a nod to the adder (*Vipera berus*), one of the few snakes with
genuinely social behaviour (shared winter dens, documented companion
preference) — and, not coincidentally, `add` + `-er`.

## Features

- **Web app** (Django templates): sign up / log in, image feed, post detail
  with comments, like/unlike, follow/unfollow, user search, profile pages,
  account settings, password change.
- **REST API** (`/api/...`): JWT login/refresh, signup, profile list/detail,
  profile update, password change — documented at `/swagger/` and `/redoc/`.
- UUID primary keys throughout, custom `User`/`Post`/`Comment` managers for
  the query logic, image-upload validation.

## Tech stack

| Layer | Choice |
|---|---|
| Language / runtime | Python 3.12+ (developed & containerized on 3.14) |
| Framework | Django 6.1 |
| API | Django REST Framework 3.18 + `djangorestframework-simplejwt` |
| API docs | `drf-yasg` (Swagger UI / ReDoc) |
| Dependency management | [`uv`](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`) |
| Database | SQLite (default; swap `DATABASES` for anything else in production) |
| Containerization | Docker / Docker Compose |

## Running locally with Docker (recommended)

No local Python installation needed — everything runs inside the container.

```sh
docker compose up --build
```

This builds the image, runs migrations, and starts the dev server at
[http://localhost:8000](http://localhost:8000).

## Running locally with `uv` (no Docker)

If you have [`uv`](https://docs.astral.sh/uv/) installed, it will fetch the
right Python version for you automatically — no separate Python install
required either.

```sh
cd backend
uv run --project .. python manage.py migrate
uv run --project .. python manage.py runserver
```

## Running the tests

```sh
# with Docker:
docker compose exec web python manage.py test

# with uv:
cd backend && uv run --project .. python manage.py test
```

## Environment variables

The app runs with safe defaults out of the box for local development. Set
these explicitly in any real deployment:

| Variable | Purpose | Local default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django's cryptographic signing key | insecure dev key (not safe to deploy with) |
| `DJANGO_DEBUG` | `True`/`False` | `True` |
| `DJANGO_ALLOWED_HOSTS` | comma-separated hostnames | *(empty)* |
| `DJANGO_CORS_ALLOWED_ORIGINS` | comma-separated origins allowed to call the API | `http://127.0.0.1:5173` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | comma-separated origins trusted for CSRF-protected POSTs | `http://127.0.0.1:5173` |

Generate a real secret key with:

```sh
uv run --project . python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Project structure

```
backend/
├── account/        # custom User model, auth views (signup/login/profile/settings)
├── core/           # Post/Comment models, feed/search/like/comment views
├── api/
│   ├── api_account/  # JWT auth, signup, profile endpoints
│   └── api_core/     # (reserved for post/comment API endpoints)
├── config/         # settings, root urls, WSGI/ASGI entrypoints
└── templates/, static/
```

## API docs

With the server running:

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Deploying to PythonAnywhere

PythonAnywhere doesn't run Docker containers — it runs your code directly in
a virtualenv behind WSGI. It also currently supports **up to Python 3.13**
(Django 6.1 needs 3.12+, so 3.13 is what you'll deploy with there — the
Docker image above uses 3.14 locally, which is why `pyproject.toml` only
requires `>=3.12`).

1. **Create a free account** at [pythonanywhere.com](https://www.pythonanywhere.com).

2. **Open a Bash console** (Dashboard → New console → Bash) and clone the repo:

   ```sh
   git clone https://github.com/codesbygom/adderhub.git
   cd adderhub
   ```

3. **Create a virtualenv on Python 3.13** and install dependencies:

   ```sh
   mkvirtualenv --python=/usr/bin/python3.13 adderhub-env
   pip install -r requirements.txt
   ```

   (`requirements.txt` is exported from `uv.lock` — regenerate it after
   changing dependencies with `uv export --no-hashes --no-dev -o requirements.txt`.)

4. **Create the web app**: Dashboard → Web → *Add a new web app* → choose
   **Manual configuration** → Python 3.13.

5. **Point it at the virtualenv**: on the Web tab, under *Virtualenv*, enter
   `/home/<your-username>/.virtualenvs/adderhub-env`.

6. **Edit the WSGI file** (linked at the top of the Web tab). Replace its
   contents with:

   ```python
   import os
   import sys

   path = '/home/<your-username>/adderhub/backend'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

   # Production settings — this file lives on PythonAnywhere only,
   # it's never committed to the repo, so it's a safe place for these.
   os.environ['DJANGO_SECRET_KEY'] = 'paste-a-freshly-generated-key-here'
   os.environ['DJANGO_DEBUG'] = 'False'
   os.environ['DJANGO_ALLOWED_HOSTS'] = '<your-username>.pythonanywhere.com'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

7. **Run migrations and collect static files** (back in the Bash console,
   with the virtualenv active — `workon adderhub-env` if it isn't):

   ```sh
   cd ~/adderhub/backend
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

8. **Wire up static/media files** on the Web tab, under *Static files*:

   | URL | Directory |
   |---|---|
   | `/static/` | `/home/<your-username>/adderhub/backend/staticfiles` |
   | `/media/` | `/home/<your-username>/adderhub/backend/media` |

9. Hit the green **Reload** button on the Web tab, then visit
   `https://<your-username>.pythonanywhere.com`.

The free tier's SQLite database resets if the account goes idle for too long
and isn't shared across reloads reliably — fine for a portfolio demo, but
swap in PythonAnywhere's free MySQL database for anything longer-lived.

## Known limitations

This started as a learning project, not a production system — a few things
worth knowing if you read the code:

- The dev server (`runserver`) is used even in the Docker image; swap in
  `gunicorn`/`daphne` before exposing this to real traffic.
- SQLite is fine for a demo, not for concurrent production traffic.
- The REST API (`api/api_core`) currently only exposes account endpoints;
  post/comment/like/follow are web-only so far.
