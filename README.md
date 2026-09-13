# FastAPI Multi-App Boilerplate

A [FastAPI](https://fastapi.tiangolo.com/) boilerplate that splits an API into
multiple mounted sub-applications. Each sub-app lives under `src/apps/`, has its
own routers, auth, DAOs and schemas, and is mounted on a different URL path of a
single "main" app.

Licensed under the [MIT License](LICENSE).

## Features

- Multi-app architecture (see [Structure](#structure)).
- JWT authentication (OAuth2 password flow + scopes) with `PyJWT` and `passlib`/`bcrypt`.
- SQLAlchemy 2.0 ORM models + DAO pattern with per-feature DAO factories.
- Alembic migrations.
- Docker + docker compose with dev, prod and test compose files.
- `pytest` test suite with DB fixtures and an authenticated `TestClient`.
- Ruff + MyPy configuration.

## Structure

```
├── alembic                 # Alembic migrations
├── docker/entrypoint.sh    # Container entrypoint (runs migrations)
├── docker-compose*.yaml    # docker compose variants (base, dev, prod, test)
├── src
│   ├── main.py             # "Main App" that mounts every sub-app
│   ├── settings.py         # pydantic-settings based configuration
│   ├── apps
│   │   ├── administrator   # Admin sub-app (auth + users API)
│   │   └── users           # Public users sub-app (auth + me API)
│   └── db                  # Shared DB layer (tables, DAO base, dependencies)
└── tests
```

Sub-apps are mounted in `src/main.py`:

| Path                                                   | App             | Docs                |
| ------------------------------------------------------ | --------------- | ------------------- |
| `/` (everything not matched above)                     | administrator   | `/docs`             |
| `/users/*`                                             | users           | `/users/docs`       |

`GET /` on the main app returns the version from `src/VERSION`.

## Requirements

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- PostgreSQL

## Setup

```bash
cp .env.example .env          # adjust SECRET_KEY and DATABASE_URL
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:main_app --reload
```

Open http://localhost:8000 for the main app, http://localhost:8000/docs for the
administrator API and http://localhost:8000/users/docs for the users API.

### First admin user

`src/seed.py` creates the first administrator user on first execution. It runs
automatically from `docker/entrypoint.sh` after the migrations, and can also be
run manually:

```bash
poetry run python -m src.seed
```

Configure it via env vars (see `.env.example`): `ADMIN_EMAIL`, `ADMIN_PASSWORD`,
`ADMIN_NAME`, `ADMIN_SURNAME`. It is idempotent — if the email already exists it
does nothing. Change `ADMIN_PASSWORD` before going to production.

### Running tests

Tests require a running PostgreSQL. `tests/base.py` creates the configured test
database automatically if it does not exist; point `DATABASE_URL` at a database
you do not mind being dropped/recreated.

```bash
poetry run pytest -v
```

### Docker

Docker compose overrides `DATABASE_URL` at runtime so the containers connect to
the `postgres` service by name (`@postgres:5432`) instead of `localhost`. The
`localhost` value in `.env` is only used when running without Docker.

```bash
# development (loads docker-compose.override.yaml: --reload + volume mounts)
docker compose up --build

# production
docker compose -f docker-compose.yaml -f docker-compose.prod.yaml up --build

# tests
docker compose -f docker-compose.test.yaml build
docker compose -f docker-compose.test.yaml run --rm test
```

## Adding a new sub-app

1. Create `src/apps/<name>/app.py` with a `FastAPI` instance that includes its
   routers under its own `PREFIX`.
2. Give it `auth.py`, `dependencies.py`, `dao/factory.py` and `schemas/` as
   needed (use the `users` app as a minimal reference).
3. Mount it in `src/main.py` **before** the catch-all `/` mount:

```python
main_app.mount("/<name>", <name>_app)
```

## API endpoints

### Administrator (`/api/v1`)

| Method | Path           | Auth scope | Description      |
| ------ | -------------- | ---------- | ---------------- |
| POST   | `/login`       | —          | Get a JWT token  |
| GET    | `/users`       | `me:read`  | List users       |
| POST   | `/users`       | `me:read`  | Create a user    |
| GET    | `/users/me`    | `me:read`  | Current user     |
| GET    | `/users/{id}`  | `me:read`  | Get a user       |
| PATCH  | `/users/{id}`  | `me:read`  | Update a user    |

### Users (`/users/api/v1`)

| Method | Path    | Auth scope | Description     |
| ------ | ------- | ---------- | --------------- |
| POST   | `/login`| —          | Get a JWT token |
| GET    | `/me`   | —          | Current user    |