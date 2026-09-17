## usa o FakeMetadataRepository para isolar a camada de serviço de qualquer dependência do MongoDB

import pytest

from app.core.exceptions import (
    DuplicateMetadataException,
    InvalidMetadataIdException,
    MetadataNotFoundException,
)
from app.schemas.metadata_schemas import MetadataCreateRequest, MetadataUpdateRequest
from app.services.metadata_service import MetadataService


@pytest.fixture
def service(fake_repository) -> MetadataService:
    return MetadataService(fake_repository)


class TestCreateMetadata:
    @pytest.mark.asyncio
    async def test_create_metadata_returns_response_with_generated_id(
        self, service, sample_create_payload
    ):
        request = MetadataCreateRequest(**sample_create_payload)
        response = await service.create_metadata(request)

        assert response.id is not None
        assert response.table_name == sample_create_payload["table_name"].lower()
        assert response.schema_version == 1
        assert response.full_name.endswith(sample_create_payload["table_name"].lower())

    @pytest.mark.asyncio
    async def test_create_duplicate_table_raises_exception(self, service, sample_create_payload):
        request = MetadataCreateRequest(**sample_create_payload)
        await service.create_metadata(request)

        with pytest.raises(DuplicateMetadataException):
            await service.create_metadata(request)


class TestGetMetadata:
    @pytest.mark.asyncio
    async def test_get_existing_metadata(self, service, sample_create_payload):
        request = MetadataCreateRequest(**sample_create_payload)
        created = await service.create_metadata(request)

        fetched = await service.get_metadata(created.id)
        assert fetched.id == created.id
        assert fetched.description == sample_create_payload["description"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_metadata_raises_not_found(self, service):
        from bson import ObjectId

        with pytest.raises(MetadataNotFoundException):
            await service.get_metadata(str(ObjectId()))

    @pytest.mark.asyncio
    async def test_get_metadata_with_invalid_id_raises_invalid_id_exception(self, service):
        with pytest.raises(InvalidMetadataIdException):
            await service.get_metadata("nao-e-um-object-id-valido")


class TestListMetadata:
    @pytest.mark.asyncio
    async def test_list_metadata_returns_created_items(self, service, sample_create_payload):
        request = MetadataCreateRequest(**sample_create_payload)
        await service.create_metadata(request)

        result = await service.list_metadata(page=1, page_size=10)
        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_list_metadata_filters_by_domain(self, service, sample_create_payload):
        request = MetadataCreateRequest(**sample_create_payload)
        await service.create_metadata(request)

        matching = await service.list_metadata(page=1, page_size=10, domain="vendas")
        non_matching = await service.list_metadata(page=1, page_size=10, domain="rh")

        assert matching.total == 1
        assert non_matching.total == 0


class TestUpdateMetadata:
    @pytest.mark.asyncio
    async def test_update_description(self, service, sample_create_payload):
        request = MetadataCreateRequest(**sample_create_payload)
        created = await service.create_metadata(request)

        update_request = MetadataUpdateRequest(description="Nova descrição da tabela.")
        updated = await service.update_metadata(created.id, update_request)

        assert updated.description == "Nova descrição da tabela."
        assert updated.schema_version == 1 

    @pytest.mark.asyncio
    async def test_update_schema_fields_bumps_version_and_archives_history(
        self, service, sample_create_payload
    ):
        request = MetadataCreateRequest(**sample_create_payload)
        created = await service.create_metadata(request)

        update_request = MetadataUpdateRequest(
            schema_fields=[
                {"name": "order_id", "data_type": "string", "is_primary_key": True},
                {"name": "order_status", "data_type": "string", "nullable": False},
            ],
            change_description="Adicionada coluna order_status.",
        )
        updated = await service.update_metadata(created.id, update_request)

        assert updated.schema_version == 2
        assert len(updated.schema_history) == 1
        assert updated.schema_history[0].change_description == "Adicionada coluna order_status."
        assert len(updated.schema_fields) == 2

    @pytest.mark.asyncio
    async def test_update_nonexistent_metadata_raises_not_found(self, service):
        from bson import ObjectId

        update_request = MetadataUpdateRequest(description="Não importa.")
        with pytest.raises(MetadataNotFoundException):
            await service.update_metadata(str(ObjectId()), update_request)


class TestDeleteMetadata:
    @pytest.mark.asyncio
    async def test_delete_existing_metadata(self, service, sample_create_payload):
        request = MetadataCreateRequest(**sample_create_payload)
        created = await service.create_metadata(request)

        await service.delete_metadata(created.id)

        with pytest.raises(MetadataNotFoundException):
            await service.get_metadata(created.id)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_metadata_raises_not_found(self, service):
        from bson import ObjectId

        with pytest.raises(MetadataNotFoundException):
            await service.delete_metadata(str(ObjectId()))
