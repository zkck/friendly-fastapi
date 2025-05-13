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
    with Path("config.toml").open("rb") as f:
        return config.Settings(**tomllib.load(f))


def get_fileservice_client(
    settings: Annotated[config.Settings, Depends(get_settings)],
) -> fileservice.Client:
    return fileservice.Client(settings.fileservice.datadir)


@app.get("/config")
async def get_config(
    settings: Annotated[config.Settings, Depends(get_settings)],
) -> config.Settings:
    return settings


@app.get("/download/{file_id}")
async def upload(
    file_id: str,
    fileservice_client: Annotated[fileservice.Client, Depends(get_fileservice_client)],
):
    return fileservice_client.download(file_id)


def main():
    # load settings, fail early in case of missing config
    settings = get_settings()
    uvicorn.run(
        "main:app", host=settings.host, port=settings.port, reload=settings.reload
    )


if __name__ == "__main__":
    main()
