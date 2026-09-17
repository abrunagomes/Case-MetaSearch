from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import (
    DuplicateMetadataException,
    InvalidMetadataIdException,
    MetadataNotFoundException,
)


class AbstractMetadataRepository(ABC):
    ##Define uma interface abstrata para que a camada de serviço não dependa diretamente do MongoDB

    @abstractmethod
    async def insert(self, document: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def find_by_id(self, metadata_id: str) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    async def find_by_full_name(
        self, database_name: str, schema_name: str, table_name: str
    ) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    async def list_paginated(
        self,
        page: int,
        page_size: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        ...

    @abstractmethod
    async def update(self, metadata_id: str, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    async def delete(self, metadata_id: str) -> bool:
        ...


class MongoMetadataRepository(AbstractMetadataRepository):
    ##Implementação do repositório usando MongoDB

    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection = collection

    @staticmethod
    def _to_object_id(metadata_id: str) -> ObjectId:
        try:
            return ObjectId(metadata_id)
        except (InvalidId, TypeError) as exc:
            raise InvalidMetadataIdException(metadata_id) from exc

    async def insert(self, document: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = await self._collection.insert_one(document)
        except DuplicateKeyError as exc:
            raise DuplicateMetadataException(
                database=document.get("database_name", ""),
                schema=document.get("schema_name", ""),
                table_name=document.get("table_name", ""),
            ) from exc
        document["_id"] = result.inserted_id
        return document

    async def find_by_id(self, metadata_id: str) -> Optional[Dict[str, Any]]:
        object_id = self._to_object_id(metadata_id)
        return await self._collection.find_one({"_id": object_id})

    async def find_by_full_name(
        self, database_name: str, schema_name: str, table_name: str
    ) -> Optional[Dict[str, Any]]:
        return await self._collection.find_one(
            {
                "database_name": database_name,
                "schema_name": schema_name,
                "table_name": table_name,
            }
        )

    async def list_paginated(
        self,
        page: int,
        page_size: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = filters or {}
        total = await self._collection.count_documents(query)
        skip = max(page - 1, 0) * page_size
        cursor = (
            self._collection.find(query)
            .sort("updated_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        items = [document async for document in cursor]
        return items, total

    async def update(self, metadata_id: str, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        object_id = self._to_object_id(metadata_id)
        try:
            result = await self._collection.find_one_and_update(
                {"_id": object_id},
                {"$set": update_fields},
                return_document=True,
            )
        except DuplicateKeyError as exc:
            raise DuplicateMetadataException(
                database=update_fields.get("database_name", ""),
                schema=update_fields.get("schema_name", ""),
                table_name=update_fields.get("table_name", ""),
            ) from exc
        return result

    async def delete(self, metadata_id: str) -> bool:
        object_id = self._to_object_id(metadata_id)
        result = await self._collection.delete_one({"_id": object_id})
        return result.deleted_count > 0


def raise_not_found(metadata_id: str) -> None:
    raise MetadataNotFoundException(metadata_id)
