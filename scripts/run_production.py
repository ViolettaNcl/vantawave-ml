from __future__ import annotations

import uvicorn

from vantawave.core.settings import load_settings


def main():
    settings = load_settings()
    uvicorn.run(
        "vantawave.api.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
