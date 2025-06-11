from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from friendly import config, main

client = TestClient(main.app)


@pytest.fixture
def override_config():
    dummy_config = config.Settings(
        fileservice=config.FileService(datadir=Path("/dummydir/"))
    )
    with patch.dict(
        main.app.dependency_overrides, {main.load_settings: lambda: dummy_config}
    ):
        yield dummy_config


def test_config(override_config: config.Settings):
    response = client.get("/config")
    assert response.status_code == 200
    assert response.json() == override_config.model_dump(mode="json")
