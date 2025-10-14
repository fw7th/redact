from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class ImageStatus(str, Enum):
    uploaded = "queued"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class Files(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    status: ImageStatus = Field(default=ImageStatus.uploaded)
    batch_id: UUID = Field(foreign_key="batch.id")
    filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    batch: Optional["Batch"] = Relationship(back_populates="files")


class Batch(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    status: ImageStatus = Field(default=ImageStatus.uploaded)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    files: List[Files] = Relationship(back_populates="batch")
