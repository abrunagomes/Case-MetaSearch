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