##Define um FakeMetadataRepository que implementa a mesma interface abstrata usada pela camada de serviço
## porém guarda os dados em memória, sso permite testar MetadataService e as rotas sem depender de uma instância real do MongoDB

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

import pytest
from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import DuplicateMetadataException, InvalidMetadataIdException
from app.repositories.metadata_repository import AbstractMetadataRepository


class FakeMetadataRepository(AbstractMetadataRepository):
    ##Replica MongoMetadataRepository

    def __init__(self) -> None:
        self._storage: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _validate_id(metadata_id: str) -> None:
        try:
            ObjectId(metadata_id)
        except (InvalidId, TypeError) as exc:
            raise InvalidMetadataIdException(metadata_id) from exc

    async def insert(self, document: Dict[str, Any]) -> Dict[str, Any]:
        for existing in self._storage.values():
            if (
                existing["database_name"] == document["database_name"]
                and existing["schema_name"] == document["schema_name"]
                and existing["table_name"] == document["table_name"]
            ):
                raise DuplicateMetadataException(
                    document["database_name"],
                    document["schema_name"],
                    document["table_name"],
                )
        object_id = ObjectId()
        document = dict(document)
        document["_id"] = object_id
        self._storage[str(object_id)] = document
        return document

    async def find_by_id(self, metadata_id: str) -> Optional[Dict[str, Any]]:
        self._validate_id(metadata_id)
        document = self._storage.get(metadata_id)
        return dict(document) if document else None

    async def find_by_full_name(
        self, database_name: str, schema_name: str, table_name: str
    ) -> Optional[Dict[str, Any]]:
        for document in self._storage.values():
            if (
                document["database_name"] == database_name
                and document["schema_name"] == schema_name
                and document["table_name"] == table_name
            ):
                return dict(document)
        return None

    async def list_paginated(
        self,
        page: int,
        page_size: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        documents = list(self._storage.values())
        # Filtro simplificado que aplica apenas correspondências exatas de owner.name/domain/tags
        
        if filters:
            if "domain" in filters:
                documents = [d for d in documents if d.get("domain") == filters["domain"]]
            if "tags" in filters:
                documents = [d for d in documents if filters["tags"] in d.get("tags", [])]
        total = len(documents)
        start = max(page - 1, 0) * page_size
        end = start + page_size
        return documents[start:end], total

    async def update(self, metadata_id: str, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self._validate_id(metadata_id)
        document = self._storage.get(metadata_id)
        if document is None:
            return None
        document.update(update_fields)
        self._storage[metadata_id] = document
        return dict(document)

    async def delete(self, metadata_id: str) -> bool:
        self._validate_id(metadata_id)
        return self._storage.pop(metadata_id, None) is not None


@pytest.fixture
def fake_repository() -> FakeMetadataRepository:
    return FakeMetadataRepository()


@pytest.fixture
def sample_create_payload() -> Dict[str, Any]:
    return {
        "database_name": "sales_lake",
        "schema_name": "gold",
        "table_name": f"fct_orders_{uuid.uuid4().hex[:6]}",
        "description": "Tabela fato com pedidos consolidados de vendas.",
        "domain": "vendas",
        "layer": "gold",
        "tags": ["vendas", "pedidos"],
        "classification": "internal",
        "owner": {
            "name": "Time de Dados de Vendas",
            "email": "dados-vendas@empresa.com",
            "team": "Data Engineering",
        },
        "schema_fields": [
            {
                "name": "order_id",
                "data_type": "string",
                "nullable": False,
                "description": "Identificador único do pedido.",
                "is_primary_key": True,
            }
        ],
    }
