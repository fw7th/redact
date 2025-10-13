import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ImageStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class jobs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    status: ImageStatus = Field(default=ImageStatus.uploaded)
    created_at: datetime.datetime
