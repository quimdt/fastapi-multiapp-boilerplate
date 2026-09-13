from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm

from src.apps.users.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from src.apps.users.dependencies import get_dao
from src.apps.users.schemas.auth import Token, User
from src.db.dao.base import BaseDAO
from src.db.exceptions import BadCredentials
from src.db.tables.users import UserSQLModel

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    dao: Annotated[BaseDAO, Depends(get_dao("default"))],
) -> Token:
    try:
        user = authenticate_user(dao, form_data.username, form_data.password)
    except BadCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email, "scopes": []})
    return Token(access_token=access_token)


@router.get("/me", response_model=User)
async def read_me(
    current_user: Annotated[UserSQLModel, Security(get_current_active_user, scopes=[])],
) -> UserSQLModel:
    return current_user
