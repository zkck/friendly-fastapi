from pathlib import Path

from fastapi import responses


class Client:
    def __init__(self, datadir: str) -> None:
        self.resolved_datadir = Path(datadir).resolve()

    def download(self, filepath: str) -> responses.Response:
        p = (self.resolved_datadir / filepath).resolve()
        if not p.is_relative_to(self.resolved_datadir):
            return responses.Response("attempted directory traversal", status_code=403)
        try:
            f = p.open("rb")
        except FileNotFoundError:
            return responses.Response("file not found", status_code=404)
        return responses.StreamingResponse(_iterfile(f))


def _iterfile(f):
    yield from f
    f.close()
