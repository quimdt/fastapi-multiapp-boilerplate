from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.apps.administrator.auth import authenticate_user, create_access_token
from src.apps.administrator.dependencies import get_dao
from src.apps.administrator.schemas.auth import Token
from src.db.dao.base import BaseDAO
from src.db.exceptions import BadCredentials

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

    access_token = create_access_token(
        data={"sub": user.email, "scopes": ["me:read"]}
    )
    return Token(access_token=access_token)
