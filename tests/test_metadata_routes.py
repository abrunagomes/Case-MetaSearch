## usa TestClient do FastAPI e sobrescreve a dependência get_metadata_service pra injetar um MetadataService 
## construído sobre o FakeMetadataRepository, evitando conexão real com MongoDB .

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.api.dependencies import get_metadata_service
from app.main import create_app
from app.services.metadata_service import MetadataService


@pytest.fixture
def client(fake_repository):
    app = create_app()
    service = MetadataService(fake_repository)
    app.dependency_overrides[get_metadata_service] = lambda: service
    test_client = TestClient(app)
    yield test_client


class TestPostMetadata:
    def test_create_metadata_returns_201(self, client, sample_create_payload):
        response = client.post("/metadata", json=sample_create_payload)
        assert response.status_code == 201
        body = response.json()
        assert body["table_name"] == sample_create_payload["table_name"].lower()
        assert "id" in body

    def test_create_duplicate_metadata_returns_409(self, client, sample_create_payload):
        client.post("/metadata", json=sample_create_payload)
        response = client.post("/metadata", json=sample_create_payload)
        assert response.status_code == 409

    def test_create_metadata_with_missing_field_returns_422(self, client, sample_create_payload):
        payload = dict(sample_create_payload)
        payload.pop("description")
        response = client.post("/metadata", json=payload)
        assert response.status_code == 422


class TestGetMetadata:
    def test_get_metadata_by_id_returns_200(self, client, sample_create_payload):
        created = client.post("/metadata", json=sample_create_payload).json()
        response = client.get(f"/metadata/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_metadata_not_found_returns_404(self, client):
        response = client.get(f"/metadata/{ObjectId()}")
        assert response.status_code == 404

    def test_get_metadata_invalid_id_returns_400(self, client):
        response = client.get("/metadata/id-invalido")
        assert response.status_code == 400


class TestListMetadata:
    def test_list_metadata_returns_200_with_pagination(self, client, sample_create_payload):
        client.post("/metadata", json=sample_create_payload)
        response = client.get("/metadata", params={"page": 1, "page_size": 10})
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["page"] == 1
        assert len(body["items"]) == 1


class TestPutMetadata:
    def test_update_metadata_description_returns_200(self, client, sample_create_payload):
        created = client.post("/metadata", json=sample_create_payload).json()
        response = client.put(
            f"/metadata/{created['id']}", json={"description": "Descrição atualizada."}
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Descrição atualizada."

    def test_update_metadata_not_found_returns_404(self, client):
        response = client.put(
            f"/metadata/{ObjectId()}", json={"description": "Não importa."}
        )
        assert response.status_code == 404

    def test_update_schema_fields_bumps_schema_version(self, client, sample_create_payload):
        created = client.post("/metadata", json=sample_create_payload).json()
        response = client.put(
            f"/metadata/{created['id']}",
            json={
                "schema_fields": [
                    {"name": "order_id", "data_type": "string", "is_primary_key": True},
                    {"name": "order_status", "data_type": "string"},
                ],
                "change_description": "Adicionada coluna order_status.",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["schema_version"] == 2
        assert len(body["schema_history"]) == 1


class TestDeleteMetadata:
    def test_delete_metadata_returns_204(self, client, sample_create_payload):
        created = client.post("/metadata", json=sample_create_payload).json()
        response = client.delete(f"/metadata/{created['id']}")
        assert response.status_code == 204

        follow_up = client.get(f"/metadata/{created['id']}")
        assert follow_up.status_code == 404

    def test_delete_nonexistent_metadata_returns_404(self, client):
        response = client.delete(f"/metadata/{ObjectId()}")
        assert response.status_code == 404


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
