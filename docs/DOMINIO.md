# La capa de dominio — a fondo

> Documento complementario de [`ARQUITECTURA.md`](./ARQUITECTURA.md).
> El diagrama del flujo del mapper está en la **página 2** de
> [`arquitectura.drawio`](./arquitectura.drawio).

La capa de dominio (`domain/`) es el componente más evaluado del enunciado
(clause h/i) y el centro conceptual del sistema. Este documento explica **por qué
existe, para qué, cómo se comunica y cómo está construida**.

---

## 1. Por qué existe

**Razón del enunciado (clause h/i):** los modelos/entidades del negocio deben
vivir en una capa de dominio **independiente del Backend**, en Python, siguiendo
Arquitectura Limpia, desacoplada de vistas, serializers, controladores y lógica
HTTP; gestionada con **Poetry** y consumida desde el Backend.

**Razón de ingeniería — Inversión de Dependencias:** sin capa de dominio, las
reglas del negocio terminan dentro del framework (p. ej. en un serializer de
Django), y entonces el negocio *depende* del framework. La capa de dominio
invierte esa flecha: los detalles (DB, HTTP, framework) dependen del negocio, no
al revés.

```
   SIN dominio                          CON dominio
   Django ──contiene──► reglas          Django ─►┐
   (cambiar de framework                FastAPI ─►│──► domain (reglas)
    = reescribir el negocio)                      └ las flechas apuntan al negocio;
                                                    el negocio no apunta a nadie
```

---

## 2. Para qué existe

| Beneficio | Cómo se ve aquí |
|---|---|
| **Fuente única de verdad** | "no se suma USD con COP" vive en `Money`, no repetida en cada endpoint |
| **Consistencia entre 2 backends** | Django y FastAPI importan el **mismo** `Role` y `can_use_ai_agent` → política idéntica |
| **Testabilidad** | 19 pruebas del dominio corren en ~0.02 s, sin DB ni HTTP |
| **Independencia verificada** | un test recorre el AST y falla la build si aparece `import django` |
| **Infraestructura reemplazable** | cambiar Django/Postgres no afecta al dominio |

---

## 3. Cómo se comunica con todo

Clave: **el dominio NO hace I/O**. No abre conexiones, no llama HTTP, no toca la
DB. No "se comunica" en runtime — **lo importan y lo llaman**. Tres formas:

### (a) Dependencia de código (compile-time)
```toml
# en backend/ y services/ pyproject.toml
domain = { path = "../domain", develop = true }
```
Es una librería compartida por ruta, no un servicio en red. Por eso en el
diagrama las flechas hacia `domain` son **punteadas** (import), no continuas.

### (b) Patrón Mapper (traductor en la frontera)
Un `mapper` traduce entre el modelo Django (infraestructura) y la entidad de
dominio (negocio):

```python
# backend/apps/companies/mappers.py
def validate_with_domain(nit, name, address, phone) -> DomainCompany:
    return DomainCompany.create(nit=nit, name=name, address=address, phone=phone)
```

Flujo de una escritura (ver diagrama, página 2):
```
POST /api/companies/ (JSON)
  → CompanySerializer.validate()
      → validate_with_domain(...)
          → Company.create(...)         construye la entidad
              → __post_init__ valida     si algo falla → ValidationError (dominio)
      ← el serializer atrapa ValidationError → HTTP 400
  → si válido: mapper → Django ORM → PostgreSQL
```

Detalle elegante: **la validación ocurre al construir la entidad**. No hay un
`validate()` aparte; si logras crear el objeto, es porque es válido
("objeto construido = objeto válido").

### (c) Política compartida (reglas importadas por ambos backends)
```python
# backend/apps/accounts/permissions.py  y  services/app/auth.py
from domain.rules import can_manage_companies, can_use_ai_agent
from domain.value_objects import Role
```
```
        ┌────────────── domain ──────────────┐
        │ Role · can_use_ai_agent · can_manage│
        └──▲──────────────────────────▲───────┘
           │ import                    │ import
  Django permissions.py        FastAPI auth.py
  (autoriza el CRUD)           (autoriza agente/PDF)
```

> **Matiz honesto:** en la ruta de *lectura* de FastAPI (RAG, PDF) se usan modelos
> SQLAlchemy directamente como *read-models*, no entidades de dominio. Es correcto
> en Clean Architecture: las proyecciones de lectura pueden saltarse el dominio;
> las **escrituras** y las **reglas de autorización** nunca lo hacen.

---

## 4. Cómo está construido

Cuatro tipos de piezas, todas Python puro:

### Value Objects — inmutables, autovalidados, con comportamiento
```python
@dataclass(frozen=True)              # inmutable
class Money:
    amount: Decimal                  # Decimal, no float → sin redondeos
    currency: str
    def __post_init__(self):         # valida Y normaliza al construir
        if amount < 0: raise ValidationError(...)
        if currency not in _ALLOWED_CURRENCIES: raise ValidationError(...)
        object.__setattr__(self, "currency", currency.upper())
    def add(self, other):            # comportamiento con reglas
        self._assert_same_currency(other)      # rechaza mezclar monedas
        return Money(self.amount + other.amount, self.currency)
```
Tres ideas: **inmutabilidad** (`frozen=True`), **validación en el constructor**
(`__post_init__`) y **comportamiento** (`add` lanza `CurrencyMismatchError` al
sumar USD+COP). `Money` resuelve "precio en varias monedas". `Nit` valida la
identidad de Empresa; `Role` modela Admin/Externo.

### Entities — identidad e invariantes
```python
@dataclass(frozen=True)
class Company:
    nit: Nit                         # la identidad es un value object validado
    name: str; address: str; phone: str
    def __post_init__(self):
        if not self.name.strip(): raise ValidationError("...")
    @classmethod
    def create(cls, nit: str, ...):  # factory: strings crudos → value objects
        return cls(nit=Nit(nit), ...)
```
Entidades: `Company`, `Product`, `User`, `Inventory`.

### Rules — funciones puras de política
```python
def can_use_ai_agent(role: Role) -> bool:
    return role.is_admin
```

### Errors — excepciones de dominio, jamás HTTP
```python
class DomainError(Exception): ...
class ValidationError(DomainError): ...        # el serializer la traduce a 400
class CurrencyMismatchError(DomainError): ...  # el dominio nunca conoce códigos HTTP
```

### El guardián que lo hace real
```python
# domain/tests/test_framework_independence.py
FORBIDDEN_ROOTS = {"django","rest_framework","fastapi","sqlalchemy","redis","httpx",...}
# recorre el AST de cada .py del dominio y falla si importa alguno
```
Convierte "está desacoplado" en un invariante verificado por CI.

### Empaquetado
```
domain/
├── pyproject.toml          Poetry (entregable clause i), layout src/
└── src/domain/
    ├── entities/  value_objects/  rules/  errors.py
    └── __init__.py         API pública: from domain import Company, Money, Role, …
```

---

## En una frase

El dominio es un **paquete Python puro, inmutable y autovalidante**, que backend y
services **importan por ruta**; concentra las **entidades**, las **reglas** y la
**política de autorización**, y un **test guardián** garantiza que nunca se
contamine con un framework.
