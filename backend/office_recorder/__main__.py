from __future__ import annotations

import uvicorn

from .config import load_config


def main() -> None:
    config = load_config()
    uvicorn.run(
        "office_recorder.main:app",
        host=config.host,
        port=config.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
