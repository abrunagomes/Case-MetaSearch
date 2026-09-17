from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongodb import MongoDBConnectionManager, get_mongo_manager
from app.repositories.metadata_repository import (
    AbstractMetadataRepository,
    MongoMetadataRepository,
)
from app.services.metadata_service import MetadataService


def get_metadata_collection(
    mongo_manager: MongoDBConnectionManager = None,
) -> AsyncIOMotorCollection:
    ##Retorna a collection de metadados
    manager = mongo_manager or get_mongo_manager()
    return manager.get_collection()


def get_metadata_repository() -> AbstractMetadataRepository:
    ##implementação do repositório de metadados
    collection = get_metadata_collection()
    return MongoMetadataRepository(collection)


def get_metadata_service() -> MetadataService:
    ##Fornece uma instância do serviço de metadados, com o repositório injetado
    repository = get_metadata_repository()
    return MetadataService(repository)
