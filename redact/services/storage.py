import os
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from redact.core.config import SUPABASE_BUCKET, get_supabase_client
from redact.core.database import AsyncSessionLocal
from redact.sqlschema.tables import Batch, BatchStatus, Files


async def create_batch_and_files(
    files: List[UploadFile], session: AsyncSession
) -> UUID:
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
                    batch_id=batch_id,
                    filename=f.filename,
                    created_at=datetime.utcnow(),
                )
                file_objs.append(file_obj)

            session.add_all(file_objs)
        # No need to call await.commit(), handled auto-handled by session.begin()

    except SQLAlchemyError as e:
        # handle/log later
        print("DB Error: ", e)
        raise HTTPException(status_code=500, detail="Failed to store batch")

    return batch_id


async def get_file_id_by_batch(batch_id: UUID, session: AsyncSession):
    statement = select(Files.file_id).where(Files.batch_id == batch_id)
    results = await session.execute(statement)
    return results.scalars().all()


# for async usage (FastAPI)
async def update_batch_status_async(batch_id: UUID, status: BatchStatus):
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Create and add batch record
                batch = await session.get(Batch, batch_id)

                if not batch:
                    raise ValueError("Batch not found")

                batch.status = status

                # Propagate to files
                # Return batch_id matching column for all rows, in a list.
                result = await session.execute(
                    select(Files).where(Files.batch_id == batch_id)
                )

                files = result.scalars().all()

                for f in files:
                    f.status = status

    except SQLAlchemyError as e:
        # handle/log later
        print("DB Error: ", e)
        raise


async def delete_batch_db(batch_id: UUID, session: AsyncSession):
    try:
        async with session.begin():
            batch = await session.get(Batch, batch_id)

            if not batch:
                raise ValueError("Batch not found")

            statement = select(Files.filename, Files.redact_filename).where(
                Files.batch_id == batch_id
            )
            results = await session.execute(statement)
            filenames = results.all()

            upload_list = []
            redact_list = []
            supabase_client = await get_supabase_client()
            for filename in filenames:
                file = f"uploads/{filename[0]}"
                upload_list.append(file)

                redact_file = f"redacted/{filename[1]}"
                redact_list.append(redact_file)

            await supabase_client.storage.from_(SUPABASE_BUCKET).remove(
                upload_list
            )  # Delete uploads

            await supabase_client.storage.from_(SUPABASE_BUCKET).remove(
                redact_list
            )  # Delete redacted files

            print("Specified files have been deleted.")

            # Delete all rows with this batch_id
            statement2 = delete(Files).where(Files.batch_id == batch_id)

            await session.execute(statement2)
            await session.delete(batch)  # Delete the row

    except SQLAlchemyError as e:
        # handle/log later
        print("DB Error: ", e)
        raise
