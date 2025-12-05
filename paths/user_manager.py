from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, SQLModel, Field
from typing import Annotated, List
from database import SessionDep
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(SQLModel):
    name: str = Field(index = True)
    password: str
    
class User(UserBase,table=True):
    id: int = Field(default=None,primary_key=True)
    
class UserPublic(SQLModel):
    name: str
    id: int
    
@router.post("/register/", response_model=UserPublic)
def create_user(user: UserBase, session: SessionDep):
    user.password=pwd_context.hash(user.password)
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/auth/", response_model=UserPublic)
def read_user(user: UserBase, session: SessionDep):
    user_exist = session.exec(select(User).where(User.name == user.name)).first()
    if not user_exist or not pwd_context.verify(user.password, user_exist.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user_exist
