from pathlib import Path

from fastapi.responses import StreamingResponse


class Client:
    def __init__(self, datadir: str) -> None:
        self.datadir = datadir

    def _iterfile(self, filename: str):
        with Path(self.datadir, filename).open("rb") as f:
            yield from f

    def download(self, filename: str) -> StreamingResponse:
        return StreamingResponse(self._iterfile(filename))
