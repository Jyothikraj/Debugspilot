from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import Chat, Repository, User
from app.llm.generator import generate_answer
from app.schemas.chat import ChatCreate, ChatResponse


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------
    # Check Repository
    # --------------------------------------------------

    result = await db.execute(
        select(Repository).where(
            Repository.id == chat_data.repository_id,
            Repository.user_id == current_user.id,
        )
    )

    repository = result.scalar_one_or_none()

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found.",
        )

    # --------------------------------------------------
    # Check Repository Status
    # --------------------------------------------------

    if repository.status != "ready":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Repository is not ready. "
                f"Current status: {repository.status}"
            ),
        )

    # --------------------------------------------------
    # Generate Answer
    # --------------------------------------------------

    answer = await run_in_threadpool(
        generate_answer,
        chat_data.query,
        chat_data.repository_id,
    )

    # --------------------------------------------------
    # Save Chat
    # --------------------------------------------------

    chat = Chat(
        user_id=current_user.id,
        repository_id=chat_data.repository_id,
        query=chat_data.query,
        answer=answer,
    )

    db.add(chat)

    await db.commit()
    await db.refresh(chat)

    # --------------------------------------------------
    # Return Response
    # --------------------------------------------------

    return chat

@router.get("/{repository_id}", response_model=list[ChatResponse])
async def get_chat_history(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Repository).where(
            Repository.id == repository_id,
            Repository.user_id == current_user.id,
        )
    )

    repository = result.scalar_one_or_none()

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found."
        )

    result = await db.execute(
        select(Chat)
        .where(
            Chat.repository_id == repository_id,
            Chat.user_id == current_user.id,
        )
        .order_by(Chat.id.asc())
    )

    return result.scalars().all()