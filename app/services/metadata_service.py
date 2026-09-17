from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.exceptions import MetadataNotFoundException
from app.models.metadata import TableMetadata
from app.repositories.metadata_repository import AbstractMetadataRepository
from app.schemas.metadata_schemas import (
    MetadataCreateRequest,
    MetadataListResponse,
    MetadataResponse,
    MetadataUpdateRequest,
)


class MetadataService:
    ##CRUD dos metadados

    def __init__(self, repository: AbstractMetadataRepository):
        self._repository = repository

    async def create_metadata(self, request: MetadataCreateRequest) -> MetadataResponse:
        entity = TableMetadata(
            database_name=request.database_name,
            schema_name=request.schema_name,
            table_name=request.table_name,
            description=request.description,
            domain=request.domain,
            layer=request.layer,
            tags=request.tags,
            classification=request.classification,
            owner=request.owner,
            schema_fields=request.schema_fields,
        )
        document = entity.model_dump()
        created_document = await self._repository.insert(document)
        return self._to_response(created_document)

    async def get_metadata(self, metadata_id: str) -> MetadataResponse:
        ##Busca um metadado pelo id, lança 404 se não existir
        document = await self._repository.find_by_id(metadata_id)
        if document is None:
            raise MetadataNotFoundException(metadata_id)
        return self._to_response(document)

    async def list_metadata(
        self,
        page: int,
        page_size: int,
        owner: Optional[str] = None,
        domain: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> MetadataListResponse:
        ##Lista metadados de forma paginada, com filtros opcionais
        
        filters: Dict[str, Any] = {}
        if owner:
            filters["owner.name"] = {"$regex": owner, "$options": "i"}
        if domain:
            filters["domain"] = domain
        if tag:
            filters["tags"] = tag
        if search:
            filters["$or"] = [
                {"table_name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]

        documents, total = await self._repository.list_paginated(page, page_size, filters)
        items = [self._to_response(document) for document in documents]
        return MetadataListResponse(items=items, total=total, page=page, page_size=page_size)

    async def update_metadata(
        self, metadata_id: str, request: MetadataUpdateRequest
    ) -> MetadataResponse:
        ##Atualiza um metadado e arquiva a mudança no schema_history
        
        existing_document = await self._repository.find_by_id(metadata_id)
        if existing_document is None:
            raise MetadataNotFoundException(metadata_id)

        entity = TableMetadata(**existing_document)
        update_data = request.model_dump(
            exclude_unset=True, exclude={"change_description", "schema_fields"}
        )

        for field_name, value in update_data.items():
            setattr(entity, field_name, value)

        # SchemaField tipados usando o objeto original (em vez do dict produzido por model_dump) 
        # pra que register_schema_change armazene instâncias corretamente tipadas
        
        if request.schema_fields is not None:
            entity.register_schema_change(
                new_fields=request.schema_fields,
                change_description=request.change_description,
            )
        else:
            from datetime import datetime, timezone

            entity.updated_at = datetime.now(timezone.utc)

        updated_fields = entity.model_dump(exclude={"database_name", "schema_name", "table_name"})
        updated_document = await self._repository.update(metadata_id, updated_fields)
        if updated_document is None:
            raise MetadataNotFoundException(metadata_id)
        return self._to_response(updated_document)

    async def delete_metadata(self, metadata_id: str) -> None:
        ##Remove um metadado pelo identificador. Lança 404 se não existir
        deleted = await self._repository.delete(metadata_id)
        if not deleted:
            raise MetadataNotFoundException(metadata_id)

    @staticmethod
    def _to_response(document: Dict[str, Any]) -> MetadataResponse:
        ##Converte um documento MongoDB (dict) em um DTO de resposta
        document = dict(document)
        object_id = document.pop("_id")
        entity = TableMetadata(**document)
        return MetadataResponse(
            id=str(object_id),
            database_name=entity.database_name,
            schema_name=entity.schema_name,
            table_name=entity.table_name,
            full_name=entity.full_name,
            description=entity.description,
            domain=entity.domain,
            layer=entity.layer,
            tags=entity.tags,
            classification=entity.classification,
            owner=entity.owner,
            schema_fields=entity.schema_fields,
            schema_version=entity.schema_version,
            schema_history=entity.schema_history,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
