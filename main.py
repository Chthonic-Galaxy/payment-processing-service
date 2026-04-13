from fastapi import FastAPI

from src.api.v1.router import router as router_v1
from src.config import settings
from src.infrastructure.logger import setup_logging

setup_logging(settings.log_level)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Async Payment Processing Service",
        description="High-load fintech microservice",
        version="1.0.0",
    )

    app.include_router(router_v1)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
