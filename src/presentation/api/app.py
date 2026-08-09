import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain.application.use_cases import CategorizationService
from presentation.api.v1.routes.classification import router as classification_router
from shared.utils import logger

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)
ANCHORS_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "knowledge_anchors.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loading embedding model and knowledge anchors from {ANCHORS_PATH}")
    app.state.categorization_service = CategorizationService(anchors_path=ANCHORS_PATH)
    logger.info("Categorization service ready.")
    yield
    app.state.categorization_service = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Photus B - Categorization API",
        description="Recebe uma frase em linguagem natural e devolve a categoria semântica mais próxima.",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/health", tags=["health"])
    def health() -> dict:
        ready = getattr(app.state, "categorization_service", None) is not None
        return {"status": "ok" if ready else "starting"}

    app.include_router(classification_router, prefix="/v1")

    return app


app = create_app()
