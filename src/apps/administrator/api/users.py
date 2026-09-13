import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status

from src.apps.administrator.auth import get_current_active_user, get_password_hash
from src.apps.administrator.dao.users import UsersDAO
from src.apps.administrator.dependencies import get_dao
from src.apps.administrator.schemas.users import User, UserCreate, UserUpdate
from src.db.exceptions import DBError, NotFound
from src.db.tables.users import UserSQLModel

ScopeRead = Security(get_current_active_user, scopes=["me:read"])

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[UserSQLModel, ScopeRead],
) -> UserSQLModel:
    return current_user


@router.get("/users", response_model=list[User])
async def read_users(
    current_user: Annotated[UserSQLModel, ScopeRead],
    dao: Annotated[UsersDAO, Depends(get_dao("users"))],
) -> list[UserSQLModel]:
    return dao.get_all_users()


@router.get("/users/{user_id}", response_model=User)
async def read_user(
    user_id: uuid.UUID,
    current_user: Annotated[UserSQLModel, ScopeRead],
    dao: Annotated[UsersDAO, Depends(get_dao("users"))],
) -> UserSQLModel:
    try:
        return dao.get_user_by_id(user_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: Annotated[UserSQLModel, ScopeRead],
    dao: Annotated[UsersDAO, Depends(get_dao("users"))],
) -> UserSQLModel:
    values = payload.model_dump(exclude={"password"})
    values["pwd"] = get_password_hash(payload.password)
    try:
        return dao.create_user(values)
    except DBError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user",
        )


@router.patch("/users/{user_id}", response_model=User)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: Annotated[UserSQLModel, ScopeRead],
    dao: Annotated[UsersDAO, Depends(get_dao("users"))],
) -> UserSQLModel:
    values = payload.model_dump(exclude_unset=True)
    if "password" in values:
        values["pwd"] = get_password_hash(values.pop("password"))

    try:
        num_updated = dao.update_user(values, id=user_id)
        if num_updated == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return dao.get_user_by_id(user_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="User not found")
    except DBError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update user",
        )
