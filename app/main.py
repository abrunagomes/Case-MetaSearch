from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.metadata_routes import router as metadata_router
from app.core.config import get_settings
from app.core.exceptions import DataCatalogException
from app.db.mongodb import MongoDBConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    ##Gerencia a abertura/fechamento da conexão com o MongoDB
    mongo_manager = MongoDBConnectionManager()
    await mongo_manager.connect()
    yield
    await mongo_manager.disconnect()


def create_app() -> FastAPI:
    ##Factory function que configura a aplicação, Factory facilita a criação de instâncias isoladas em testes
    
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.include_router(metadata_router)

    @app.exception_handler(DataCatalogException)
    async def data_catalog_exception_handler(request: Request, exc: DataCatalogException):
        
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "service": settings.app_name, "version": settings.app_version}

    return app


app = create_app()
