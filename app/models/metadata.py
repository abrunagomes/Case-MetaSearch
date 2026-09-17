##modela os metadados e usa a collection metadata fazendo embedding dos metadados, schema e schema_history

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DataClassification(str, Enum):
    ##Classificação de sensibilidade dos dados

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DataLayer(str, Enum):

    RAW = "raw"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    ANALYTICS = "analytics"


class SchemaField(BaseModel):
    ##Representa uma coluna/campo do schema

    name: str = Field(..., min_length=1, description="Nome da coluna.")
    data_type: str = Field(..., description="Tipo de dado (ex: string, int, timestamp)")
    nullable: bool = Field(default=True, description="Se a coluna aceita valores nulos")
    description: Optional[str] = Field(default=None, description="Descrição de negócio da coluna")
    is_primary_key: bool = Field(default=False, description="Se a coluna faz parte da PK")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "order_id",
            "data_type": "string",
            "nullable": False,
            "description": "Identificador único do pedido",
            "is_primary_key": True,
        }
    })


class SchemaVersion(BaseModel):
    ##Cada vez que o schema de uma tabela é alterado, a versão anterior é arquivada aqui

    version: int = Field(..., ge=1, description="Número sequencial da versão")
    fields: List[SchemaField] = Field(default_factory=list)
    changed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    change_description: Optional[str] = Field(
        default=None, description="Descrição do que mudou nessa versão"
    )


class Owner(BaseModel):
    ##define o owner da tabela

    name: str = Field(..., min_length=1, description="Nome do responsável ou time")
    email: Optional[str] = Field(default=None, description="E-mail de contato")
    team: Optional[str] = Field(default=None, description="Time/squad responsável")


class TableMetadata(BaseModel):
    ##define as entidades da tabela

    # Identificação da tabela
    database_name: str = Field(..., min_length=1, description="Nome do banco/catálogo")
    schema_name: str = Field(..., min_length=1, description="Nome do schema")
    table_name: str = Field(..., min_length=1, description="Nome da tabela")

    # Contexto de negócio
    description: str = Field(..., min_length=1, description="Descrição da tabela")
    domain: Optional[str] = Field(default=None, description="Equipe de negócio")
    layer: DataLayer = Field(default=DataLayer.RAW, description="Camada de dados")
    tags: List[str] = Field(default_factory=list, description="Tags para busca")
    classification: DataClassification = Field(
        default=DataClassification.INTERNAL, description="Sensibilidade dos dados"
    )

    owner: Owner = Field(..., description="Responsável pela tabela")

    # Estrutura da tabela
    schema_fields: List[SchemaField] = Field(
        default_factory=list, description="Colunas do schema atual"
    )
    schema_version: int = Field(default=1, ge=1, description="Versão atual do schema")
    schema_history: List[SchemaVersion] = Field(
        default_factory=list, description="Histórico de versões do schema"
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("database_name", "schema_name", "table_name")
    @classmethod
    def _normalize_identifier(cls, value: str) -> str:
        ##Normaliza IDs da tabela pra minúsculas e sem espaços
        return value.strip().lower()

    @property
    def full_name(self) -> str:
        ##Nome da tabela
        return f"{self.database_name}.{self.schema_name}.{self.table_name}"

    def register_schema_change(
        self, new_fields: List[SchemaField], change_description: Optional[str] = None
    ) -> None:
        ##Aplica mudança do schema, arquivando a versão anterior no histórico
        previous_version = SchemaVersion(
            version=self.schema_version,
            fields=self.schema_fields,
            changed_at=self.updated_at,
            change_description=change_description,
        )
        self.schema_history.append(previous_version)
        self.schema_fields = new_fields
        self.schema_version += 1
        self.updated_at = datetime.now(timezone.utc)

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "database_name": "sales_lake",
                "schema_name": "gold",
                "table_name": "fct_orders",
                "description": "Tabela fato com pedidos consolidados de vendas.",
                "domain": "vendas",
                "layer": "gold",
                "tags": ["vendas", "pedidos", "financeiro"],
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
        },
    )
