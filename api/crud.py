from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from tables import Batch, Files, FileStatus


async def create_batch_and_files(files: List[UploadFile], session: AsyncSession):
    batch_id = uuid4()

    try:
        async with session.begin():  # start transaction
            # Create and add batch record
            batch = Batch(id=batch_id)
            session.add(batch)

            # Create file records
            file_objs = []
            for f in files:
                file_obj = Files(
                    batch_id=batch_id, filename=f.filename, created_at=datetime.utcnow()
                )
                file_objs.append(file_obj)

            session.add_all(file_objs)
        # No need to call await.commit(), handled auto-handled by session.begin()

    except SQLAlchemyError as e:
        # handle/log later
        print("DB Error: ", e)
        raise HTTPException(status_code=500, detail="Failed to store batch")


def get_image(session: Session, image_id: int) -> Files | None:
    return session.get(Files, image_id)


async def get_files_by_batch(batch_id: UUID, session: AsyncSession):
    statement = select(Files).where(Files.batch_id == batch_id)
    results = await session.exec(statement)
    return results.all()


def update_image_status(session: Session, image_id: int, status: str) -> Files | None:
    image = session.get(Files, image_id)
    if not image:
        return None

    image.status = status
    session.add(image)
    session.commit()
    session.refresh(image)
    return image
