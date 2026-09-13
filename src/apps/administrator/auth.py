from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import ValidationError

from src.apps.administrator.dependencies import get_dao
from src.apps.administrator.schemas.auth import TokenData
from src.db.dao.base import BaseDAO
from src.db.exceptions import BadCredentials, NotFound
from src.db.tables.users import UserSQLModel
from src.settings import settings

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/login",
    scopes={"me:read": "Read users."},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches a given hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def authenticate_user(dao: BaseDAO, email: str, password: str) -> UserSQLModel:
    try:
        user = dao.get_value_by_filter(UserSQLModel, email=email)
    except NotFound:
        raise BadCredentials()
    if not verify_password(password, user.pwd):
        raise BadCredentials()
    return user


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    dao: Annotated[BaseDAO, Depends(get_dao("default"))],
) -> UserSQLModel:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, email=email)

    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    try:
        user = dao.get_value_by_filter(UserSQLModel, email=email)
    except NotFound:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[UserSQLModel, Security(get_current_user, scopes=[])],
) -> UserSQLModel:
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
