<p align="center">
  <img src="backend/static/images/logo.png" alt="AdderHub" width="360">
</p>

# AdderHub

A small Instagram-style social network built with Django: image posts,
likes, following, profile search — served both as server-rendered pages and
as a JWT-authenticated REST API (with Swagger/Redoc docs) on the same
codebase.

The name is a nod to the adder (*Vipera berus*), one of the few snakes with
genuinely social behaviour (shared winter dens, documented companion
preference) — and, not coincidentally, `add` + `-er`.

## Features

- **Web app** (Django templates): sign up / log in, "forgot password"
  email reset, Explore / Following feeds, like/unlike, comments,
  follow/unfollow with follower / following lists, user search, profile pages
  with avatar/background drag-and-drop upload, account settings, password
  change.
- **Admin panel** (`/panel/`, staff only): dashboard with site stats, user
  management (search, block / unblock, grant staff — superusers only),
  post and comment moderation.
- **REST API** (`/api/...`): JWT login/refresh/verify, signup, profiles
  (list + search, detail, `me`, update incl. images, password change),
  follow/unfollow + followers/following lists, suggestions, posts (CRUD,
  like/unlike, personal feed) and comments — documented at `/swagger/` and
  `/redoc/`.
- Sidebar "Upload Post" overlay (drag-and-drop image + caption), same
  interaction pattern as the profile picture uploader.
- Caching of profile counters, follow suggestions and panel stats, with
  signal-based invalidation. The backend is one setting (`CACHE_BACKEND`):
  Redis in Docker, Django's file cache on PythonAnywhere, in-process cache
  for local dev — the code doesn't change.
- UUID primary keys throughout, custom `User`/`Post` managers for the query
  logic, image-upload validation.

## Tech stack

| Layer | Choice |
|---|---|
| Language / runtime | Python 3.13 |
| Framework | Django 6.1 |
| API | Django REST Framework 3.18 + `djangorestframework-simplejwt` |
| API docs | `drf-yasg` (Swagger UI / ReDoc) |
| Cache | Redis (`django-redis`) or any Django cache backend, picked by `CACHE_BACKEND` |
| Dependency management | [`uv`](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`) |
| Database | SQLite (default; swap `DATABASES` for anything else in production) |
| Containerization | Docker / Docker Compose (`web` + `redis` services) |

## Running locally with Docker (recommended)

No local Python installation needed — everything (including Redis) runs
inside containers.

```sh
docker compose up --build
```

This builds the image, runs migrations, and starts the dev server at
[http://localhost:8000](http://localhost:8000), with a `redis` container
wired up automatically via `REDIS_URL`.

## Running locally with `uv` (no Docker)

If you have [`uv`](https://docs.astral.sh/uv/) installed, it will fetch the
right Python version for you automatically — no separate Python install
required either. Without `REDIS_URL` set, caching just uses Django's
in-process backend, so Redis isn't required for local dev.

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
| `CACHE_BACKEND` | `redis`, `file`, `db`, `locmem` or `dummy` | `redis` if `REDIS_URL` is set, else `locmem` |
| `REDIS_URL` | Redis connection string (for `CACHE_BACKEND=redis`) | *(empty)* |
| `CACHE_DIR` | folder for `CACHE_BACKEND=file` | `backend/.cache` |
| `CACHE_TIMEOUT` | default cache lifetime in seconds | `300` |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | SMTP for password-reset mails | console backend (mails are printed) |

Generate a real secret key with:

```sh
uv run --project . python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Project structure

```
backend/
├── account/            # custom User model, auth views (signup/login/profile/settings)
├── core/               # Post model, feed/search/like views, suggested_users tag
├── api/
│   ├── api_account/    # JWT auth, signup, profile + follow endpoints
│   └── api_core/       # post, like, feed and comment endpoints
├── panel/              # staff-only admin panel (/panel/)
├── config/             # settings, root urls, WSGI/ASGI entrypoints
├── templates/
│   ├── account/partials/   # avatar & background upload overlay
│   └── core/partials/      # post-upload overlay
└── static/
```

## API docs

With the server running:

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

Every endpoint except signup/login and the public profile reads needs an
`Authorization: Bearer <access token>` header. Lists are paginated
(`?page=N`, 20 per page).

| Method | Endpoint | What it does |
|---|---|---|
| POST | `/api/account/signup/` | create an account |
| POST | `/api/account/login/` · `refresh/` · `verify/` | JWT obtain / refresh / verify |
| GET | `/api/account/me/` | your own profile (incl. email) |
| PATCH | `/api/account/update/` | edit profile; multipart for `profile_img` / `background_img` |
| PUT | `/api/account/changepassword/` | change password |
| GET | `/api/account/?search=<text>` | list / search users |
| GET | `/api/account/suggestions/` | users you might want to follow |
| GET | `/api/account/<id>/` | public profile |
| POST / DELETE | `/api/account/<id>/follow/` | follow / unfollow |
| GET | `/api/account/<id>/followers/` · `following/` | follower lists |
| GET / POST | `/api/core/posts/` | all posts (`?user=<id>` to filter) / create (multipart) |
| GET | `/api/core/posts/feed/` | posts from people you follow, plus your own |
| GET / PATCH / DELETE | `/api/core/posts/<id>/` | post detail; only the owner can edit the caption or delete |
| POST / DELETE | `/api/core/posts/<id>/like/` | like / unlike |
| GET / POST | `/api/core/posts/<id>/comments/` | list / add comments |
| GET / PATCH / DELETE | `/api/core/comments/<id>/` | comment detail; owner-only edits |

## Deploying to PythonAnywhere

PythonAnywhere doesn't run Docker containers — it runs your code directly in
a virtualenv behind WSGI. It currently supports up to Python 3.13, which
matches what this project is pinned to, so no version juggling is needed.

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
   # PythonAnywhere has no Redis. The file cache is shared by all of the
   # web app's worker processes (LocMem would give each worker its own copy).
   os.environ['CACHE_BACKEND'] = 'file'
   os.environ['CACHE_DIR'] = '/home/<your-username>/adderhub/backend/.cache'

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
