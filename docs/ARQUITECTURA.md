# Documentación de arquitectura — Lite Thinking 2026

> Prueba técnica: aplicación de inventario con capa de dominio desacoplada,
> Django + FastAPI, agente IA local y anclaje del PDF en blockchain.
> El diagrama visual está en [`arquitectura.drawio`](./arquitectura.drawio)
> (ábrelo en [diagrams.net](https://app.diagrams.net)).

---

## 1. Estructura del monorepo — qué es cada carpeta y por qué se llama así

Es un **monorepo**: todos los componentes viven en un solo repositorio para que
la capa de dominio pueda compartirse por ruta (`path dependency`) entre el
backend y los servicios sin publicar un paquete.

```
lite/
├── domain/         Capa de dominio (Python puro, Poetry)
├── backend/        Django + DRF (aplicación + infraestructura)
├── services/       FastAPI (microservicios)
├── frontend/       Next.js (interfaz)
├── infra/          Scripts de inicialización de infraestructura
├── openspec/       Planificación spec-driven (propuestas, diseño, specs)
├── docs/           Esta documentación
├── docker-compose.yml
└── .env / .env.example
```

### `domain/` — el corazón del negocio
Se llama **domain** por la terminología de *Clean Architecture* / DDD: la capa
que contiene entidades y reglas de negocio, sin saber nada de frameworks. Es la
capa hacia la que apuntan todas las dependencias, y no importa a nadie.

```
domain/
├── pyproject.toml          Entregable exigido por el enunciado (gestión con Poetry)
└── src/domain/
    ├── entities/           Company · Product · User · Inventory
    ├── value_objects/      Money (multi-moneda) · Nit · Role
    ├── rules/              permisos por rol (can_manage_companies, …)
    └── errors.py           excepciones de dominio (nunca HTTP)
```
- **`entities`**: objetos con identidad e invariantes (una Empresa se identifica
  por su NIT). Son `@dataclass(frozen=True)` → inmutables.
- **`value_objects`**: objetos sin identidad, definidos por su valor. `Money` es
  el que resuelve "precio en varias monedas"; `Role` modela Admin/Externo.
- **`rules`**: la política de autorización en términos de negocio; el backend la
  invoca en vez de reimplementarla.
- Un test guardián (`tests/test_framework_independence.py`) **falla la build** si
  alguien importa Django, FastAPI o SQLAlchemy aquí. Así el desacoplamiento no es
  una promesa, es una regla verificada.

### `backend/` — Django, el emisor de identidad
Se llama **backend** porque es la capa de aplicación + infraestructura principal:
expone la API REST, autentica, aplica roles y persiste. Django es el **único
emisor** del token JWT.

```
backend/
├── config/                 settings · urls · wsgi
├── apps/                   apps de Django (una por capacidad)
│   ├── accounts/           Usuario (login por correo), emisión de JWT, permisos
│   ├── companies/          CRUD Empresa (NIT como PK)
│   └── products/           CRUD Producto (multi-moneda) + inventario
└── infrastructure/
    └── events/             publisher de eventos a Redis
```
- **`apps`**: convención de Django; cada "app" es un módulo cohesivo. Se nombran
  en plural (`companies`, `products`) siguiendo el estilo idiomático de Django.
- **`config`**: nombre neutral para el proyecto Django (settings/urls), en vez de
  acoplar el nombre del proyecto al de una app.
- **`infrastructure/events`**: separa un detalle de infraestructura (publicar a un
  broker) de la lógica de las apps.

### `services/` — FastAPI, el validador
Se llama **services** (plural) porque hospeda **varios servicios acotados** dentro
de una misma app FastAPI: documentos, agente IA y blockchain. FastAPI **valida**
el token que Django emitió; nunca emite uno.

```
services/
└── app/
    ├── main.py             monta routers + arranque (lifespan)
    ├── config.py           settings tipadas (pydantic-settings)
    ├── auth.py             valida el JWT (offline) + require_admin
    ├── db.py               engine SQLAlchemy
    ├── documents/          PDF (ReportLab) + email (Resend)
    ├── ai_agent/           embeddings · indexer · agente RAG + tools
    └── blockchain/         contrato Solidity + cliente web3
```
- **`ai_agent`**, **`documents`**, **`blockchain`**: cada subcarpeta es un
  *bounded context* con su router. Nombres en inglés y en singular por convención
  de módulos Python.

### `frontend/` — Next.js con Atomic Design
```
frontend/src/
├── app/                    rutas (App Router): login, companies, products, inventory, agent
├── components/
│   ├── atoms/              Button · Input · Label · Card · Badge
│   ├── molecules/          FormField · PriceInput
│   ├── organisms/          formularios, tablas, NavBar, AgentChat, BlockchainPanel
│   └── templates/          PageShell (layout + guardia de auth)
└── lib/                    api.ts (un cliente, mismo Bearer) · auth.tsx (rol del JWT)
```
Las carpetas **atoms / molecules / organisms / templates** son literalmente los
niveles de **Atomic Design** (exigido por el enunciado): componentes que se
componen de menor a mayor complejidad.

### `infra/` y `openspec/`
- **`infra/`**: scripts que preparan la infraestructura (p. ej. `postgres/init.sql`
  habilita la extensión `pgvector`). Nombre corto y universal para "plomería".
- **`openspec/`**: artefactos de planificación *spec-driven* (propuestas, diseño,
  specs, tareas). Es la memoria del "por qué" de cada cambio.

---

## 3. Por qué cada tecnología

| Tecnología | Dónde | Por qué se eligió |
|---|---|---|
| **Poetry** | `domain/` | Exigido por el enunciado para la capa de dominio; `pyproject.toml` es entregable. Permite consumir el dominio por ruta desde backend y services. |
| **Python (puro)** | `domain/` | La capa de dominio debe ser independiente de frameworks; Python plano lo garantiza. |
| **Django + DRF** | `backend/` | ORM maduro, migraciones, panel admin y sistema de auth/roles listos. Ideal para el CRUD y como emisor de identidad. |
| **djangorestframework-simplejwt** | `backend/` | Emisión de JWT con claims personalizados (`rol`, `type`) que FastAPI valida. |
| **Argon2** | `backend/` | Hashing de contraseñas fuerte (requisito f del enunciado). |
| **FastAPI** | `services/` | Async y liviano; encaja para microservicios aislados (PDF/email, IA, blockchain) que solo validan el token. |
| **SQLAlchemy** | `services/` | Exigido por el enunciado. Vive en FastAPI (no en Django, que ya tiene ORM): **lee** las tablas core y **posee** la tabla de embeddings. |
| **PostgreSQL + pgvector** | infra | Base relacional + búsqueda vectorial para el agente IA (embeddings semánticos). |
| **Redis Streams** | infra | Broker de eventos pub/sub para desacoplar el indexado de embeddings (con persistencia y ack). |
| **Ollama (qwen2.5, nomic-embed-text)** | host | Ejecuta el LLM y los embeddings **100% local**, sin llaves de nube; `qwen2.5` es fuerte en tool-calling. |
| **LangChain / LangGraph** | `services/ai_agent` | Orquestación del agente y de las herramientas (tool-calling ReAct). |
| **Next.js + React** | `frontend/` | Exigidos por el enunciado; App Router, renderizado estático (buen Lighthouse). |
| **Tailwind CSS** | `frontend/` | Estilos utilitarios, bundle pequeño, encaja con componentes atómicos. |
| **ReportLab** | `services/documents` | Generación de PDF en Python; configurado determinista para el hash de blockchain. |
| **Resend** | `services/documents` | API REST de envío de correo (requisito d), sin montar un SMTP propio. |
| **web3.py + Solidity + Anvil** | `services/blockchain` | Blockchain real (smart contract) pero **local** (Anvil), sin fondos ni testnet. |
| **Docker Compose** | raíz | Levanta todo el sistema (6 servicios) de forma reproducible. |
| **OpenSpec** | `openspec/` | Flujo spec-driven: explore → propose → apply → archive; documenta el porqué. |

---

## 4. Cómo se comunican los componentes

### 4.1 Regla de dependencias (compile-time)
```
frontend ─▶ backend ─▶ domain ◀─ services
                         ▲
        domain no importa a nadie; backend y services lo importan por ruta
```

### 4.2 Autenticación: un emisor, muchos validadores
```
Frontend --login (correo+contraseña)--> Django
Django   --firma JWT { sub, rol, type } con JWT_SIGNING_KEY (HS256)--> Frontend
Frontend --MISMO Bearer--> Django (CRUD)  y  --MISMO Bearer--> FastAPI (PDF/IA/blockchain)
FastAPI  --valida la firma OFFLINE con la misma llave, lee el claim `rol`--> autoriza
```
FastAPI **nunca** emite tokens ni consulta a Django para validarlos: comparten la
llave y el rol viaja dentro del token.

### 4.3 CRUD (síncrono)
`Frontend → Django (DRF)`. Las escrituras construyen la **entidad de dominio**
(que valida las reglas) antes de persistir con el ORM. Escrituras = admin;
lectura de empresas = cualquiera autenticado (visitante Externo).

### 4.4 Indexado de embeddings (pub/sub, sin usuario)
```
Django (al crear/editar/borrar un producto)
   --publica evento product.created|updated|deleted--> Redis Streams
Redis --el indexer de FastAPI consume--> genera embedding (Ollama)
FastAPI --UPSERT/DELETE del vector--> PostgreSQL/pgvector
```
Se usa pub/sub aquí porque no hay un usuario en el request: el hecho se publica y
nadie llama a nadie, así que "sin usuario, sin token" deja de ser un problema.

### 4.5 Agente IA (RAG + herramientas)
```
Frontend --pregunta (Bearer admin)--> FastAPI /agent/chat
FastAPI --require_admin--> agente ReAct (LangGraph, qwen2.5 vía Ollama)
   herramientas: search_products (pgvector) · list_companies · count_products
                 inventory_summary · send_inventory_email · anchor_inventory
FastAPI --responde solo con el resultado de las tools (guardrail anti-alucinación)-->
```

### 4.6 PDF + correo (síncrono)
```
Frontend --Bearer--> FastAPI /inventory/pdf     → descarga PDF (ReportLab)
Frontend --Bearer--> FastAPI /inventory/send     → PDF + envío por Resend (BackgroundTasks)
```

### 4.7 Blockchain (anclaje de integridad)
```
FastAPI --al arrancar--> despliega DocumentRegistry en Anvil (web3.py) y guarda la
                         dirección en PostgreSQL (blockchain_deployment)
Frontend --Bearer admin--> /inventory/anchor  → SHA-256 del PDF → anchor(hash) on-chain
Frontend --Bearer--> /inventory/verify (sube un PDF) → recomputa el hash → verify(hash)
```
El PDF se genera **determinista** (`reportlab invariant`) para que su hash sea
función pura del contenido y un PDF descargado luego verifique correctamente.

---

## 5. Modelo de datos (resumen)

| Tabla | Dueño | Contenido |
|---|---|---|
| `accounts_user` | Django | correo (login), rol, hash Argon2 |
| `companies_company` | Django | **nit (PK)**, name, address, phone |
| `products_product` | Django | code, name, characteristics, company (FK), quantity |
| `products_productprice` | Django | product (FK), currency, amount (una fila por moneda) |
| `ai_product_embedding` | FastAPI | vector(768) + metadata (company_id, precio…) para RAG híbrido |
| `blockchain_deployment` | FastAPI | chain_id (PK), address, abi del contrato desplegado |

En cadena (Anvil): `DocumentRegistry` guarda `hash → timestamp` (first-write-wins).

---

## 6. Cómo correr

```bash
cp .env.example .env          # completar llaves si se usan (Resend, etc.)
# Ollama en el host: ollama pull qwen2.5 && ollama pull nomic-embed-text
docker compose up --build
# crear admin:
docker compose exec backend poetry run python manage.py createsuperuser --email admin@acme.com
```
- Frontend: http://localhost:3000 · Django: :8000 · FastAPI: :8001 · Anvil: :8545

