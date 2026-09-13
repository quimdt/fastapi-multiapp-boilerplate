from fastapi import FastAPI

from src.apps.administrator.api import auth, users
from src.settings import settings

administrator_app = FastAPI(
    title="Administrator API",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

PREFIX = f"/api/{settings.api_version}"

administrator_app.include_router(auth.router, prefix=PREFIX)
administrator_app.include_router(users.router, prefix=PREFIX)
