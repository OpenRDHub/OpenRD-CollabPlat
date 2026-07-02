from datetime import datetime

from pydantic import BaseModel


class FileOut(BaseModel):
    file_id: str
    filename: str
    size: int = 0
    url: str

    model_config = {"from_attributes": True}
