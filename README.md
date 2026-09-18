# Case-MetaSearch

### Contexto: 
Uma empresa está passando por uma dor de descoberta de dados e também de ownership 
das tabelas dentro do data lake. Perguntas como: Quem é o dono dessa tabela? Qual o 
contexto dessa tabela? Estão aparecendo diariamente. 
Para isso, você foi designado a construir um microserviço que servirá como catálogo de 
metadados das tabelas de dados da empresa. Esse serviço será consumido por outras 
equipes para descobrir, entender e governar os dados disponíveis no ecossistema. 
O objetivo é que qualquer pessoa consiga buscar uma tabela e entender o contexto da 
tabela, entender sua estrutura, saber quem é o responsável, acompanhar a evolução do 
schema ao longo do tempo e outras informações relevantes. 

### Solução técnica: 
Desenvolver uma aplicação usando o framework FastAPI para realizar operações CRUD 
(Create, Read, Update, Delete) em uma entidade de "Metadado". O candidato deve persistir 
os dados no banco de dados MongoDB. 
A modelagem do banco de dados fica a critério do candidato. Podendo ter uma ou mais 
collections. 

### Requisitos Técnicos: 
1. Utilizar FastAPI como framework. 
2. Utilizar o conceito de orientação a objetos no desenvolvimento da aplicação. 
3. Persistir os dados em um banco de dados MongoDB. 
4. Implementar as operações CRUD para a entidade "Metadado" (GET, POST, PUT, 
DELETE). 
5. Implementar testes unitários 
6. O código deve ser bem estruturado e seguir as melhores práticas de programação. 
7. O código deve seguir algum padrão de projeto conhecido pela comunidade. 

### Endpoints: 
1. POST /metadata: Cadastrar um novo metadado de tabela 
2. GET /metadata: Listagem dos metadados 
3. GET /metadata/{metadata_id}: Detalhes de um metadado 
4. PUT /metadata/{metadata_id}: Atualizar metadados 
5. DELETE /metadata/{metadata_id}: Deletar metadados 

## Metadata Service
É um microserviço de catálogo de metadados que realiza buscas nas tabelas de um data lake, permitindo entender seu contexto, estrutura e owner, além de acompanhar a evolução do esquema pelo registro de histórico.

### Stack
FastAPI: framework para construção da API assíncrona
MongoDB: base de dados para persistir os metadados
Pydantic: para validação e modelagem de dados
Pytest: para os testes unitários

## Arquitetura

### App
main.py: orquestração da aplicação
core/exceptions.py: trata as exceções do domínio
db/mongodb.py: Singleton de conexão com o MongoDB
models/metadata.py: modelagemde metadados
schemas/metadata_schemas.py: DTOs da resquest e response
repositories/metadata_repository.py: repositório de exceções de domínio
services/metadata_service.py: regras de negócio das chamadas
api/dependencies.py: provider de dependências da API
api/routes/metadata_routes.py: controller das rotas

### Tests
conftest.py: cria um repositório fake em memória
test_models.py: testes das entidades de domínios
test_metadata_service: teste das camadas de serviço
test_metadata_routes.py: teste de integração das rotas

### Modelagem de dados

Uma única collection é usada com o schema atual e o histórico de versões do documento da tabela. Leitura conjunta para facilitar a consulta


### Como executar

python -m venv .venv
source .venv/bin/activate  #para criar o virtual environment

pip install -r requirements-dev.txt
cp .env .env       #para instalar dependências e configurar variáveis de ambiente locais

uvicorn app.main:app --reload


## Testes
pip install -r requirements-dev.txt
pytest -v


**Criar um metadado:**

curl -X POST http://localhost:8000/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "database_name": "sales_lake",
    "schema_name": "gold",
    "table_name": "fct_orders",
    "description": "Tabela fato com pedidos consolidados de vendas.",
    "domain": "vendas",
    "layer": "gold",
    "tags": ["vendas", "pedidos"],
    "owner": {"name": "Time de Dados de Vendas", "email": "dados-vendas@empresa.com"},
    "schema_fields": [
      {"name": "order_id", "data_type": "string", "nullable": false, "is_primary_key": true}
    ]
  }'

**Listagem de metadados por filtro:**


curl "http://localhost:8000/metadata?domain=vendas&page=1&page_size=10"


**Atualizar o schema:**

curl -X PUT http://localhost:8000/metadata/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "schema_fields": [
      {"name": "order_id", "data_type": "string", "is_primary_key": true},
      {"name": "order_status", "data_type": "string", "nullable": false}
    ],
    "change_description": "Adicionada coluna order_status."
  }'