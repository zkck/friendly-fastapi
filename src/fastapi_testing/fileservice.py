from pathlib import Path

from fastapi import responses


class Client:
    def __init__(self, datadir: str) -> None:
        self.datadir = datadir

    def download(self, filename: str) -> responses.Response:
        # allow directory traversal :)
        p = Path(self.datadir, filename)
        try:
            f = p.open("rb")
        except FileNotFoundError:
            return responses.Response("file not found", status_code=404)
        return responses.StreamingResponse(_iterfile(f))


def _iterfile(f):
    yield from f
    f.close()
