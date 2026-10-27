from pydantic import BaseModel
from typing import Any


class FileResponse(BaseModel):
    success: bool
    file_name: str
    file_type: str
    record_count: int
    data: list[Any]