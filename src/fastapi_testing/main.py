from functools import cache
from typing import Annotated, Union

import uvicorn
from fastapi import Depends, FastAPI

from fastapi_testing import config

app = FastAPI()


@cache
def get_settings() -> config.Settings:
    return config.Settings()  # type: ignore


@app.get("/config")
async def get_config(
    settings: Annotated[config.Settings, Depends(get_settings)],
) -> config.Settings:
    return settings


@app.get("/items/{item_id}")
async def get_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


def main():
    # load settings, fail early in case of missing config
    settings = get_settings()
    uvicorn.run(
        "main:app", host=settings.host, port=settings.port, reload=settings.reload
    )


if __name__ == "__main__":
    main()
