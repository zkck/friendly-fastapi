# Friendly and Testable Python APIs with FastAPI

I'm someone who is extremely risk-averse, bordering OCD. If I lock my car, I'll
pull on the door handle. I have zero trust in my abilities. So to me, there is
nothing more scary than writing code in a project where I find it difficult to
write tests.

And if I have deliverables and stuff, changing the code to make it testable is a
lot of refactoring and sometimes not feasible. So setting up a project with a
testable structure from the beginning is paramount, and a common courtesy to
your fellow developers.

So in this blogpost we'll go through we can build a dev-friendly, test-friendly,
image-friendly, Kubernetes-friendly API using Python. We'll be using frameworks
which in my opinion should be in every Python project, namely:

- uv for project management
- FastAPI for the HTTP server
- pytest for testing
- pydantic for data validation.

We're going to aim to build this HTTP server as minimally as possible, with no
unnecessary dependencies, as we want to build a nice clean image from our
project.

> If you're lazy like me and just want to see the code, go check it out at
> github.com/zkck/friendly-fastapi

## Create the project with `uv`

First off, let's create the project. `uv` is a package manager, a task runner,
basically just does a lot of different Python things very well.

Let's create our project with uv:

```bash
uv init --package friendly
```

We use `--package` because IMO it creates a nicer project structure, where the
source code is contained within a `src/` directory, making it more suitable for
projects which grow in size. Furthermore we will be adding a `tests/` directory
later on at the root, so I find it better to have two separate directories.

Your project should now look like this:

```
.
├── pyproject.toml
├── README.md
└── src
    └── friendly
        └── __init__.py
```

## The `main.py` module

As mentioned, we'll be writing an HTTP server. We'll be using FastAPI, which is
an HTTP server library which comes with a lot of batteries included and makes
lots of good choices in its dependencies.

For this project, we'll be taking particular care when installing our
dependencies, as we want to have a minimal footprint for our Docker image.
Instead of using `fastapi[standard]`, we'll just add `fastapi` directly and
install the HTTP runtime `uvicorn` ourselves:

```bash
uv add fastapi uvicorn
```

Let's write the main function in a new file under
`src/niceapi/main.py`:

```python
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/config")
async def get_config():
    return "TODO: return server config"

def main():
    uvicorn.run("main:app")

if __name__ == "__main__":
    main()
```

> The code structure in `main.py` is a bit different to what's shown in the
> FastAPI docs, where you just define the `app` and the endpoints, and let
> FastAPI CLI take care of the main function. But we want to be careful with our
> dependencies, so define the main ourselves in order to avoid installing the FastAPI CLI.

We can then run our project with `uv`.

```bash
uv run src/niceapi/main.py
```

## Making it configurable

An important part of writing contianer-friendly APIs is easy settings
management. I personally like using file-based configs, instead of 
environment variables. This allows for changing the config at
runtime, which can be useful for things like changing the log level.

Let's write some code to make our app configurable with a `config.toml` file. Our
friendly HTTP server has a `/config` endpoint, which aims to expose all the
settings passed to the app. First, let's define the data model for the config under
`src/niceapi/config.py`.

```python
from pydantic import BaseModel

class Settings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
```

Let's load it in our `main.py`:

```python
import uvicorn
import tomllib
from fastapi import FastAPI
from niceapi import config

app = FastAPI()

settings = load_settings()

def load_settings() -> config.Settings:
    with open("config.toml") as f:
        raw_settings = tomllib.load(f)
    return config.Settings(**raw_settings)

@app.get("/config")
async def get_config() -> config.Settings:
    return settings

def main():
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)

if __name__ == "__main__":
    main()
```

Alright so we now have basic config. But. Global variables are incredibly
annoying, and this is **not testable at all**. How would we set the config for a
test? And if we set a precendent for global variables in our code now, other devs will feel entitled to do the same, and it will
become **a mess**. So don't do this. Let's see how we can do better with
dependencies.

## Testing with dependencies

To make our friendly API's `/config` endpoint testable, we're going to follow
the approach outlined here: (Settings in a
dependency)[https://fastapi.tiangolo.com/advanced/settings/#settings-in-a-dependency].
It essentially involves moving global variables to dependency functions.

To do so, we will restructure our `main.py` as follows:

```python
import uvicorn
import tomllib
from fastapi import FastAPI
from niceapi import config

app = FastAPI()

@lru_cache
def load_settings() -> config.Settings:
    with open("config.toml") as f:
        raw_settings = tomllib.load(f)
    return Settings(**raw_settings)

@app.get("/config")
async def get_config(
    settings: Annotated[config.Settings, Depends(load_settings)],
) -> config.Settings:
    return settings

def main():
    settings = load_settings()
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)

if __name__ == "__main__":
    main()
```

That's one global variable less. Let's see how we can test this:

```python
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from friendly import config, main

client = TestClient(main.app)


@pytest.fixture
def dummy_config():
    dummy_config = config.Settings(
        fileservice=config.FileService(datadir=Path("/dummydir/"))
    )
    with patch.dict(
        main.app.dependency_overrides, {main.load_settings: lambda: dummy_config}
    ):
        yield dummy_config


def test_config(dummy_config: config.Settings):
    response = client.get("/config")
    assert response.status_code == 200
    assert response.json() == dummy_config.model_dump(mode="json")
```

Let's go through this. First we create a `TestClient`, which allows for easily
communicating with the FastAPI `app` for testing purposes, via `get` or `post`
methods.

We then have the `dummy_config` pytest fixture. What this does is first creates a
`config.Settings` with some dummy data. It then uses `unittest.mock.patch` in
order to patch the dependency of the FastAPI `app` with the `dummy_config`. This
means that now, when `/config` gets called, it will load the `config.Settings`
from the dependency override that we've specified.

## Another test

## Dockerfile
