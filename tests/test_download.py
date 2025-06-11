from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi import responses
from fastapi.testclient import TestClient

from friendly import main

client = TestClient(main.app)


class InMemoryFileservice:
    def __init__(self) -> None:
        self.d: dict[str, bytes] = {}

    def download(self, filepath: str) -> responses.Response:
        return responses.StreamingResponse(BytesIO(self.d[filepath]))


@pytest.fixture
def override_fileservice():
    inmem = InMemoryFileservice()
    with patch.dict(
        main.app.dependency_overrides, {main.get_fileservice_client: lambda: inmem}
    ):
        yield inmem.d


def test_download(override_fileservice: dict):
    override_fileservice["myfile"] = b"hello"
    response = client.get("/download/myfile")
    assert response.status_code == 200
    assert response.content == b"hello"
