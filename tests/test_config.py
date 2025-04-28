import pytest
from fastapi.testclient import TestClient

import fastapi_testing.config
import fastapi_testing.main

client = TestClient(fastapi_testing.main.app)


@pytest.fixture
def custom_config():
    config = fastapi_testing.config.Settings(host="8.8.8.8", port=9999)
    fastapi_testing.main.app.dependency_overrides[fastapi_testing.main.get_settings] = (
        lambda: config
    )
    yield config
    fastapi_testing.main.app.dependency_overrides.clear()


def test_config(custom_config: fastapi_testing.config.Settings):
    response = client.get("/config")
    assert response.status_code == 200
    assert response.json() == custom_config.model_dump(mode="json")
