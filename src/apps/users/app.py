from fastapi import FastAPI

from src.apps.users.api import auth
from src.settings import settings

user_app = FastAPI(
    title="Users API",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

PREFIX = f"/api/{settings.api_version}"

user_app.include_router(auth.router, prefix=PREFIX)
