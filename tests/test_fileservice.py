from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from friendly import config, main

client = TestClient(main.app)


@pytest.fixture
def override_datadir(tmpdir):
    datadir = Path(tmpdir / "data")
    datadir.mkdir()
    c = config.Settings(fileservice=config.FileService(datadir=datadir))
    with patch.dict(main.app.dependency_overrides, {main.load_settings: lambda: c}):
        yield c


@pytest.mark.xfail
def test_prevent_directory_traversal(override_datadir: config.Settings, tmpdir):
    with (tmpdir / "target.txt").open("w") as f:
        f.write("secret")
    assert client.get("/download/%2E%2E/target.txt").status_code != 200
