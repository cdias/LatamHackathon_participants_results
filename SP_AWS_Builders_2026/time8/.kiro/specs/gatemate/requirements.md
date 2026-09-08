# Requirements Document

## Introduction

O **GateMate** é um concierge de IA pessoal para passageiros que enfrentam atrasos de voos ou conexões curtas em aeroportos. O passageiro informa seu código de reserva e descreve em linguagem natural o que precisa; o sistema retorna um plano de ação empático de 3 passos com serviços e recomendações próximas no aeroporto.

O sistema é construído com Python (FastAPI) + React (Vite) + TiDB Cloud Starter + Amazon Bedrock, desenvolvido para o Hackathon TiDB × AWS em São Paulo (02/09/2026).

---

## Glossary

- **GateMate**: Nome da aplicação — o sistema completo descrito neste documento.
- **API**: Serviço backend FastAPI exposto na porta 8000.
- **Frontend**: Aplicação React (Vite) que serve a interface do usuário.
- **Passageiro**: Usuário final que interage com o GateMate via código de reserva.
- **Código de reserva**: Identificador único da reserva do passageiro na tabela `booking`.
- **Serviço de aeroporto**: Estabelecimento ou recurso disponível no aeroporto (café, carregador, lounge, farmácia, portão etc.), armazenado na tabela `airport_services`.
- **Plano de ação**: Resposta estruturada em 3 passos gerada pelo modelo de linguagem.
- **TiDB**: Banco de dados distribuído compatível com MySQL, hospedado no TiDB Cloud Starter na região `sa-east-1`.
- **Bedrock_Client**: Módulo responsável pela comunicação com o Amazon Bedrock na região `ap-southeast-1`.
- **Vector_Search**: Mecanismo de busca semântica baseado em embeddings vetoriais com `VEC_COSINE_DISTANCE` no TiDB.
- **Embedding**: Representação vetorial de dimensão 1024 gerada pelo modelo `amazon.titan-embed-text-v2` via função `EMBED_TEXT` do TiDB.
- **DB_Connection**: Módulo de conexão com o TiDB Cloud via SSL (`ssl={"ca": "/etc/ssl/cert.pem"}`).
- **env_file**: Arquivo `.env` com credenciais sensíveis, nunca versionado.
- **env_example**: Arquivo `.env.example` com todas as variáveis necessárias sem valores secretos, versionado no repositório.

---

## Requirements

### Requisito 1: Consulta de Reserva e Status do Voo

**User Story:** Como passageiro, quero informar meu código de reserva para que o sistema recupere minhas informações de voo e eu possa receber recomendações contextualizadas.

#### Critérios de Aceitação

1. WHEN o passageiro envia um código de reserva válido (6 caracteres alfanuméricos), THE API SHALL consultar as tabelas `booking`, `passenger`, `passengerdetails` e `flight` no TiDB e retornar nome do passageiro, número do voo, aeroporto de origem, aeroporto de destino, horário programado de partida e status atual do voo (um dos valores: `Scheduled`, `Delayed`, `Cancelled`, `Landed`).
2. IF o código de reserva não estiver no formato esperado (não alfanumérico ou tamanho diferente de 6), THEN THE API SHALL retornar uma resposta de erro indicando formato inválido, sem acionar consulta ao banco de dados.
3. IF o código de reserva não existir na tabela `booking`, THEN THE API SHALL retornar uma resposta de erro indicando que a reserva não foi encontrada.
4. IF a conexão com o TiDB falhar durante a consulta, THEN THE API SHALL retornar uma resposta de erro indicando indisponibilidade temporária do serviço de dados.
5. WHEN a consulta de reserva for concluída com sucesso, THE API SHALL retornar a resposta em no máximo 3 segundos.

---

### Requisito 2: Configuração e Ingestão de Dados de Serviços do Aeroporto

**User Story:** Como operador do sistema, quero que os serviços do aeroporto sejam armazenados com embeddings vetoriais para que buscas semânticas em linguagem natural possam ser realizadas.

#### Critérios de Aceitação

1. THE Vector_Search SHALL criar a tabela `airport_services` no TiDB com as colunas: `id` (INT PRIMARY KEY AUTO_INCREMENT), `name` (VARCHAR(255)), `category` (VARCHAR(100)), `location` (VARCHAR(255)), `description` (TEXT), `embedding` (VECTOR(1024)).
2. WHEN o script de seed for executado, THE Vector_Search SHALL inserir no mínimo 30 registros sintéticos de serviços do aeroporto cobrindo as categorias: café/alimentação, carregadores elétricos, lounges, farmácia, portões de embarque, banheiros e loja de conveniência, com cada categoria representada por no mínimo 3 registros distintos.
3. WHEN um novo registro de serviço for inserido, THE Vector_Search SHALL gerar o embedding da coluna `description` usando a função `EMBED_TEXT("tidbcloud_free/amazon/titan-embed-text-v2", description)` do TiDB e armazená-lo na coluna `embedding`.
4. IF a tabela `airport_services` já existir ao executar o script de seed, THEN THE Vector_Search SHALL ignorar a criação da tabela e prosseguir sem erro.
5. IF a geração de embedding falhar para um registro durante o script de seed, THEN THE Vector_Search SHALL interromper a execução do seed e exibir uma mensagem de erro indicando o nome do registro que causou a falha, sem realizar inserções parciais na tabela.
6. WHEN o script de seed for concluído com sucesso, THE Vector_Search SHALL exibir uma mensagem de confirmação indicando o número total de registros inseridos.

---

### Requisito 3: Busca Semântica de Serviços por Necessidade do Passageiro

**User Story:** Como passageiro, quero descrever minha necessidade em linguagem natural para que o sistema encontre os serviços do aeroporto mais relevantes para mim.

#### Critérios de Aceitação

1. WHEN o passageiro envia uma descrição de necessidade em linguagem natural com entre 1 e 500 caracteres, THE Vector_Search SHALL gerar o embedding da consulta usando `EMBED_TEXT("tidbcloud_free/amazon/titan-embed-text-v2", :query)` e executar busca por similaridade com `VEC_COSINE_DISTANCE` na tabela `airport_services`.
2. WHEN a busca semântica for executada, THE Vector_Search SHALL retornar os 5 serviços com menor distância de cosseno em relação ao embedding da consulta, incluindo para cada resultado: nome, descrição e distância de cosseno calculada.
3. IF a descrição de necessidade estiver vazia ou exceder 500 caracteres, THEN THE Vector_Search SHALL retornar uma resposta de erro indicando que a entrada é inválida, sem acionar a busca vetorial.
4. IF nenhum serviço for encontrado na tabela `airport_services`, THEN THE Vector_Search SHALL retornar uma lista vazia sem lançar exceção.
5. IF a geração de embedding da consulta ou a execução da busca falhar, THEN THE Vector_Search SHALL retornar uma resposta de erro indicando falha no serviço de busca.
6. WHEN a busca semântica for concluída com sucesso, THE Vector_Search SHALL retornar os resultados em no máximo 2 segundos a partir do recebimento da consulta.
7. THE Vector_Search SHALL aceitar consultas em português (pt-BR) e inglês sem configuração adicional.

---

### Requisito 4: Geração do Plano de Ação via Amazon Bedrock

**User Story:** Como passageiro, quero receber um plano de ação empático e personalizado em português para que eu saiba exatamente o que fazer durante meu atraso ou conexão curta.

#### Critérios de Aceitação

1. WHEN os dados do passageiro e os serviços relevantes forem recuperados, THE Bedrock_Client SHALL invocar o modelo de linguagem configurado com um prompt contendo: nome do passageiro, número do voo, status do voo, tempo estimado de espera e lista dos serviços encontrados.
2. WHEN o Bedrock_Client invocar o modelo, THE Bedrock_Client SHALL formatar o prompt de forma que a resposta gerada seja exclusivamente em português (pt-BR), contenha exatamente 3 passos numerados sequencialmente de 1 a 3, e que cada passo seja uma instrução direta e acionável dirigida ao passageiro em primeira pessoa do plural (ex.: "Dirija-se a...").
3. WHEN o modelo retornar a resposta, THE API SHALL estruturar o plano de ação como um objeto com exatamente 3 campos distintos e individualmente acessíveis, cada um contendo o texto de um passo, preservando a ordem sequencial dos passos gerados.
4. IF a chamada ao Amazon Bedrock exceder 10 segundos sem resposta, THEN THE Bedrock_Client SHALL interromper a chamada e THE API SHALL retornar uma resposta de erro indicando que o tempo limite foi excedido ao gerar recomendações, com código HTTP 504.
5. IF o Amazon Bedrock retornar um erro de serviço, THEN THE Bedrock_Client SHALL realizar no máximo 2 tentativas adicionais com intervalo de 1 segundo entre cada tentativa antes de propagar o erro.
6. IF as tentativas de retry forem esgotadas sem sucesso, THEN THE API SHALL retornar uma resposta de erro indicando falha no serviço de geração de recomendações, com código HTTP 503.
7. IF as credenciais AWS necessárias para autenticação com o Amazon Bedrock não estiverem disponíveis no ambiente de execução, THEN THE Bedrock_Client SHALL falhar na inicialização e THE API SHALL retornar uma resposta de erro indicando indisponibilidade do serviço, com código HTTP 503.

---

### Requisito 5: Interface Web do Passageiro

**User Story:** Como passageiro, quero uma interface simples e guiada para que eu possa consultar o GateMate sem precisar de treinamento ou conta cadastrada.

#### Critérios de Aceitação

1. THE Frontend SHALL exibir um campo de texto para entrada do código de reserva, aceitando entre 1 e 20 caracteres alfanuméricos, e um botão de confirmação como primeiro passo da interação.
2. WHEN o passageiro confirmar o código de reserva com sucesso, THE Frontend SHALL exibir o nome do passageiro, número do voo e status atual antes de solicitar a descrição da necessidade.
3. WHEN os dados do voo forem exibidos, THE Frontend SHALL apresentar um campo de texto no estilo chat para o passageiro descrever sua necessidade em linguagem natural, aceitando entre 1 e 500 caracteres.
4. WHEN o plano de ação for recebido da API, THE Frontend SHALL exibir os passos do plano em lista numerada, apresentando cada passo em sequência distinta com separação visual entre eles.
5. WHILE o Frontend aguarda resposta da API, THE Frontend SHALL exibir um indicador de carregamento visível ao passageiro por no máximo 30 segundos.
6. IF a API retornar um erro, THEN THE Frontend SHALL exibir uma mensagem de erro em português sem expor detalhes técnicos, códigos de status ou informações de sistema ao passageiro.
7. IF o Frontend não receber resposta da API dentro de 30 segundos, THEN THE Frontend SHALL exibir ao passageiro uma mensagem indicando indisponibilidade temporária e orientar nova tentativa.
8. IF o passageiro submeter o campo de código de reserva vazio ou contendo apenas espaços, THEN THE Frontend SHALL exibir uma indicação de campo obrigatório sem acionar chamada à API.
9. THE Frontend SHALL funcionar sem autenticação — o código de reserva é o único identificador necessário.
10. THE Frontend SHALL ser acessível via navegador na porta 3000.

---

### Requisito 6: Configuração da Aplicação e Segurança de Credenciais

**User Story:** Como desenvolvedor, quero que a aplicação seja configurada por variáveis de ambiente para que credenciais nunca sejam expostas no repositório.

#### Critérios de Aceitação

1. WHEN a API for inicializada, THE API SHALL carregar todas as variáveis de ambiente do arquivo `.env` usando `python-dotenv` antes de estabelecer qualquer conexão com serviços externos.
2. WHEN a API for inicializada com sucesso, THE API SHALL estar acessível na porta 8000 com bind em `0.0.0.0`.
3. THE GateMate SHALL incluir um arquivo `.env.example` versionado no repositório com todas as variáveis de ambiente necessárias e sem valores de credenciais reais. As variáveis mínimas são: `TIDB_HOST`, `TIDB_PORT`, `TIDB_USER`, `TIDB_PASSWORD`, `TIDB_DB`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`.
4. THE GateMate SHALL incluir um arquivo `.gitignore` que liste explicitamente `.env` para impedir o versionamento de credenciais.
5. IF o arquivo `.env` não contiver uma ou mais das variáveis de ambiente obrigatórias, ou se seus valores estiverem em branco, THEN THE API SHALL encerrar a inicialização com código de saída não-zero e uma mensagem de erro legível indicando o nome de cada variável ausente ou vazia.
6. IF o arquivo `.env` tiver sido previamente rastreado pelo git, THEN o `.gitignore` SHALL ser verificado antes do commit e THE GateMate SHALL incluir instruções no README para remoção do rastreamento via `git rm --cached .env`.

---

### Requisito 7: Estrutura de Arquivos e Entregáveis do Hackathon

**User Story:** Como avaliador do hackathon, quero que o projeto siga a estrutura de arquivos definida para que a avaliação e execução sejam reproduzíveis.

#### Critérios de Aceitação

1. THE GateMate SHALL conter os arquivos `backend/main.py`, `backend/tidb_vector.py`, `backend/bedrock_client.py`, `backend/db.py`, `frontend/` (diretório React Vite), `SUBMISSION.md`, `.env.example` e `.gitignore` no repositório raiz.
2. THE GateMate SHALL incluir um arquivo `SUBMISSION.md` com no mínimo: (a) descrição do projeto em até 500 palavras, (b) passo a passo de execução local com comandos exatos para backend e frontend, e (c) lista de todas as tecnologias e bibliotecas utilizadas com suas respectivas versões.
3. THE GateMate SHALL incluir um arquivo `.env.example` listando todas as variáveis de ambiente exigidas pela aplicação, sem valores reais de segredos, de modo que um avaliador possa configurar o ambiente copiando o arquivo e preenchendo os valores.
4. WHEN o comando `uvicorn main:app --host 0.0.0.0 --port 8000` for executado no diretório `backend/` com todas as variáveis de ambiente do `.env.example` devidamente preenchidas, THE API SHALL iniciar sem erros e responder com HTTP 200 na rota de health check em até 10 segundos.
5. WHEN o comando `npm run dev` for executado no diretório `frontend/` após `npm install`, THE Frontend SHALL iniciar e ficar acessível na porta 3000 em até 30 segundos, sem erros fatais no console.
