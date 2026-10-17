# CIAO --- Conecta IoT Angola

> Plataforma IoT acessível para estudantes, profissionais e
> organizações, inspirada em plataformas como Blynk. O objetivo é
> facilitar a criação, gestão e monitorização de projetos IoT, com uma
> arquitetura modular e preparada para crescer.

**Estado do projeto:** backend com os módulos principais implementados e
testados (identidade/RBAC, empresas, projetos, dispositivos,
datastreams, histórico de valores e MQTT — ver Prioridades 1-5 na
secção 11). Dashboards/widgets e regras de automação com notificações
internas foram implementados no backend e ligados à tela mobile. Comandos
MQTT para atuadores são publicados por uma fila persistente com tentativas
de repetição; falta integrar e validar o contrato no firmware. O frontend
(`frontend/`, Expo/React Native) já liga
os fluxos principais (login, empresas, projetos, dispositivos,
datastreams, dashboards/widgets e valores/histórico à API real.
As notificações são internas à aplicação; envio push/e-mail ainda não
está implementado — ver secção 7.

------------------------------------------------------------------------

## Índice

-   [1. Visão geral](#1-visão-geral)
-   [2. Tecnologias](#2-tecnologias)
-   [3. Arquitetura funcional](#3-arquitetura-funcional)
-   [4. Estrutura do backend](#4-estrutura-do-backend)
-   [5. Funcionalidades implementadas](#5-funcionalidades-implementadas)
-   [6. Modelo de dados](#6-modelo-de-dados)
-   [7. API atual](#7-api-atual)
-   [8. Ambiente de desenvolvimento](#8-ambiente-de-desenvolvimento)
-   [9. Migrações da base de dados](#9-migrações-da-base-de-dados)
-   [10. Testes realizados](#10-testes-realizados)
-   [11. Trabalho pendente](#11-trabalho-pendente)
-   [12. Próximas etapas recomendadas](#12-próximas-etapas-recomendadas)
-   [13. Segurança e observações
    técnicas](#13-segurança-e-observações-técnicas)
-   [14. Estado atual resumido](#14-estado-atual-resumido)

------------------------------------------------------------------------

## 1. Visão geral

**CIAO** significa **Conecta IoT Angola**. É uma plataforma para
conectar dispositivos IoT, organizar os dispositivos por projetos e
empresas e, futuramente, recolher dados através de MQTT, armazená-los e
apresentá-los em dashboards.

### Objetivos

-   Tornar a criação e gestão de projetos IoT mais acessível.
-   Organizar utilizadores, empresas, projetos e dispositivos.
-   Permitir que um dispositivo tenha vários canais de dados
    (*Datastreams*).
-   Preparar a integração com MQTT e sistemas de visualização.
-   Manter uma arquitetura modular, com separação entre API, serviços,
    repositórios e modelos.

## 2. Tecnologias

Tecnologias identificadas no backend atual:

-   **Python**
-   **FastAPI** --- API HTTP e documentação OpenAPI/Swagger.
-   **SQLAlchemy assíncrono** --- ORM e acesso à base de dados.
-   **PostgreSQL** --- base de dados relacional.
-   **Alembic** --- migrações do esquema da base de dados.
-   **Pydantic** --- validação e serialização dos dados.
-   **uv** --- gestão do ambiente Python e execução de comandos.
-   **Uvicorn** --- servidor ASGI.

Frontend (`frontend/`):

-   **Expo SDK 57 / React Native 0.86 / Expo Router** --- app móvel nativa
    (não é o React web originalmente previsto; a app foi convertida a
    partir de um protótipo web anterior — ver `frontend/README.md`).
-   **@tanstack/react-query** --- camada de fetching/mutations contra a
    API real.
-   **expo-secure-store** --- persistência de tokens JWT e do URL do
    backend configurado.
-   Cliente HTTP próprio (`frontend/src/api/client.ts`), sem gerador de
    tipos a partir do OpenAPI — tipos escritos à mão, espelhando os
    schemas Pydantic do backend.

Tecnologias previstas ou cuja integração completa ainda precisa de ser
confirmada:

-   **Redis** --- configurado em `.env`, mas ainda sem nenhum uso real no
    código (nem cache, nem filas, nem rate limiting).
-   **Auth0** --- foi considerado no plano de autenticação; o backend usa
    hoje autenticação própria via JWT (`OAuth2PasswordRequestForm` +
    tokens de acesso/refresh), não Auth0.

## 3. Arquitetura funcional

A hierarquia principal definida é:

``` text
Utilizador
   │
   ├── pertence/tem acesso a uma Empresa (Company)
   │                         │
   │                         └── Projeto (Project)
   │                                  │
   │                                  └── Dispositivo (Device)
   │                                           │
   │                                           └── Datastream
   │                                                  │
   │                                                  └── Histórico de valores
   │
   └── Role e permissões (RBAC)
```

Fluxo IoT previsto:

``` text
ESP32 / outro dispositivo
        │
        ▼
   Broker MQTT
        │
        ▼
   Serviço MQTT do CIAO
        │
        ▼
 Identificação do Device e Datastream
        │
        ▼
 Armazenamento de valores
        │
        ▼
 Dashboards, widgets, alertas e automações
```

**Nota:** a parte de receção MQTT, armazenamento de histórico e
visualização é uma direção arquitetural planeada, não uma funcionalidade
que esteja confirmada como concluída.

## 4. Estrutura do backend

A estrutura inclui módulos separados por domínio. A estrutura exata pode
variar conforme os últimos ficheiros locais:

``` text
backend/
├── alembic/
│   └── versions/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   ├── common/
│   ├── core/
│   ├── db/
│   │   ├── base.py
│   │   ├── models.py
│   │   ├── session.py
│   │   └── seeds/
│   ├── modules/
│   │   ├── auth/
│   │   ├── identity/
│   │   ├── users/
│   │   ├── companies/
│   │   ├── projects/
│   │   ├── devices/
│   │   ├── datastreams/
│   │   ├── mqtt/
│   │   ├── dashboards/
│   │   ├── widgets/
│   │   ├── automation/
│   │   └── notifications/
│   ├── scripts/
│   └── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```

Cada módulo de domínio pode separar as responsabilidades em:

-   `model.py` --- modelo SQLAlchemy.
-   `schema.py` --- schemas Pydantic para entrada/saída.
-   `repository.py` --- consultas e persistência.
-   `service.py` --- regras de negócio.
-   `api.py` --- endpoints FastAPI.
-   `__init__.py` --- inicialização do pacote.

Nem todos os módulos listados estão concluídos; alguns aparecem na
estrutura do projeto, mas ainda precisam de implementação ou validação.

## 5. Funcionalidades implementadas

### 5.1 Identidade e autenticação

Implementado no módulo `identity`:

-   Utilizador e credenciais.
-   Login com `OAuth2PasswordRequestForm`.
-   Autenticação via token, usada nos endpoints protegidos.
-   Endpoint para obter o utilizador autenticado (`/me`).
-   Relação entre utilizador e role.
-   Modelo de refresh token.
-   Dependência `get_current_user`.
-   Dependência `require_permission(permission_name)` para verificação
    de permissões.

**A confirmar antes de produção:** rotação/revogação de refresh tokens,
expiração, recuperação de palavra-passe, verificação de e-mail,
limitação de tentativas e política completa de sessões.

### 5.2 RBAC --- funções e permissões

Roles presentes no ambiente de desenvolvimento:

-   `admin`
-   `user`
-   `student`
-   `teacher`

Permissões já usadas ou previstas no seed:

-   `users:create`, `users:read`, `users:update`, `users:delete`
-   `projects:create`, `projects:read`, `projects:update`,
    `projects:delete`
-   `devices:create`, `devices:read`, `devices:update`, `devices:delete`
-   `companies:read`, `companies:create`, `companies:update`,
    `companies:delete`, `companies:manage_members`

A matriz efetiva de permissões depende do estado atual da base de dados
e do ficheiro de seed. Algumas permissões e atribuições foram ajustadas
manualmente durante os testes.

**Gap real encontrado e corrigido:** a role `user` (atribuída por
omissão no registo — a usada pela app móvel) não tinha
`companies:create` nem `projects:read`/`projects:create`. Um utilizador
recém-registado conseguia autenticar-se mas nunca conseguia criar a sua
própria empresa nem projeto — ficava bloqueado logo no onboarding.
Corrigido em `app/modules/identity/seed.py`. **Importante:** `seed_rbac`
é aditivo (nunca remove permissões existentes), por isso numa base de
dados já semeada antes desta correção é preciso chamar outra vez
`POST /api/v1/identity/seed-rbac` (sem autenticação, pensado para
bootstrap) para as roles existentes passarem a ter as permissões novas
— editar só o `seed.py` não as aplica retroativamente.

**Pendente:** consolidar todas as roles e permissões no seed
idempotente, garantir que uma instalação nova recebe o mesmo conjunto de
permissões e aplicar de forma consistente `require_permission` nos
endpoints.

### 5.3 Empresas --- `companies`

Modelo de empresa com:

-   `name`
-   `slug` único
-   `description`
-   `owner_id`
-   relação com membros

Modelo de membro (`CompanyMember`) com:

-   `company_id`
-   `user_id`
-   `role`
-   restrição única para impedir o mesmo utilizador de ser adicionado
    duas vezes à mesma empresa.

Operações implementadas e testadas:

-   Criar/listar empresas, conforme os endpoints existentes.
-   Consultar membros.
-   Adicionar membro.
-   Atualizar o papel do membro.
-   Remover membro.
-   Impedir a alteração ou remoção do proprietário através das operações
    de membros.
-   Validar que um utilizador sem acesso à empresa não consegue aceder
    aos seus dados.

Papéis de membro usados nos testes incluem `developer` e `technician`. A
autorização detalhada por papel de membro ainda deve ser formalizada.

### 5.4 Projetos --- `projects`

Um projeto pertence a uma empresa e tem um proprietário.

Campos principais:

-   `id`
-   `name`
-   `description`
-   `owner_id`
-   `company_id`
-   campos herdados da entidade base, como timestamps e eliminação
    lógica, conforme o `BaseEntity`.

Operações implementadas e testadas:

-   Criar projeto.
-   Listar projetos acessíveis ao utilizador.
-   Consultar projeto.
-   Atualizar projeto.
-   Eliminar projeto.
-   Verificar acesso com base no utilizador e na associação à empresa.

Foi criado um projeto de teste chamado `Esp32-quarto`. O ID
anteriormente registado nas notas era
`c921e2f5-7a55-4608-8224-61e5657bc395`. A empresa de teste `tech angola`
tinha o ID `6171883c-8bcc-4b6c-9f1d-0a82f4ec4337`. Estes IDs são
referências do ambiente de desenvolvimento e podem já não corresponder
ao estado atual da base de dados.

### 5.5 Dispositivos --- `devices`

Cada dispositivo pertence a um projeto.

Campos principais:

-   `project_id`
-   `uuid` --- identificador externo do dispositivo
-   `serial`
-   `token`
-   `mqtt_username`
-   `mqtt_password`
-   `name`
-   `model`
-   `firmware_version`
-   `status`
-   `last_seen`
-   `is_active`
-   campos de auditoria/entidade base

O token é gerado com `secrets.token_urlsafe(32)`. O schema normal de
resposta não expõe `token` nem `mqtt_password`.

Endpoints implementados:

-   Criar dispositivo para um projeto.
-   Listar dispositivos de um projeto.
-   Consultar dispositivo por ID.
-   Atualizar dispositivo.
-   Eliminar dispositivo.

Testes realizados:

-   CRUD principal passou.
-   Persistência após requisições foi corrigida através de
    commit/rollback na dependência de sessão.
-   Teste de isolamento: utilizador sem acesso ao projeto não deve
    conseguir consultar o dispositivo.

**Pendente:** definir a política de autorização para alterações e
eliminações; atualmente o serviço de Device verifica acesso ao projeto,
mas não aplica necessariamente uma regra de proprietário ou papel
específico para mutações. Rever também o ciclo de vida seguro das
credenciais do dispositivo.

### 5.6 Datastreams --- `datastreams`

Um Datastream representa um canal de dados de um dispositivo, por
exemplo:

-   `temperature` --- temperatura, `float`, `°C`
-   `humidity` --- humidade, `float`, `%`
-   `pump` --- estado de uma bomba

Campos implementados:

-   `device_id`
-   `name`
-   `key`
-   `data_type`
-   `unit`
-   `min_value`
-   `max_value`
-   `is_active`
-   campos de auditoria/entidade base

Código criado:

-   `model.py`
-   `schema.py`
-   `repository.py`
-   `service.py`
-   `api.py`

Regras no serviço:

-   Validar acesso ao dispositivo através de `DeviceService`.
-   Rejeitar chaves duplicadas no mesmo dispositivo com `409 Conflict`
    ao nível da aplicação.
-   Validar que `min_value` não é maior que `max_value`.
-   Permitir listar, consultar, atualizar e eliminar Datastreams.

Migration aplicada:

-   Revision: `ea839d03eea6`
-   Revisão anterior: `f4ca78204707`
-   Tabela `datastreams` criada com sucesso.
-   O problema recorrente de autogenerate relacionado com
    `projects.owner_id` foi removido manualmente da migration para não
    alterar uma FK alheia ao trabalho.

O router foi registado em `app/main.py` com o prefixo
`/api/v1/datastreams`.

**Estado dos testes:** o import da classe `DatastreamService` e o import
da aplicação `app.main` foram confirmados. A compilação passou. Ainda
falta completar o CRUD funcional via Swagger, porque o ID do Device de
teste precisa de ser recuperado da base de dados.

**Melhoria de integridade recomendada:** criar uma constraint única
composta por `(device_id, key)`. A verificação atual no serviço,
isoladamente, pode permitir duplicados em pedidos concorrentes.

## 6. Modelo de dados

Relações principais:

``` text
users ──< company_members >── companies
  │                            │
  │                            └──< projects
  │                                    │
  └── roles / permissions              └──< devices
                                               │
                                               └──< datastreams
```

Tabelas que foram confirmadas nas migrations ou no desenvolvimento:

-   `users`
-   `roles`
-   `permissions`
-   `role_permissions`
-   `refresh_tokens`
-   `companies`
-   `company_members`
-   `projects`
-   `devices`
-   `datastreams`
-   `datastream_values`
-   `dashboards`
-   `widgets`

A lista deve ser comparada com as migrations e a base de dados atual
antes de se considerar um inventário definitivo.

## 7. API atual

O prefixo principal da API é `/api/v1`.

### Identidade

O router está registado sob:

``` text
/api/v1/identity
```

Endpoints conhecidos no desenvolvimento incluem login, consulta do
utilizador autenticado (`/me`) e seed RBAC. Consultar `/docs` para os
caminhos e métodos exatos da versão local.

### Empresas

``` text
/api/v1/companies
```

O módulo inclui operações de empresas e gestão de membros. Consultar
Swagger para a lista exata de endpoints.

### Projetos

``` text
/api/v1/projects
```

CRUD de projetos com verificação de acesso.

### Dispositivos

``` text
POST   /api/v1/devices/projects/{project_id}
GET    /api/v1/devices/projects/{project_id}
GET    /api/v1/devices/{device_id}
PATCH  /api/v1/devices/{device_id}
DELETE /api/v1/devices/{device_id}
```

### Datastreams

``` text
POST   /api/v1/datastreams/devices/{device_id}
GET    /api/v1/datastreams/devices/{device_id}
GET    /api/v1/datastreams/{datastream_id}
PATCH  /api/v1/datastreams/{datastream_id}
DELETE /api/v1/datastreams/{datastream_id}
```

### Dashboards e widgets

``` text
POST   /api/v1/dashboards
GET    /api/v1/dashboards/projects/{project_id}
GET    /api/v1/dashboards/{dashboard_id}
PATCH  /api/v1/dashboards/{dashboard_id}
DELETE /api/v1/dashboards/{dashboard_id}
POST   /api/v1/dashboards/{dashboard_id}/widgets
GET    /api/v1/dashboards/{dashboard_id}/widgets
PATCH  /api/v1/dashboards/widgets/{widget_id}
DELETE /api/v1/dashboards/widgets/{widget_id}
```

Os dashboards guardam nome, descrição e layout JSON por projeto. Cada
widget guarda tipo, configuração, posição e referência a um Datastream
do mesmo projeto. A API verifica acesso ao projeto; apenas o proprietário
do projeto pode criar, alterar ou eliminar dashboards e widgets. A tela
mobile lista/cria dashboards, associa widgets de valor, gráfico e
controlo e consulta valores atuais/histórico pelos endpoints existentes.

### Automações e notificações

``` text
POST   /api/v1/automations
GET    /api/v1/automations/projects/{project_id}
PATCH  /api/v1/automations/{rule_id}
DELETE /api/v1/automations/{rule_id}
GET    /api/v1/notifications
PATCH  /api/v1/notifications/{notification_id}
POST   /api/v1/notifications/read-all
```

As regras suportam condições numéricas (`<`, `>` ou `=`) e criam uma
notificação interna quando um valor recebido satisfaz a condição. Há um
intervalo configurável entre notificações repetidas. A criação de regras
é restrita ao proprietário do projeto. A ação pode também controlar um
Datastream booleano do mesmo projeto. O backend grava o comando numa fila
transacional e publica com QoS 1 em
`ciao/devices/{device_uuid}/commands/{key}`, com payload
`{"command_id":"…","value":true,"created_at":"…"}` e repetição em
caso de falha. O firmware deve subscrever esse tópico e tratar
`command_id` de forma idempotente. Envio push/e-mail ainda não está
implementado.

A documentação interativa deve estar disponível em:

``` text
http://127.0.0.1:8000/docs
```

A lista acima documenta os caminhos definidos durante o desenvolvimento;
a aplicação local e o OpenAPI são a referência final para confirmar o
estado atual.

### CORS

Middleware adicionado em `app/main.py` (`CORSMiddleware`, `allow_origins=["*"]`,
sem credentials) para o frontend Expo conseguir chamar a API a partir de
origens variáveis em dev (web local, túneis, IP de rede do telemóvel).
**É uma configuração de desenvolvimento, não de produção** — antes de
produção, restringir `allow_origins` ao(s) domínio(s) reais do
frontend.

## 8. Ambiente de desenvolvimento

O ambiente registado é Windows, com o projeto localizado em:

``` text
C:\Users\Sejogal\Documents\Projetos\Blynk AO\backend
```

O projeto utiliza `uv`. Os comandos abaixo devem ser executados na pasta
`backend`.

### Instalar/sincronizar dependências

``` powershell
uv sync
```

Se o projeto ainda não tiver o ambiente sincronizado, este comando
instala as dependências declaradas no `pyproject.toml`/`uv.lock`.

### Configuração de ambiente

Existe um ficheiro `.env` no ambiente de desenvolvimento. **Não
publiques o conteúdo do `.env` nem credenciais reais.**

Confirma no código de configuração quais são as variáveis obrigatórias,
sobretudo:

-   URL/host da base de dados PostgreSQL.
-   Nome da base de dados.
-   Utilizador e palavra-passe da base de dados.
-   Chave secreta e configuração de tokens.
-   Redis e MQTT, quando ativados.

A configuração deve ser coerente com o PostgreSQL local. Durante o
desenvolvimento foram encontrados defaults que apontavam para o host
Docker `postgres`, enquanto o `.env` indicava `localhost`; verifica a
precedência de configuração antes de executar migrations.

### Executar migrations

``` powershell
uv run alembic current
uv run alembic upgrade head
```

### Verificar sintaxe Python

``` powershell
uv run python -m compileall app
```

Este comando verifica a compilação dos ficheiros, mas **não garante que
todos os imports funcionem em runtime**.

### Verificar imports e aplicação

``` powershell
uv run python -c "from app.main import app; print('CIAO OK')"
```

### Iniciar servidor

``` powershell
uv run uvicorn app.main:app --reload
```

Depois abre:

``` text
http://127.0.0.1:8000/docs
```

## 9. Migrações da base de dados

Migrações relevantes no estado registado:

  Revisão          Descrição
  ---------------- -------------------------------------
  `8d2ffbf01604`   Adição de `company_id` aos projetos
  `f4ca78204707`   Criação da tabela `devices`
  `ea839d03eea6`   Criação da tabela `datastreams`
  `71ab22e046a1`   Criação de dashboards e widgets
  `9d31c640a72b`   Criação de regras de automação e notificações
  `5b8cf21ad804`   Fila de comandos MQTT para atuadores
  `b2ac33f081e2`   Constraints para status de device e tipo de datastream
  `c1d8e7a4f602`   Tokens de recuperacao de password de uso unico

O estado confirmado mais recente foi:

``` text
Migrations `b2ac33f081e2` e `c1d8e7a4f602` aplicadas na base local.
O seed RBAC tambem foi executado para adicionar as permissoes de datastream.
```

### Cuidado com autogenerate

O Alembic detetou repetidamente uma diferença na FK `projects.owner_id`:
a definição do modelo e a FK existente na base de dados não coincidem
quanto ao comportamento `ON DELETE` (`RESTRICT` no modelo descrito,
`CASCADE` observado na base de dados).

Ao gerar novas migrations:

1.  Rever sempre o ficheiro gerado.
2.  Não aplicar alterações a `projects.owner_id` se a tarefa não as
    exigir.
3.  Remover do `upgrade()` e `downgrade()` as operações não relacionadas
    apenas depois de confirmar o conteúdo.
4.  Não apagar nem reescrever migrations já aplicadas sem um plano de
    migração explícito.

## 10. Testes realizados

### Confirmados como aprovados durante o desenvolvimento

-   Login e autenticação via Swagger.
-   Consulta do utilizador autenticado e respetivo role/permissões.
-   Seed RBAC inicial.
-   Verificação de permissões com `require_permission`.
-   Gestão de membros da empresa: adicionar, listar, alterar papel e
    remover.
-   Bloqueio de operações de alteração/remoção do proprietário como
    membro.
-   Isolamento de empresa para utilizador sem associação.
-   CRUD de projetos, incluindo PATCH e DELETE.
-   CRUD de dispositivos, incluindo PATCH e DELETE.
-   Persistência corrigida na dependência `get_db()` com commit e
    rollback.
-   Migration de `devices`.
-   Migration de `datastreams`.
-   Compilação Python após o código de Datastreams.
-   Import de `DatastreamService`.
-   Import de `app.main`.
-   CRUD funcional completo de Datastreams via HTTP (create, list, get,
    patch, delete), verificado manualmente e com pytest.
-   Duplicação de `key` no mesmo Device → `409`, incluindo o caso de
    corrida real (constraint única `uq_datastreams_device_id_key` na
    base de dados + `IntegrityError` tratado no service, não só a
    verificação prévia a nível de aplicação).
-   `min_value > max_value` no create e no update → `400`.
-   Isolamento de Datastream para utilizador sem acesso ao Device/
    projeto → `404`.
-   Testes automatizados com pytest (ver `backend/tests/`): Datastreams,
    identidade/registo, RBAC e histórico de valores.
-   Cobertura das regras RBAC: role por omissão no registo, promoção de
    role por admin, bloqueio de utilizador sem role.
-   Modelo de histórico de valores (`datastream_values`), validação de
    tipo contra `data_type`, API de valor atual e histórico com
    filtros de tempo e paginação.
-   Dashboards/widgets: testes de CRUD básico e rejeição de associação
    a Datastream de outro projeto (`tests/test_dashboards.py`).
-   Automações/notificações: testes de criação de regra, geração de
    notificação, cooldown, marcação de leitura, tipo numérico e acesso
    ao projeto (`tests/test_automations.py`).
-   Comandos MQTT: teste de criação na fila e publicação QoS 1 no tópico
    do dispositivo com o worker (`tests/test_automations.py`).
-   Heartbeat: teste de transição para offline após timeout e manutenção
    do estado online para dispositivos com heartbeat recente
    (`tests/test_mqtt_heartbeat.py`).
-   Bug real corrigido: `devices/api.py` e `datastreams/api.py`
    importavam `get_db` de `app.db.session`, enquanto os restantes
    módulos (e `get_current_user`) importavam de `app.db.dependencies`
    — duas sessões/ligações diferentes dentro do mesmo pedido. Unificado
    em `app.db.session.get_db` (a variante com commit automático, a
    única segura para os módulos que já dependiam dela); `app/db/
    dependencies.py` foi removido.
-   Bug real corrigido: `seed_rbac()` em `app/modules/identity/seed.py`
    nunca tinha funcionado (`KeyError` ao tratar o dict de cada role
    como se já fosse a lista de permissões).
-   Gap real resolvido: utilizadores novos ficavam sempre com
    `role_id = NULL` (sem endpoint para lhes atribuir uma role). Agora o
    registo atribui a role `user` por omissão (quando o RBAC já foi
    semeado) e existe `PATCH /api/v1/identity/users/{user_id}/role`
    (requer `users:update`) para um admin promover outro utilizador. Um
    script `app/scripts/promote_admin.py <email>` permite promover o
    primeiro admin manualmente.

### Integração frontend ↔ backend --- bugs reais encontrados e corrigidos

-   **CORS inexistente**: não havia `CORSMiddleware` nenhum em
    `app/main.py`. Testar a partir do browser (Expo web) falhava
    silenciosamente (erro de CORS no fetch, sem detalhe visível na UI) —
    parecia "não há ligação ao servidor". Corrigido (ver secção 7).
-   **Porta por omissão errada no frontend**: `frontend/src/api/client.ts`
    tinha `DEFAULT_API_URL` a apontar para a porta `8010`; o `.env` do
    backend define `PORT=8000`. Corrigido para `8000`.
-   **Dois servidores a disputar a mesma porta**: durante os testes desta
    sessão chegaram a correr ao mesmo tempo um `run_dev.py` em
    background e um `uvicorn --reload` manual, ambos a tentar a porta
    `8000` — comportamento imprevisível de qual respondia a cada pedido.
    Confirmar sempre com `Get-NetTCPConnection -LocalPort 8000` (Windows)
    antes de assumir que só há um processo a servir a API.
-   **`fetch` do React Native não define `Content-Type` sozinho para
    body `URLSearchParams`**: ao contrário do browser, que o faz
    automaticamente. O login (`OAuth2PasswordRequestForm`, espera
    `application/x-www-form-urlencoded`) funcionava em Expo web mas
    devolvia `422 Unprocessable Content` num telemóvel real. Corrigido
    em `client.ts` definindo o header explicitamente.
-   **Sem forma de configurar o URL da API antes de autenticar**: o ecrã
    Definições só era alcançável a partir de Perfil, que exige sessão —
    um utilizador num telemóvel novo não conseguia sequer chegar a
    mudar o URL do `localhost` por omissão para o IP da rede local.
    Corrigido com um atalho (ícone de engrenagem) no ecrã de boas-vindas
    (`app/index.tsx`), acessível sem sessão.
-   **Backend tem de escutar em `0.0.0.0`, não só `127.0.0.1`**, para ser
    alcançável por um telemóvel físico na mesma rede Wi-Fi — `uvicorn
    app.main:app --reload` sem `--host` só aceita o próprio PC. Usar
    `run_dev.py`, que já define isto.
-   **Dependência `expo-linking` ausente** do `package.json`, apesar de
    ser exigida pelo `expo-router` em runtime — o bundling falhava com
    `Unable to resolve "expo-linking"`. Corrigido com
    `npx expo install expo-linking`.

### Ainda por confirmar

-   Integração ponta a ponta MQTT → Datastream → armazenamento.
-   [x] Matriz de acesso definida: permissao global habilita a operacao;
    membro da empresa tem leitura; proprietario do projeto pode escrever.
    CompanyMember.role nao eleva acesso de projeto; owner/admin podem gerir
    membros da empresa quando tambem passam pelo RBAC global.
-   Política de retenção de `datastream_values` (hoje não há purga/
    agregação; cresce indefinidamente).
-   [x] Enums/validacao de `Datastream.data_type` e `Device.status` aplicadas em schema e base de dados.

## 11. Trabalho pendente

### Prioridade 1 --- concluir o módulo Datastreams (✅ concluído)

-   [x] Recuperar o ID atual do Device de teste através de
    `GET /api/v1/devices/projects/{project_id}` ou consulta à base de
    dados.
-   [x] Criar o Datastream `temperature`.
-   [x] Listar Datastreams do Device.
-   [x] Consultar Datastream por ID.
-   [x] Atualizar com PATCH.
-   [x] Eliminar com DELETE.
-   [x] Confirmar duplicação de `key` (esperado `409`).
-   [x] Testar `min_value > max_value` (esperado erro de validação da
    regra de negócio).
-   [x] Testar acesso a partir de utilizador sem acesso ao projeto.
-   [x] Adicionar constraint única `(device_id, key)` e gerar/rever
    migration.

### Prioridade 2 --- robustez de identidade e permissões (parcial)

-   [x] Consolidar roles/permissões no seed idempotente (corrigido bug
    real no `seed_rbac`; já era idempotente de resto).
-   [x] Aplicar `require_permission` aos endpoints de devices e
    datastreams, por operacao (read/create/update/delete), mantendo
    tambem a verificacao de acesso ao projeto/dispositivo no servico.
    O seed idempotente agora inclui permissoes de datastream e as
    associacoes correspondentes para as roles existentes.
-   [x] Definir matriz: a role global precisa da permissao da operacao;
    membros da empresa podem ler projetos; apenas o proprietario do projeto
    pode alterar recursos. `CompanyMember.role` nao eleva estas permissoes;
    owner/admin da empresa podem gerir membros, sempre com RBAC global.
-   [x] Definir autorização para criar/alterar/eliminar projetos e
    dispositivos (via `require_permission` + posse de projeto).
-   [x] Rever o acesso: membros da empresa consultam recursos do projeto; apenas o proprietario do projeto pode alterar projeto,
    dispositivos, datastreams, dashboards, widgets e regras. As permissoes globais continuam a limitar cada operacao.
-   [x] Adicionar testes automatizados de autorização (`tests/test_rbac.py`,
    `tests/test_identity_and_access.py`).
-   [x] (Novo, não listado antes) Resolver o gap de utilizadores novos
    sem forma de obter uma role: registo atribui `user` por omissão;
    `PATCH /api/v1/identity/users/{user_id}/role` permite promoção por
    um admin; `app/scripts/promote_admin.py` faz o bootstrap do
    primeiro admin.

### Prioridade 3 --- segurança de dispositivos (parcial)

-   [x] Mostrar o token de dispositivo apenas uma vez na resposta de
    criação e disponibilizar o fluxo de provisionamento na app.
-   [x] Não devolver segredos em respostas normais (confirmado por
    teste: `DeviceResponse` não expõe `token`/`mqtt_password`).
-   [x] Armazenar a password MQTT em hash e não a devolver após a criação.
-   [x] Rotacao de credenciais MQTT via `POST /api/v1/devices/{id}/credentials/rotate`; as antigas deixam de autenticar novas ligacoes e as novas sao exibidas uma vez. Reprovisione o dispositivo.
    A integracao nao termina sessoes MQTT existentes; desligue o client antigo no EMQX durante a rotacao.
-   [x] Implementar autenticação/autorização dispositivo-broker via HTTP
    authenticator e ACL por dispositivo no EMQX.
-   [x] Atualizar `online`/`last_seen` ao receber telemetria e marcar o dispositivo `offline` após timeout sem heartbeat.
-   [x] Configurar timeout/frequência com `MQTT_DEVICE_OFFLINE_AFTER_SECONDS` (120s) e `MQTT_HEARTBEAT_CHECK_INTERVAL_SECONDS` (30s).
-   [x] Restringir `Device.status` (online/offline) e `Datastream.data_type` (boolean/integer/float/string/json) em schemas e migration `b2ac33f081e2`.

### Prioridade 4 --- valores e histórico dos Datastreams (✅ concluído)

-   [x] Criar modelo/tabela para valores históricos dos Datastreams
    (`datastream_values`, migration `403c3c3a4eed`).
-   [x] Definir tipos de valor suportados: boolean, integer, float,
    string ou JSON — coluna `value` em JSONB, validada no service
    contra `Datastream.data_type`.
-   [x] Definir timestamps, índices para consultas temporais
    (`ix_datastream_values_datastream_id_recorded_at`). Retenção
    **ainda não definida** — ver "Ainda por confirmar".
-   [x] Definir API de leitura do valor atual
    (`GET /{datastream_id}/values/latest`) e do histórico
    (`GET /{datastream_id}/values`, com `since`/`until`/`limit`/
    `offset`).

### Prioridade 5 --- MQTT (implementado; falta validar o EMQX local)

-   [x] Implementar conexão com broker MQTT/EMQX — cliente `aiomqtt`,
    gerido pelo `lifespan` de `app/main.py` (tarefa em background,
    reconecta sozinho se o broker cair ou não existir ainda; nunca
    impede o arranque da API). Ver `app/modules/mqtt/client.py`.
-   [x] Definir convenção de tópicos —
    `ciao/devices/{device_uuid}/datastreams/{key}`
    (`app/modules/mqtt/topics.py`; `device_uuid` é `Device.uuid`, nunca
    o `id` interno).
-   [x] Autenticar dispositivos — **ao nível da aplicação**: o payload
    inclui `{"token": "<device.token>", "value": ...}` e
    `app/modules/mqtt/ingest.py` verifica o token (comparação em tempo
    constante) contra o dispositivo indicado no tópico antes de aceitar
    qualquer valor.
-   [x] Autenticar e autorizar no broker EMQX: `app/modules/mqtt/auth.py`
    valida credenciais MQTT individuais e devolve ACL para publicar apenas
    nos datastreams ativos do dispositivo e subscrever os respetivos
    comandos. O utilizador de serviço da API fica limitado a
    `ciao/devices/#`. Configuração em `backend/emqx/base.hocon`.
-   [x] Gerar e guardar `EMQX_AUTH_SECRET` localmente em `backend/.env`, sem o adicionar ao repositorio.
-   [ ] Reiniciar o Compose e validar autenticacao, publicacao e subscricao com EMQX em execucao.
-   [x] Validar mensagens recebidas e associá-las ao Device/Datastream —
    tipo do valor validado contra `Datastream.data_type`; `Device`
    passa a `status="online"` e `last_seen` é atualizado a cada
    mensagem aceite.
-   [x] Tratar mensagens inválidas, reconexões e falhas — `ingest_message`
    nunca propaga exceção (tópico desconhecido, JSON inválido, device/
    datastream inexistente, tipo errado ou token errado só geram um
    `IngestResult(ok=False, reason=...)` e um log, nunca derrubam o
    subscriber); `run_mqtt_ingest_loop` reconecta em qualquer
    `MqttError`.
-   [x] Criar testes com um cliente MQTT de simulação — `amqtt` (broker
    Python puro, só em dev/teste — ver `pyproject.toml`) +
    `tests/test_mqtt_ingest.py` (lógica de ingestão isolada, 10 casos) +
    `tests/test_mqtt_broker_e2e.py` (broker real + publish real +
    subscriber real, prova a ligação ponta a ponta).

**Gap real encontrado e corrigido pelo caminho**: `Device.last_seen`
estava declarado sem timezone na base de dados (`TIMESTAMP` em vez de
`TIMESTAMP WITH TIME ZONE`) — nunca tinha sido escrito por código
nenhum até este módulo, por isso o bug ficou invisível até agora.
Corrigido no modelo + migration `203bf690c532`.

### Prioridade 6 --- Dashboards, widgets e automações

-   [x] Definir modelos persistidos e CRUD de dashboards por projeto.
-   [x] Definir widgets persistidos, associados a Datastreams do mesmo projeto.
-   [x] Aplicar a migration e validar endpoints de dashboards/widgets em ambiente de desenvolvimento.
-   [x] Ligar o ecrã mobile à listagem/criação de dashboards e widgets persistidos.
-   [x] Apresentar valores atuais e histórico nos widgets de valor/gráfico; controlar Datastreams booleanos.
-   [x] Criar/consultar/alterar/eliminar regras numéricas de automação com intervalo de repetição.
-   [x] Gerar notificações internas quando uma regra é satisfeita e permitir marcá-las como lidas.
-   [x] Implementar e testar em `ciao_test` a fila e publicação MQTT QoS 1 para Datastreams booleanos, com repetição em caso de falha.
-   [x] Ligar as telas mobile de automações e notificações à API.
-   [x] Aplicar as migrations e validar os fluxos backend de automação/notificação na base de testes.
-   [ ] Confirmar o worker de comandos com o broker EMQX configurado.
-   [ ] Implementar suporte no firmware para subscrever e executar comandos MQTT.
-   [ ] Implementar envio push/e-mail.
-   [x] Definir partilha: sem convites externos; membros da empresa leem os recursos dos projetos e apenas o proprietario os altera.

### Prioridade 7 --- frontend e operação (parcial)

-   [x] Frontend implementado como app Expo/React Native (`frontend/`),
    não o React web originalmente previsto — ver `frontend/README.md`.
-   [x] Integrar login, registo, empresas, projetos, dispositivos e
    Datastreams à API real (`frontend/src/api/`, com
    `@tanstack/react-query` + `expo-secure-store`).
-   [x] Página de dashboard (`app/dashboards.tsx`) ligada a dados reais
    de datastreams/valores.
-   [x] Ligar as telas de automações e notificações à API backend.
-   [ ] Implementar notificações push/e-mail; atualmente são visíveis na app.
-   [x] Editar perfil pelo `PATCH /api/v1/identity/me`: nome, avatar,
    idioma e fuso horário; email permanece somente leitura.
-   [x] Recuperacao de password implementada com token de uso unico, validade de 30 minutos, hash no banco e revogacao de refresh tokens.
    A entrega do link depende da configuracao SMTP no `backend/.env`.
-   [x] Configurar logs estruturados do backend: saída JSON fora de DEBUG,
    log por pedido HTTP com duração/status e `X-Request-ID` para correlação.
-   [x] Uniformizar erros HTTP, validação e falhas de rede no cliente API;
    falhas de consultas aparecem no toast global e erros de formulários
    continuam junto ao respetivo formulário.
-   [x] Configurar CI no GitHub Actions: suíte pytest com PostgreSQL e
    typecheck TypeScript do frontend em push e pull request.
-   [ ] Provisionar e operar o ambiente de producao (host, TLS, secrets, backups e monitorizacao).
-   [x] Documentar preparacao, atualizacao, rollback e operacoes em `backend/DEPLOYMENT.md`.

## 12. Proximas etapas recomendadas

1. Aplicar a primeira execucao CI no GitHub apos push/PR.
2. Reiniciar Compose quando Docker estiver ativo e validar EMQX auth,
   ingestao MQTT e entrega do worker de comandos.
3. Configurar SMTP para ativar recuperacao de password.
4. Implementar push/e-mail de notificacoes e firmware de comandos; nao ha
   firmware neste repositorio e a app ainda nao regista tokens push.
5. Provisionar infraestrutura de producao conforme `backend/DEPLOYMENT.md`.
6. Definir retencao/arquivo de valores antes de criar uma rotina de purga.

## 13. Segurança e observações técnicas

-   Nunca incluir `.env`, passwords, tokens de acesso ou credenciais
    MQTT no repositório.
-   O `DeviceResponse` nao expoe `token` nem `mqtt_password`. Apenas
    os endpoints de criacao/rotacao exibem segredos uma vez;
    `mqtt_password` fica em hash na BD. Credenciais perdidas exigem
    reprovisionamento do dispositivo.
-   Mensagens MQTT são autenticadas pelo broker com credenciais individuais
    e ACL por dispositivo; a ingestão também compara o token do payload
    em tempo constante. Configurar TLS nos listeners e no tráfego entre
    EMQX e API antes de expor estes serviços fora da rede local.
-   Validar autorização em cada endpoint com base no recurso e no
    utilizador, não apenas por conhecer um UUID.
-   A validação de unicidade no serviço deve ser complementada por uma
    constraint na base de dados.
-   A dependência `get_db()` foi corrigida para fazer commit em sucesso
    e rollback em exceção. Preservar esse comportamento ou substituí-lo
    apenas por uma estratégia transacional equivalente e testada.
-   Em SQLAlchemy assíncrono, evitar lazy loading implícito de relações;
    usar consultas explícitas ou `selectinload` quando necessário para
    prevenir `MissingGreenlet`.
-   Rever migrations autogeradas antes de as aplicar.
-   **Dev local no Windows**: `python -m uvicorn app.main:app` deixa o
    uvicorn criar o event loop (ProactorEventLoop, o padrão do asyncio no
    Windows) antes de `app/main.py` sequer ser importado — definir a
    policy de loop lá dentro já não tem efeito. O ProactorEventLoop não
    implementa `add_reader`/`add_writer`, que o `aiomqtt` precisa, por
    isso o MQTT falha a ligar-se sempre, em silêncio. Usar
    `venv/Scripts/python.exe run_dev.py --port 8000` em vez do `uvicorn`
    direto — define a `WindowsSelectorEventLoopPolicy` antes de importar
    o próprio uvicorn. Só afeta Windows; em produção (Linux) corre-se
    `uvicorn app.main:app` normalmente, sem este problema.
-   O código que compila não está necessariamente livre de erros de
    importação ou de execução; validar imports e testar endpoints.
-   Antes de producao, definir rate limiting, auditoria, backups, TLS e
    retencao de dados; CORS exige origens explicitas quando `DEBUG=False`.

## 14. Estado atual resumido

| Area | Estado |
| --- | --- |
| API e dados | FastAPI, PostgreSQL e migrations aplicados ate `c1d8e7a4f602` |
| RBAC e acesso | Permissoes globais mais leitura por membro e escrita pelo dono do projeto |
| Dispositivos | CRUD, rotacao MQTT e provisionamento de credenciais em uso unico |
| Datastreams e historico | Tipos limitados; CRUD, valores atuais e historico implementados |
| Password reset | Fluxo implementado; precisa de SMTP configurado |
| MQTT local | Secret criado; EMQX nao foi reiniciado/validado (Docker indisponivel) |
| Notificacoes | Persistidas na app; push/e-mail ainda pendentes |
| Producao | Runbook pronto; host, TLS, backups e monitorizacao por provisionar |
| Retencao de dados | Politica ainda por decidir |
| CI | Workflow configurado; aguarda execucao remota em push/PR |

------------------------------------------------------------------------

**Este README é um retrato de continuidade do desenvolvimento**, baseado
no estado registado durante as sessões de trabalho. Antes de usar como
documentação oficial de release, confirmar os ficheiros atuais, a lista
real de rotas em `/docs`, as migrations existentes e o estado efetivo da
base de dados.
