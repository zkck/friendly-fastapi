from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from fastapi_testing import config, main

client = TestClient(main.app)


@pytest.fixture
def custom_config():
    c = config.Settings(fileservice=config.FileService(datadir="/dummydir/"))
    with patch.dict(main.app.dependency_overrides, {main.get_settings: lambda: c}):
        yield c


def test_config(custom_config: config.Settings):
    response = client.get("/config")
    assert response.status_code == 200
    assert response.json() == custom_config.model_dump(mode="json")
