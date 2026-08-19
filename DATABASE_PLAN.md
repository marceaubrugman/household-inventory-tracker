# Household Inventory Tracker Database Plan

## Purpose

This document describes the database architecture of the Household Inventory Tracker, or HIT.

It records:

* the PostgreSQL implementation introduced in v0.2.0
* how the FastAPI interface added in v0.3.0 reuses the same database foundation
* how Dockerized local development added in v0.4.0 runs PostgreSQL through Docker Compose
* how GitHub Actions added in v0.5.0 verifies Python behavior, PostgreSQL integration, and Docker image builds
* how v0.6.0 introduced quantity and individual tracking modes through sequential PostgreSQL migrations
* how v0.7.0 made Docker startup reproducible through service health checks, readiness-based startup ordering, and automatic first-run schema initialization
* the responsibilities of the database, repository, service, and interface layers
* current security, validation, migration, and integrity decisions
* the migration path from the legacy JSON format
* likely future database evolution

The current database model remains intentionally focused. It supports quantity-tracked supplies and individually tracked durable assets in one inventory table, providing a reliable PostgreSQL foundation before introducing users, households, audit history, structured locations, automated migration tooling, and more advanced search.

## Current Status

**Implemented through HIT v0.7.0**

PostgreSQL is the primary source of truth for inventory data.

The previous JSON runtime storage has been removed from the application. JSON remains supported only as a legacy migration source. Imported legacy records use quantity tracking.

HIT now distinguishes between:

* `quantity` items, which require non-negative `quantity` and `minimum_quantity` values
* `individual` items, which represent distinct durable assets and require both quantity fields to be `NULL`

The `tracking_mode` domain rule is enforced across API schemas, service behavior, repository operations, and PostgreSQL constraints. PostgreSQL remains the final integrity boundary.

v0.6.0 introduced the first explicit sequential schema-upgrade path:

```text
sql/migrations/001_add_tracking_mode.sql
sql/migrations/002_add_tracking_mode_quantity_rules.sql
```

Migration tests upgrade a frozen v0.5.0 schema fixture and verify that existing data is preserved and backfilled to quantity tracking.

HIT can run PostgreSQL in two local development modes:

* manually managed PostgreSQL using a local `DATABASE_URL`
* Docker Compose PostgreSQL using the `db` service and local `.env` configuration

Docker Compose is intended for reproducible local development. In v0.7.0, PostgreSQL gained a Docker health check, the API waits for PostgreSQL to become healthy before startup, the API gained its own Docker health check, and a fresh PostgreSQL volume automatically applies `sql/schema.sql` through `/docker-entrypoint-initdb.d/`. Existing volumes skip initialization and preserve their data. These changes do not alter PostgreSQL’s role as the source of truth or move SQL out of the repository layer.

GitHub Actions, introduced in v0.5.0, verifies non-integration Python tests, PostgreSQL integration tests, and Docker image builds on pushes and pull requests.

## Current Persistence Architecture

### Console path

```text
app.py
   ↓
inventory_workflows.py
   ↓
item_repository.py
   ↓
database.py
   ↓
PostgreSQL
```

### API path

```text
Uvicorn
   ↓
FastAPI
   ↓
API routers and dependencies
   ↓
item_service.py
   ↓
item_repository.py
   ↓
database.py
   ↓
PostgreSQL
```

### Docker local development path

```text
docker compose
   ↓
api service
   ↓
FastAPI / Uvicorn
   ↓
API routers and dependencies
   ↓
item_service.py
   ↓
item_repository.py
   ↓
database.py
   ↓
db service
   ↓
PostgreSQL 18
```

The console and FastAPI interfaces use the same PostgreSQL schema, repository functions, and connection layer.

FastAPI does not connect directly to PostgreSQL. API requests pass through Python API, service, repository, and database layers.

Inside Docker Compose, the API connects to PostgreSQL using the Compose service name:

```text
db
```

The Docker Compose database connection string is provided through `.env` as:

```text
DATABASE_URL=postgresql://hit_user:hit_password@db:5432/hit
```

Tracking-mode data flows through all persistence-facing layers. The API can create both tracking modes and perform atomic transitions between them. The console currently remains quantity-oriented, but updates preserve the stored tracking mode of existing records.

## Database Environments

### Manual development database

```text
hit_db
```

Used by:

* the console application when run manually
* the FastAPI application when run manually with Uvicorn
* database connection diagnostics
* manual development and smoke testing

The connection string is read from:

```text
DATABASE_URL
```

Example manual local format:

```text
postgresql://USERNAME:PASSWORD@localhost:5432/hit_db
```

### Docker Compose development database

```text
hit
```

Used by:

* the FastAPI application running inside the Docker Compose `api` service
* PostgreSQL running inside the Docker Compose `db` service
* Docker Compose smoke testing
* the `/db-health` endpoint

The Docker Compose connection string is defined in `.env`:

```text
DATABASE_URL=postgresql://hit_user:hit_password@db:5432/hit
```

Inside Docker Compose, the hostname is:

```text
db
```

not:

```text
localhost
```

The Docker Compose PostgreSQL data is persisted in a named Docker volume.

### Integration-test database

```text
hit_test
```

Used only by PostgreSQL integration tests.

The connection string is read from:

```text
TEST_DATABASE_URL
```

The development, Docker Compose, and test databases must remain separate.

## PostgreSQL Schema

HIT database objects are stored in:

```text
hit
```

The current inventory table is:

```text
hit.items
```

The schema definition is stored in:

```text
sql/schema.sql
```

## Current Schema Definition

```sql
CREATE SCHEMA IF NOT EXISTS hit;

CREATE TABLE IF NOT EXISTS hit.items (
    id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    tracking_mode VARCHAR(20) NOT NULL DEFAULT 'quantity'
        CONSTRAINT tracking_mode_allowed
        CHECK (tracking_mode IN ('quantity', 'individual')),
    quantity INTEGER
        CONSTRAINT quantity_non_negative CHECK (quantity >= 0),
    minimum_quantity INTEGER
        CONSTRAINT minimum_quantity_non_negative CHECK (minimum_quantity >= 0),
    notes TEXT NOT NULL DEFAULT '',
    CONSTRAINT tracking_mode_quantity_fields
    CHECK (
        (
            tracking_mode = 'quantity'
            AND quantity IS NOT NULL
            AND minimum_quantity IS NOT NULL
        )
        OR
        (
            tracking_mode = 'individual'
            AND quantity IS NULL
            AND minimum_quantity IS NULL
        )
    )
);
```

The standalone schema represents the final v0.6.0 database model and remains unchanged in v0.7.0. Fresh Docker environments now apply this schema automatically. Existing v0.5.0 databases are upgraded through the sequential SQL files in `sql/migrations/`.

## Field Definitions

### `id`

```text
INTEGER GENERATED BY DEFAULT AS IDENTITY
```

Purpose:

* uniquely identifies an inventory item
* is generated automatically by PostgreSQL
* can accept an explicit value during controlled legacy migration

`BY DEFAULT` was selected instead of `ALWAYS` because the JSON migration tool preserves existing v0.1 item IDs.

### `name`

```text
VARCHAR(100) NOT NULL
```

The human-readable item name.

Examples:

```text
Rice
Dish soap
Cordless drill
```

### `category`

```text
VARCHAR(100) NOT NULL
```

The broad grouping of the item.

Examples:

```text
Food
Cleaning
Bathroom
Electronics
Tools
```

Categories are currently stored directly on each item. They may become a separate table later if reusable metadata, category management, reporting, or permissions require it.

### `location`

```text
VARCHAR(100) NOT NULL
```

The household storage location of the item.

Examples:

```text
Pantry
Kitchen cabinet
Upstairs closet
Garage
```

Locations are currently stored directly on each item. They may later become structured household locations.

### `tracking_mode`

```text
VARCHAR(20) NOT NULL DEFAULT 'quantity'
```

The inventory behavior assigned to the item.

Allowed values:

```text
quantity
individual
```

`quantity` represents consumable or countable stock whose level can increase or decrease.

`individual` represents one distinct durable asset, such as a drill, bicycle, or appliance.

Existing v0.5.0 records are backfilled to `quantity` during migration. The database rejects unsupported tracking modes.

### `quantity`

```text
INTEGER CHECK (quantity >= 0)
```

For a quantity-tracked item, this stores the current stock quantity.

Zero is valid and represents stock that is known but currently unavailable.

For an individually tracked item, this field must be:

```text
NULL
```

Negative values are rejected by:

* console validation where quantity input is exposed
* Pydantic API validation
* PostgreSQL constraints

### `minimum_quantity`

```text
INTEGER CHECK (minimum_quantity >= 0)
```

For a quantity-tracked item, this stores the level at which the item should be considered low stock.

The current low-stock rule is:

```sql
quantity <= minimum_quantity
```

An item is therefore low stock when its quantity is:

* below the configured minimum
* exactly equal to the configured minimum

For an individually tracked item, this field must be:

```text
NULL
```

### Combined tracking-mode rule

PostgreSQL enforces the valid field combinations:

```text
quantity mode
    → quantity is not NULL
    → minimum_quantity is not NULL

individual mode
    → quantity is NULL
    → minimum_quantity is NULL
```

This prevents ambiguous records such as an individual asset with a stock count or a quantity-tracked supply without quantity data.

### `notes`

```text
TEXT NOT NULL DEFAULT ''
```

Optional free-form information about an item.

The current PostgreSQL representation stores an empty note as:

```text
''
```

rather than `NULL`.

The API may accept `null` when clearing notes, but the repository and database normalize the persisted value according to the current schema contract.

## Repository Operations

The PostgreSQL repository supports complete CRUD functionality plus search, sorting, and low-stock retrieval.

Every returned item dictionary includes:

```text
id
name
category
location
tracking_mode
quantity
minimum_quantity
notes
```

## Create

Repository function:

```python
create_item(...)
```

The function accepts `tracking_mode`, which defaults to `quantity` for compatibility with earlier callers.

SQL behavior:

```sql
INSERT INTO hit.items (...)
VALUES (...)
RETURNING ...;
```

PostgreSQL generates the item ID and returns the complete created row.

Valid domain combinations include:

```text
quantity
    → non-negative quantity
    → non-negative minimum_quantity

individual
    → NULL quantity
    → NULL minimum_quantity
```

Used by:

* console workflows for quantity-tracked items
* FastAPI service operations for both tracking modes

## Read All

Repository function:

```python
get_all_items(sort_key="name")
```

The database returns all quantity and individual inventory items in an approved sort order.

Supported sort keys:

* name
* category
* location
* quantity

The FastAPI `GET /items` endpoint currently reuses this repository operation through `item_service.py`.

## Read One

Repository function:

```python
get_item_by_id(item_id)
```

SQL behavior:

```sql
SELECT ...
FROM hit.items
WHERE id = %s;
```

The function returns:

* one item dictionary when found
* `None` when no matching ID exists

The API converts `None` into:

```text
404 Not Found
```

## Search

Repository function:

```python
search_items(search_term)
```

Search covers:

* name
* category
* location

The current query uses PostgreSQL `ILIKE` for case-insensitive partial matching.

Conceptually:

```sql
WHERE name ILIKE pattern
   OR category ILIKE pattern
   OR location ILIKE pattern
```

User-supplied `%` and `_` characters are escaped so they are treated literally rather than as unintended SQL pattern wildcards.

Search remains available through the console. A dedicated API search capability is planned for a later version.

## Update

Repository function:

```python
update_item(...)
```

SQL behavior:

```sql
UPDATE hit.items
SET ...
WHERE id = %s
RETURNING ...;
```

The repository receives and persists a complete item state, including `tracking_mode`.

For the API:

1. `item_service.py` loads the current item
2. merges only supplied PATCH fields
3. rejects unsupported update fields
4. validates tracking-mode transition requirements
5. sends a complete valid state to the repository
6. returns the refreshed item

A request that changes `tracking_mode` must include both quantity fields in a state valid for the target mode. This makes the transition atomic and prevents half-converted records.

The console does not currently expose tracking-mode changes, but its update flow preserves the existing stored mode.

This keeps HTTP partial-update behavior out of the repository and SQL layers.

## Delete

Repository function:

```python
delete_item(item_id)
```

SQL behavior:

```sql
DELETE FROM hit.items
WHERE id = %s
RETURNING ...;
```

The deleted row is returned so the console application can confirm exactly what was removed.

The API currently translates successful deletion into:

```text
204 No Content
```

The API does not return the deleted row, even though the repository makes it available.

## Low-Stock Retrieval

Repository function:

```python
get_low_stock_items(sort_key="name")
```

The low-stock condition is evaluated in PostgreSQL:

```sql
WHERE tracking_mode = 'quantity'
  AND quantity <= minimum_quantity
```

This explicitly excludes individually tracked assets and avoids retrieving the complete inventory for filtering in Python.

Low-stock retrieval remains available through the console. A dedicated API endpoint or query parameter is planned for a later version.

## Sorting Strategy

PostgreSQL performs inventory sorting through `ORDER BY`.

Text fields use case-insensitive expressions:

```sql
LOWER(name)
LOWER(category)
LOWER(location)
```

Quantity is sorted numerically:

```sql
quantity
```

Individually tracked assets contain `NULL` quantity values. They remain valid inventory records and are not treated as low stock.

Each query also uses `id` as a stable secondary sort:

```sql
ORDER BY selected_expression, id
```

## Secure Dynamic Sorting

SQL values can be passed through Psycopg placeholders, but column names and SQL expressions cannot.

HIT therefore uses a strict allowlist:

```python
SORT_EXPRESSIONS = {
    "name": sql.SQL("LOWER(name)"),
    "category": sql.SQL("LOWER(category)"),
    "location": sql.SQL("LOWER(location)"),
    "quantity": sql.Identifier("quantity"),
}
```

Raw user input is never inserted directly into an `ORDER BY` clause.

Unsupported sort keys raise:

```python
ValueError
```

## SQL Security

### Parameterized statements

All user-controlled values are passed separately from SQL statements:

```python
cursor.execute(query, parameters)
```

The SQL uses Psycopg placeholders:

```sql
%s
```

This prevents user data from being interpreted as executable SQL structure.

Parameterized execution is used for:

* item names
* categories
* locations
* tracking modes
* quantities
* notes
* search patterns
* item IDs

### SQL identifiers and expressions

Dynamic SQL expressions such as sorting columns are handled through:

* a fixed allowlist
* Psycopg SQL composition
* approved `sql.SQL` and `sql.Identifier` objects

### API input boundaries

The FastAPI interface adds another defensive layer through Pydantic validation.

The API currently validates:

* required text fields
* string lengths
* allowed tracking-mode values
* valid tracking-mode and quantity combinations
* non-negative quantities
* positive integer item IDs
* non-empty partial update bodies
* required fields that may not be set to `null`
* atomic tracking-mode transition payloads

Pydantic validation improves the HTTP client experience, but PostgreSQL constraints remain the final data-integrity boundary.

### Credentials

Database credentials are not stored directly in Python source code.

The application reads:

```text
DATABASE_URL
```

Integration tests read:

```text
TEST_DATABASE_URL
```

For Docker Compose local development:

* `.env.example` is committed as a safe configuration template
* `.env` contains local development values
* `.env` is ignored by Git
* `.env` is not copied into the Docker image

Real connection strings remain in local environment variables, local `.env` files, or PyCharm run configurations and are excluded from Git.

### Connection timeout

Database connections use an explicit timeout:

```python
connect_timeout=5
```

This prevents the console or API from appearing to hang indefinitely when PostgreSQL is unavailable.

## Database Error Handling

### Console boundary

Expected Psycopg failures are handled at the console application boundary.

The user receives a safe message instead of raw database details.

### API boundary

The FastAPI application uses global exception handlers.

Current API behavior:

```text
Missing DATABASE_URL
    → 503 Service Unavailable

Psycopg OperationalError
    → server-side log entry
    → 503 Service Unavailable

Missing inventory item
    → 404 Not Found

Invalid path or request body
    → 422 Unprocessable Entity
```

Technical database information is not included in public API responses.

Programming defects and malformed SQL are not broadly converted into `503` responses. They remain visible as server errors so they can be diagnosed rather than disguised as infrastructure outages.

## Data Integrity

Data integrity is protected at multiple levels.

### Console application layer

Python validators reject:

* empty required text
* negative quantities
* invalid IDs
* malformed menu input

The current console remains quantity-oriented. When it updates an existing record, it preserves the stored tracking mode.

### API application layer

Pydantic and service validation reject:

* blank required text
* unsupported tracking modes
* invalid tracking-mode and quantity combinations
* negative quantities
* empty PATCH bodies
* invalid item IDs
* unsupported update fields
* attempts to clear required fields
* incomplete tracking-mode transitions

### Repository layer

The repository:

* uses parameterized SQL
* allowlists dynamic sort expressions
* keeps SQL isolated from interfaces
* reads and writes `tracking_mode`
* returns predictable dictionaries or `None`
* restricts low-stock retrieval to quantity-tracked items

### Database layer

PostgreSQL enforces:

* primary-key uniqueness
* required descriptive fields through `NOT NULL`
* allowed tracking-mode values
* a default quantity tracking mode
* non-negative quantity values when present
* quantity fields that match the selected tracking mode
* default empty notes

This creates defense in depth:

```text
console input or HTTP request
   ↓
Python or Pydantic validation
   ↓
service and transition rules where applicable
   ↓
parameterized repository operation
   ↓
PostgreSQL constraints
```

## Transactions

Repository operations use Psycopg connection context managers.

On successful completion:

```text
transaction committed
```

On failure:

```text
transaction rolled back
```

Each current repository operation uses a short transaction containing one logical database action.

More complex multi-step transactions may be introduced later when HIT supports workflows involving several related records.

## JSON Migration

HIT includes:

```text
scripts/migrate_json_to_postgres.py
```

The migration tool imports data from the v0.1 JSON format.

Legacy JSON has no tracking-mode field. Imported records therefore use the repository and database default:

```text
tracking_mode = quantity
```

### Migration safeguards

The migration:

* validates the complete JSON document before connecting to PostgreSQL
* requires a top-level list
* verifies required fields
* rejects duplicate IDs
* rejects invalid or negative quantities
* preserves legacy item IDs
* imports records as quantity-tracked items
* requires an empty target table
* requires explicit confirmation
* inserts all records in one transaction
* resets the identity sequence after importing explicit IDs

### Dry run

The migration can validate data without writing to PostgreSQL:

```bash
python -m scripts.migrate_json_to_postgres sample_inventory.json --dry-run
```

### Real migration

```bash
python -m scripts.migrate_json_to_postgres inventory.json
```

If any database operation fails, the complete migration is rolled back.

## Testing Strategy

The current suite contains 67 passing automated tests. v0.7.0 preserved the existing Python and PostgreSQL test coverage while adding release-level Docker lifecycle verification.

## Unit and service tests

Tests that do not require PostgreSQL cover:

* console input validation
* migration-data validation
* duplicate-ID rejection
* required migration fields
* quantity validation
* tracking-mode validation
* application-service behavior
* partial-update merging
* atomic tracking-mode transitions
* deletion outcomes

These tests use fakes and pytest monkeypatching.

## API endpoint tests

FastAPI endpoint tests cover:

* health checks
* database health checks
* list retrieval
* single-item retrieval
* quantity-item creation
* individual-item creation
* partial updates
* tracking-mode transitions
* deletion
* missing records
* invalid input
* missing database configuration
* PostgreSQL operational failures

FastAPI dependency overrides and monkeypatching keep most API tests isolated from PostgreSQL.

## Docker Compose lifecycle checks

Release-level Docker checks verify:

* a fresh PostgreSQL volume initializes `sql/schema.sql` automatically
* PostgreSQL becomes healthy through `pg_isready`
* the API starts only after PostgreSQL is healthy
* the API becomes healthy through its `/health` probe
* `/health` confirms API liveness
* `/db-health` confirms API-to-database connectivity
* direct PostgreSQL access works through `docker compose exec db psql`
* an existing volume skips initialization
* persisted data survives container recreation
* invalid PostgreSQL startup configuration produces a clear failure
* an unhealthy PostgreSQL dependency blocks API cold start
* host-level environment overrides can be diagnosed and corrected
* the stack stops cleanly with `docker compose down`

These remain release-level manual lifecycle checks. GitHub Actions separately verifies that the Docker image builds successfully on a clean Ubuntu runner.

## PostgreSQL integration tests

Integration tests execute real SQL against:

```text
hit_test
```

They verify:

* create, retrieve, update, and delete
* both tracking modes
* full-stack individual-item API behavior
* multi-field and case-insensitive search
* numeric sorting
* low-stock retrieval and individual-item exclusion
* PostgreSQL tracking-mode constraints
* migration of a frozen v0.5.0 schema without data loss

## Schema migration tests

Migration tests use:

```text
tests/integration/fixtures/schema_v0_5_0.sql
```

They apply the sequential v0.6.0 migration files and verify:

* existing records are preserved
* existing records are backfilled to quantity tracking
* the tracking-mode column receives its final default and constraints
* quantity fields become nullable
* combined tracking-mode quantity rules are enforced

## Test isolation

The integration fixture:

1. reads `TEST_DATABASE_URL`
2. temporarily redirects `DATABASE_URL`
3. checks the actual connected database name
4. refuses destructive cleanup unless the name ends with `_test`
5. prepares the required schema for each integration context
6. truncates test data where appropriate
7. resets identity values
8. cleans test state after execution

The safety check protects development databases from accidental integration-test cleanup.

When `TEST_DATABASE_URL` is absent, PostgreSQL integration tests skip intentionally.

## Continuous integration

GitHub Actions runs three independent jobs:

* non-integration Python tests
* PostgreSQL 18 integration tests against an isolated `hit_test` database
* Docker image build validation

CI runs on pushes and pull requests and uses read-only repository permissions.

## Current Database Decisions

### One inventory table

The current schema uses one table deliberately.

Both quantity-tracked supplies and individually tracked assets share descriptive fields and remain inside `hit.items`. The combined tracking-mode constraint makes their different quantity rules explicit without prematurely splitting the domain into separate tables.

This keeps the current PostgreSQL model:

* understandable
* testable
* easy to migrate
* suitable for learning direct SQL
* reusable by both console and API interfaces

Categories and locations are not normalized yet because the application does not currently require:

* category metadata
* location ownership
* reusable location hierarchies
* category-level permissions
* separate category-management operations

Normalization should follow real product requirements rather than be added for architectural decoration.

### Direct SQL before an ORM

HIT currently uses direct SQL through Psycopg rather than SQLAlchemy.

Reasons:

* reinforces PostgreSQL and SQL knowledge
* keeps database behavior visible
* supports secure parameter binding
* makes migration SQL and constraints explicit
* avoids introducing an abstraction before the schema stabilizes
* creates stronger foundations for understanding future ORM behavior
* keeps the current repository layer explicit and testable

An ORM may be considered later, but it is not required for the current application.

### Sequential SQL migrations before migration tooling

v0.6.0 introduced explicit numbered SQL migration files because the schema changed for the first time.

This approach currently provides:

* visible SQL changes
* an understandable upgrade sequence
* transaction boundaries inside each migration
* a frozen earlier schema for realistic upgrade testing
* data-preservation evidence

The project does not yet include an automated migration runner or migration-history table. Alembic should be evaluated only when growing migration complexity justifies the additional abstraction and dependency.

### Shared repository across interfaces

Both interfaces reuse:

```text
item_repository.py
database.py
PostgreSQL schema
```

This avoids:

* duplicate SQL
* inconsistent persistence rules
* interface-specific database behavior
* separate sources of truth

The API adds `item_service.py` above the repository for application operations such as partial-update merging and tracking-mode transitions.

The console retains `inventory_workflows.py` as its coordination layer and currently exposes quantity-oriented workflows while preserving stored modes during updates.

### Docker Compose for local development

HIT v0.4.0 introduced Docker Compose for local development.

The current Compose setup defines:

* HIT API service
* PostgreSQL 18 service
* environment configuration through `.env`
* persistent database volume
* service-to-service database networking
* PostgreSQL health checks through `pg_isready`
* API health checks through `/health`
* API startup ordering based on PostgreSQL `service_healthy`
* automatic first-run schema initialization from `sql/schema.sql`
* `/health` API liveness check
* `/db-health` API-to-database connectivity check

The Docker Compose setup is intended for local development. It is not a production deployment model.

Important operational distinctions established in v0.7.0:

* container process state and Docker health state are separate signals
* `/health` measures API liveness, while `/db-health` verifies PostgreSQL connectivity
* `depends_on: condition: service_healthy` controls startup ordering but does not provide runtime supervision after services are already running
* inside the API container, PostgreSQL is reached as `db`, not `localhost`
* host environment variables can override `.env` values during Compose configuration resolution
* changing a host environment variable does not mutate an already-running container; the affected container must be recreated

Future Docker database improvements may include:

* a non-root application user
* controlled migration execution
* clearer reset and seed workflows for local development

## Current Limitations

The current database model does not yet support:

* multiple households
* user accounts
* authentication
* item ownership
* permissions
* structured household locations
* category management
* stock-movement history
* audit trails
* attachments or images
* expiry dates
* barcode identifiers
* full-text search
* semantic search
* trusted-successor access
* production deployment
* automated migration execution
* migration-history tracking
* automated rollback procedures

The console currently does not expose:

* creation of individually tracked assets
* tracking-mode selection
* tracking-mode transitions

The API currently provides those tracking-mode operations, but it does not yet expose:

* search queries
* sorting options
* low-stock retrieval
* pagination

The Docker local development setup does not yet include:

* automatic migration execution for existing databases
* automated seed data
* automated Docker-based test execution
* production-grade runtime supervision or orchestration

These are future capabilities, not unfinished current-release work.

## Next Database Stage

The v0.7.0 Docker-startup milestone is complete at the feature and lifecycle-verification level and is undergoing final release Lock.

Future database work should continue in bounded slices. Likely candidates include:

* API search, sorting, low-stock, and pagination support
* an automated migration runner and migration-history table
* timestamps or audit-oriented fields when a concrete workflow requires them
* Azure deployment planning after the local and CI paths remain stable

The next slice should be selected through the project roadmap rather than introduced simultaneously. PostgreSQL should remain the source of truth, direct SQL should remain visible, and every schema change should include a tested upgrade path.

## Possible Future Database Evolution

### Users and households

Likely future tables:

```text
users
households
household_members
items
```

Items would eventually belong to a household rather than a single shared global inventory.

### Structured locations

Possible tables:

```text
locations
items
```

Locations may later support structures such as:

```text
House
└── Kitchen
    └── Pantry
        └── Top shelf
```

### Categories

Categories may become reusable records if HIT needs:

* category descriptions
* icons
* custom ordering
* category-level rules
* reporting

### Stock movements

Instead of storing only the current quantity, a later version may record events:

```text
stock_movements
```

Examples:

* purchased
* consumed
* corrected
* transferred
* discarded

This would allow quantity history and auditing.

### Timestamps

Likely later fields include:

```text
created_at
updated_at
```

These should use PostgreSQL timestamp types with a clear timezone strategy.

### Audit history

Sensitive household actions may eventually require:

* who changed a record
* when it changed
* previous and new values
* why the change occurred

### Search evolution

The current `ILIKE` search remains appropriate for the current dataset.

Later stages may explore:

* indexes on commonly filtered fields
* PostgreSQL full-text search
* trigram indexes
* ranked search
* aliases and synonyms
* semantic or AI-assisted retrieval

Search improvements should be based on measured requirements and query analysis.

### Database migrations

v0.6.0 introduced the first explicit sequential schema migrations:

```text
001_add_tracking_mode.sql
002_add_tracking_mode_quantity_rules.sql
```

The current approach uses transaction-wrapped SQL files and a frozen v0.5.0 schema fixture for upgrade testing.

Likely next migration capabilities include:

* an automated migration runner
* a schema-version or migration-history table
* explicit failure and recovery procedures
* controlled execution during local setup and deployment
* rollback planning where reversible changes are practical

A formal migration framework such as Alembic may become useful when the number of migrations, environments, dependencies, or rollback requirements make the explicit SQL approach cumbersome. It should not be introduced merely because FastAPI is present.

### Continuous integration

v0.5.0 introduced GitHub Actions with:

* dependency installation
* fast non-integration tests
* a PostgreSQL 18 service for integration tests
* isolated `hit_test` setup
* Docker image build validation
* automated feedback on pushes and pull requests

Future CI improvements may include:

* `python -m pip check`
* `python -m compileall src`
* linting after a standard is selected
* coverage reporting when it provides useful evidence
* protected-branch rules
* automated migration-runner verification

CI should continue to complement, not replace, local testing discipline.

### Azure deployment

A later production direction may use:

* Azure Database for PostgreSQL
* Azure Container Apps or App Service
* managed secrets
* database backups
* monitoring
* private networking
* production migration procedures

## Indexing Considerations

The primary key automatically provides an index on:

```text
id
```

Additional indexes are not yet required for the small development dataset.

Potential future candidates include:

```text
LOWER(name)
LOWER(category)
LOWER(location)
tracking_mode
quantity
minimum_quantity
```

A composite or partial index may eventually support quantity-only low-stock queries, but it should be justified by actual table size and query plans.

Before adding an index:

1. identify a real query pattern
2. inspect query performance with `EXPLAIN`
3. estimate table size and write cost
4. verify that the index is actually used

The future search-oriented direction of HIT will require careful indexing, but premature indexing would add complexity without measurable benefit.

## Guiding Principles

The HIT database should evolve according to these principles:

1. PostgreSQL remains the source of truth.
2. Python remains the central application language.
3. SQL values use parameter binding.
4. Dynamic SQL structure uses strict allowlists.
5. Database credentials remain outside source control.
6. PostgreSQL constraints protect core data integrity.
7. Tests use an isolated database.
8. Destructive tools include explicit safety guards.
9. Schema complexity follows real product requirements.
10. New abstractions must earn their place.
11. Security and privacy are foundational concerns.
12. Every iteration must leave the system understandable and testable.
13. Interfaces reuse repository operations instead of duplicating SQL.
14. Public API errors must not expose internal database details.
15. Database schema changes require sequential, testable migration planning.
16. Existing data must be preserved or deliberately transformed during upgrades.
17. Dockerized development should make local setup more reproducible without hiding database behavior.
18. CI should automate confidence checks without weakening local development discipline.
19. Domain distinctions must remain explicit across validation, service, repository, and database layers.
20. Individual assets should not be forced into quantity-based behavior.
21. Automated migration tooling should be introduced only when it solves demonstrated complexity.
22. Portfolio evidence should show both implementation and verification.

## v0.2.0 Database Milestone

HIT v0.2.0 established:

* PostgreSQL persistence
* a dedicated HIT schema
* identity-generated IDs
* database constraints
* a Psycopg connection layer
* repository-based CRUD
* case-insensitive search
* secure dynamic sorting
* low-stock database queries
* graceful connection failures
* isolated integration testing
* guarded JSON migration
* removal of the old JSON runtime

## v0.3.0 Database and API Integration Milestone

HIT v0.3.0 established:

* reuse of the existing PostgreSQL schema by FastAPI
* shared repository and database layers across two interfaces
* Pydantic validation before repository operations
* an API-facing application service layer
* partial-update merging outside the repository
* safe translation of missing items into `404`
* safe translation of database outages into `503`
* server-side logging of Psycopg operational failures
* isolated API tests that do not require PostgreSQL
* preservation of real PostgreSQL integration tests against `hit_test`

No schema migration was required for v0.3.0.

The database foundation now supports both console and HTTP interfaces.

## v0.4.0 Dockerized Local Development Milestone

HIT v0.4.0 established:

* Dockerized local development for the FastAPI application
* a Docker Compose `api` service
* a Docker Compose PostgreSQL `db` service
* PostgreSQL 18 for the Docker Compose database
* a named Docker volume for local PostgreSQL persistence
* service-to-service database networking through the hostname `db`
* local Docker configuration through `.env`
* safe example configuration through `.env.example`
* preservation of the existing `DATABASE_URL`-based database layer
* preservation of the existing repository and integration-test behavior
* a `/db-health` endpoint to verify API-to-database connectivity
* documentation for Docker Compose startup, shutdown, and smoke testing

No database schema migration was required for v0.4.0.

The database foundation now supports both manual local development and Dockerized local development. Future database work can focus on schema evolution, migrations, indexing, users, households, audit history, CI integration, and production deployment.

## v0.5.0 Continuous Integration Milestone

HIT v0.5.0 established:

* GitHub Actions on pushes and pull requests
* a Python 3.14 non-integration test job
* a PostgreSQL 18 service-based integration test job
* isolated `hit_test` creation in CI
* application of `sql/schema.sql` before integration tests
* preservation of the `_test` cleanup safeguard
* Docker image build validation on a clean Ubuntu runner
* read-only workflow permissions
* automated verification of Python, PostgreSQL, and Docker build behavior

No database schema migration was required for v0.5.0.

## v0.6.0 Inventory Domain Model Milestone

HIT v0.6.0 established:

* explicit `quantity` and `individual` tracking modes
* quantity tracking as the default for existing and legacy records
* nullable quantity fields for individually tracked assets
* PostgreSQL constraints matching quantity fields to tracking mode
* exclusion of individual assets from low-stock queries
* tracking-mode support across repository, service, and API layers
* atomic API transitions between tracking modes
* preservation of tracking mode during console updates
* sequential SQL migrations for upgrading the v0.5.0 schema
* a frozen v0.5.0 schema fixture
* migration tests that verify data preservation and backfilling
* database-constraint, repository, service, API, and full-stack tests
* a complete suite of 67 passing automated tests

The database foundation now supports two explicit inventory behaviors while retaining one understandable table and direct SQL architecture.

## v0.7.0 Reproducible Docker Startup Milestone

HIT v0.7.0 established:

* PostgreSQL container readiness checks through `pg_isready`
* API startup ordering based on PostgreSQL `service_healthy`
* API container health checks through the existing `/health` endpoint
* automatic first-run application of `sql/schema.sql` through `/docker-entrypoint-initdb.d/001-schema.sql`
* preservation of existing Docker volumes without destructive reinitialization
* persistence of inventory data across container recreation
* clear cold-start failure behavior when PostgreSQL cannot start
* explicit distinction between API liveness and API-to-database connectivity
* explicit understanding that Compose startup dependencies are not runtime supervision
* reproducible diagnosis of host environment-variable overrides
* preservation of the v0.6.0 PostgreSQL schema and domain behavior
* a complete automated suite of 67 passing tests plus manual Docker lifecycle verification

No database schema migration was required for v0.7.0.

Future database work can focus on API query capabilities, automated migration tooling, timestamps, users, households, audit history, indexing based on measured need, and Azure deployment.
