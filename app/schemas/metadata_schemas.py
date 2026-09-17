from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.metadata import (
    DataClassification,
    DataLayer,
    Owner,
    SchemaField,
    SchemaVersion,
)


class MetadataCreateRequest(BaseModel):
    ##Payload de criação do metadado

    database_name: str = Field(..., min_length=1)
    schema_name: str = Field(..., min_length=1)
    table_name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    domain: Optional[str] = None
    layer: DataLayer = DataLayer.RAW
    tags: List[str] = Field(default_factory=list)
    classification: DataClassification = DataClassification.INTERNAL
    owner: Owner
    schema_fields: List[SchemaField] = Field(default_factory=list)


class MetadataUpdateRequest(BaseModel):
    ##Payload para atualização de um metadado

    description: Optional[str] = None
    domain: Optional[str] = None
    layer: Optional[DataLayer] = None
    tags: Optional[List[str]] = None
    classification: Optional[DataClassification] = None
    owner: Optional[Owner] = None
    schema_fields: Optional[List[SchemaField]] = None
    change_description: Optional[str] = Field(
        default=None,
        description="Descrição da mudança de schema",
    )


class MetadataResponse(BaseModel):
    ## modelo de metadado retornado pela API

    id: str = Field(..., description="Identificador único (ObjectId do MongoDB).")
    database_name: str
    schema_name: str
    table_name: str
    full_name: str
    description: str
    domain: Optional[str] = None
    layer: DataLayer
    tags: List[str]
    classification: DataClassification
    owner: Owner
    schema_fields: List[SchemaField]
    schema_version: int
    schema_history: List[SchemaVersion]
    created_at: datetime
    updated_at: datetime


class MetadataListResponse(BaseModel):
    ##listagem de metadados

    items: List[MetadataResponse]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):

    detail: str
