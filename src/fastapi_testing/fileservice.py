from pathlib import Path

from fastapi import responses


class Client:
    def __init__(self, datadir: Path) -> None:
        self.datadir = datadir

    def download(self, filepath: str) -> responses.Response:
        p = self.datadir / filepath
        try:
            f = p.open("rb")
        except FileNotFoundError:
            return responses.Response("file not found", status_code=404)
        except IsADirectoryError:
            return responses.Response("it's a directory", status_code=400)
        return responses.StreamingResponse(_iterfile(f))


def _iterfile(f):
    yield from f
    f.close()
