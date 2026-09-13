import tracemalloc
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.apps.administrator.app import administrator_app
from src.apps.users.app import user_app
from src.settings import settings

tracemalloc.start()

main_app = FastAPI(title="Main App", docs_url=None, redoc_url=None, openapi_url=None)

origins = [
    settings.frontend_host,
]

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount order matters: "/users" must be registered before the catch-all "/"
# mount so requests under /users/* are handled by the users app.
main_app.mount("/users", user_app)
main_app.mount("/", administrator_app)


@main_app.get("/")
def read_root():
    version_path = Path(__file__).resolve().parent / "VERSION"
    return {"version": version_path.read_text().strip()}
