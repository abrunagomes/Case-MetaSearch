## Testes de TableMetadata
from app.models.metadata import Owner, SchemaField, TableMetadata


def _build_entity(**overrides) -> TableMetadata:
    defaults = dict(
        database_name="Sales_Lake",
        schema_name="GOLD",
        table_name="Fct_Orders",
        description="Tabela fato de pedidos.",
        owner=Owner(name="Time de Vendas"),
        schema_fields=[
            SchemaField(name="order_id", data_type="string", nullable=False, is_primary_key=True)
        ],
    )
    defaults.update(overrides)
    return TableMetadata(**defaults)


class TestTableMetadata:
    def test_identifiers_are_normalized_to_lowercase(self):
        entity = _build_entity()
        assert entity.database_name == "sales_lake"
        assert entity.schema_name == "gold"
        assert entity.table_name == "fct_orders"

    def test_full_name_property(self):
        entity = _build_entity()
        assert entity.full_name == "sales_lake.gold.fct_orders"

    def test_initial_schema_version_is_one_with_empty_history(self):
        entity = _build_entity()
        assert entity.schema_version == 1
        assert entity.schema_history == []

    def test_register_schema_change_archives_previous_version(self):
        entity = _build_entity()
        original_fields = entity.schema_fields

        new_fields = [
            SchemaField(name="order_id", data_type="string", is_primary_key=True),
            SchemaField(name="order_status", data_type="string", nullable=False),
        ]
        entity.register_schema_change(new_fields, change_description="Adicionada coluna de status.")

        assert entity.schema_version == 2
        assert entity.schema_fields == new_fields
        assert len(entity.schema_history) == 1

        archived_version = entity.schema_history[0]
        assert archived_version.version == 1
        assert archived_version.fields == original_fields
        assert archived_version.change_description == "Adicionada coluna de status."

    def test_register_schema_change_multiple_times_accumulates_history(self):
        entity = _build_entity()

        entity.register_schema_change([SchemaField(name="a", data_type="string")])
        entity.register_schema_change([SchemaField(name="b", data_type="int")])

        assert entity.schema_version == 3
        assert len(entity.schema_history) == 2
        assert [v.version for v in entity.schema_history] == [1, 2]
