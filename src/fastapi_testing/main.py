import tomllib
from functools import cache
from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI

from fastapi_testing import config, fileservice

app = FastAPI()


@cache
def get_settings() -> config.Settings:
    """Dependency for loading settings from disk."""
    with Path("config.toml").open("rb") as f:
        settings = tomllib.load(f)
    return config.Settings(**settings)


def get_fileservice_client(
    settings: Annotated[config.Settings, Depends(get_settings)],
) -> fileservice.Client:
    """Dependency for a client for downloading files."""
    return fileservice.Client(settings.fileservice.datadir)


@app.get("/config")
async def get_config(
    settings: Annotated[config.Settings, Depends(get_settings)],
) -> config.Settings:
    return settings


@app.get("/download/{file_id:path}")
async def upload(
    file_id: str,
    fileservice_client: Annotated[fileservice.Client, Depends(get_fileservice_client)],
):
    return fileservice_client.download(file_id)


def main():
    settings = get_settings()
    uvicorn.run(
        "main:app", host=settings.host, port=settings.port, reload=settings.reload
    )


if __name__ == "__main__":
    main()
