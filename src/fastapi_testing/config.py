from pydantic import BaseModel


class FileService(BaseModel):
    datadir: str


class Settings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    fileservice: FileService
