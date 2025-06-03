from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi import responses
from fastapi.testclient import TestClient

from fastapi_testing import main

client = TestClient(main.app)


class InMemoryFileservice:
    def __init__(self) -> None:
        self.d: dict[str, bytes] = {}

    def download(self, filepath: str) -> responses.Response:
        return responses.StreamingResponse(BytesIO(self.d[filepath]))


@pytest.fixture
def fileservice_inmem():
    inmem = InMemoryFileservice()
    with patch.dict(
        main.app.dependency_overrides, {main.get_fileservice_client: lambda: inmem}
    ):
        yield inmem.d


def test_download(fileservice_inmem: dict):
    fileservice_inmem["config.toml"] = b"hello"

    response = client.get("/download/config.toml")
    assert response.status_code == 200
    assert response.content == b"hello"
