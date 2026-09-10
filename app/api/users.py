from fastapi import APIRouter , Depends 
from sqlalchemy.ext.asyncio import AsyncSession 
from app.auth.dependencies import get_current_user
from app.auth.security import hash_password 
from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserCreate , UserResponse 

router = APIRouter(
    prefix = "/users",
    tags = ["Users"],
)

@router.post("/", response_model = UserResponse)
async def create_user(
    user_data : UserCreate,
    db : AsyncSession = Depends(get_db),
):
    user = User(
        username = user_data.username,
        passcode = hash_password(user_data.passcode),
        dob = user_data.dob,
    )

    db.add(user)

    await db.commit()

    await db.refresh(user)

    return user 


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

