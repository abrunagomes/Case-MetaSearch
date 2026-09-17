from __future__ import annotations
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class MongoDBConnectionManager:
    ##encapsula AsyncIOMotorClient e expõe os métodos para conectar, desconectar e obter metadados
    _instance: Optional["MongoDBConnectionManager"] = None

    def __new__(cls, *args, **kwargs) -> "MongoDBConnectionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, settings: Optional[Settings] = None) -> None:
        if self._initialized:
            return
        self._settings = settings or get_settings()
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._initialized = True

    async def connect(self) -> None:
        ##Abre a conexão com o Mongo se ainda não estiver aberta
        if self._client is not None:
            return
        logger.info("Conectando ao MongoDB em %s", self._settings.mongodb_uri)
        self._client = AsyncIOMotorClient(self._settings.mongodb_uri)
        self._database = self._client[self._settings.mongodb_database]
        # Garante índices essenciais (idempotente).
        await self._ensure_indexes()

    async def disconnect(self) -> None:
        ##Encerra a conexão com o MongoDB.
        if self._client is not None:
            logger.info("Encerrando conexão com o MongoDB.")
            self._client.close()
            self._client = None
            self._database = None

    async def _ensure_indexes(self) -> None:
        ##Cria os índices necessários para a colection de metadados
        collection = self.get_collection()
        await collection.create_index(
            [("database_name", 1), ("schema_name", 1), ("table_name", 1)],
            unique=True,
            name="uq_database_schema_table",
        )
        await collection.create_index([("owner", 1)], name="idx_owner")
        await collection.create_index([("tags", 1)], name="idx_tags")

    def get_database(self) -> AsyncIOMotorDatabase:
        ##Retorna o handle do banco
        if self._database is None:
            raise RuntimeError(
                "A conexão com o MongoDB ainda não foi estabelecida. Inicie connect() "
            )
        return self._database

    def get_collection(self) -> AsyncIOMotorCollection:
        ##Retorna o handle da colection de metadados
        return self.get_database()[self._settings.mongodb_collection]


def get_mongo_manager() -> MongoDBConnectionManager:
    ##Dependency provider para o gerenciador da conexão
    return MongoDBConnectionManager()
