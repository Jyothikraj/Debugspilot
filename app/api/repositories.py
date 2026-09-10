from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import Repository, User
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
)
from app.ingestion.repo_loader import load_repository


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


@router.post("/", response_model=RepositoryResponse)
async def create_repository(
    repository_data: RepositoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = Repository(
        repo_url=repository_data.repo_url,
        user_id=current_user.id,
        status="pending",
    )

    db.add(repository)

    await db.commit()
    await db.refresh(repository)

    repository.status = "processing"

    await db.commit()

    try:
        await run_in_threadpool(
            load_repository,
            repository_data.repo_url,
            repository.id,
        )

        repository.status = "ready"

    except Exception:
        repository.status = "failed"
        await db.commit()
        raise

    await db.commit()
    await db.refresh(repository)

    return repository

@router.get("/", response_model=list[RepositoryResponse])
async def get_repositories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Repository)
        .where(Repository.user_id == current_user.id)
        .order_by(Repository.id.desc())
    )

    return result.scalars().all()


@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
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

    return repository

@router.delete("/{repository_id}")
async def delete_repository(
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

    await db.delete(repository)
    await db.commit()

    return {
        "message": "Repository deleted successfully."
    }