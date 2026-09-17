class DataCatalogException(Exception):
    "Exceção base."


class MetadataNotFoundException(DataCatalogException):
    ##quando um metadado não é encontrado pelo identificador

    def __init__(self, metadata_id: str):
        self.metadata_id = metadata_id
        super().__init__(f"Metadado com id '{metadata_id}' não foi encontrado.")


class DuplicateMetadataException(DataCatalogException):
    ##quando já existe um metadado para a mesma tabela

    def __init__(self, database: str, schema: str, table_name: str):
        self.database = database
        self.schema = schema
        self.table_name = table_name
        super().__init__(
            f"Já existe um metadado cadastrado para a tabela "
            f"'{database}.{schema}.{table_name}'."
        )


class InvalidMetadataIdException(DataCatalogException):
    ##quando o identificador informado não é um ObjectId válido

    def __init__(self, metadata_id: str):
        self.metadata_id = metadata_id
        super().__init__(f"O identificador '{metadata_id}' é inválido.")
