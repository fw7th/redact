from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship, SQLModel


class FileStatus(str, Enum):
    uploaded = "queued"
    processing = "processing"
    complete = "complete"
    unusable = "unusable"
    failed = "failed"


class BatchStatus(str, Enum):
    uploaded = "queued"
    processing = "processing"
    completed = "complete"
    partially_failed = "partially_failed"
    failed = "failed"


class Files(SQLModel, table=True):
    file_id: UUID = Field(default_factory=uuid4, primary_key=True)
    batch_id: UUID = Field(foreign_key="batch.id")
    filename: str
    json_data: Dict[str, Any] = Field(default=None, sa_column=Column(JSONB))
    redact_filename: Optional[str] = Field(default=None)
    status: FileStatus = Field(default=FileStatus.uploaded)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    batch: Optional["Batch"] = Relationship(back_populates="files")


class Batch(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    status: FileStatus = Field(default=BatchStatus.uploaded)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    files: List[Files] = Relationship(back_populates="batch")
