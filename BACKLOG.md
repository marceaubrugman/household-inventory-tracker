# Household Inventory Tracker Backlog

## Purpose

This backlog records the technical development of the Household Inventory Tracker, or HIT.

The project is developed incrementally. Each release should:

* introduce one meaningful architectural improvement
* remain understandable and testable
* preserve working behaviour
* produce visible portfolio evidence
* avoid introducing several major technologies at once

## Current Status

**Release target: v0.7.0**

HIT is a PostgreSQL-backed Python inventory application with two interfaces:

* a menu-driven console application
* a FastAPI REST API

The current implementation includes:

* complete inventory CRUD through both interfaces
* separate `quantity` and `individual` tracking modes
* database-backed search, sorting, and low-stock monitoring for quantity-tracked items
* individually tracked durable assets with `NULL` quantity fields
* validated FastAPI request and response models
* atomic API transitions between tracking modes
* secure parameterized SQL
* PostgreSQL constraints that enforce tracking-mode and quantity rules
* sequential PostgreSQL schema migrations
* a frozen v0.5.0 schema fixture for upgrade testing
* application, service, repository, and database layers
* controlled API error handling
* JSON migration tooling
* Dockerized local development for the FastAPI application and PostgreSQL
* PostgreSQL and API Docker health checks
* readiness-based API startup after PostgreSQL becomes healthy
* automatic first-run schema initialization for fresh Docker volumes
* `.env.example` for local Docker configuration
* GitHub Actions checks for Python tests, PostgreSQL integration tests, and Docker image builds
* unit, API, service, migration, repository, and full-stack PostgreSQL integration tests
* 67 passing automated tests

PostgreSQL remains the application’s source of truth.

The JSON runtime used in v0.1.0 has been removed. JSON remains supported only as a migration source, with imported records using quantity tracking.

Docker Compose starts the FastAPI API service and a PostgreSQL 18 database service together for reproducible local development.

The v0.7.0 feature work and Tock verification are complete on `feature/reproducible-docker-startup`. Release documentation and final Lock verification are in progress.

## Current Architecture

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
database.py
   ↓
db service
   ↓
PostgreSQL 18
```

FastAPI does not connect directly to PostgreSQL. API requests pass through Python application, service, repository, and database layers.

Inside Docker Compose, the API connects to PostgreSQL using the Compose service name `db`.

Tracking-mode rules are shared across API schemas, the service layer, repository operations, and PostgreSQL constraints. The database remains the final integrity boundary.

---

# Completed Milestones

## v0.1.0: JSON Console Application

### Inventory functionality

* [x] Add inventory items
* [x] View all items
* [x] Search items
* [x] Update items
* [x] Delete items
* [x] View low-stock items
* [x] Preserve stable item IDs
* [x] Save inventory to JSON
* [x] Load inventory from JSON

### Search and sorting

* [x] Search by name
* [x] Search by category
* [x] Search by location
* [x] Case-insensitive search
* [x] Partial matching
* [x] Sort by name
* [x] Sort by category
* [x] Sort by location
* [x] Sort quantity numerically

### Validation and usability

* [x] Reject empty required input
* [x] Reject invalid quantities
* [x] Allow zero quantity
* [x] Add cancellation flows
* [x] Preserve unchanged values during updates
* [x] Replace or clear notes
* [x] Normalize text input
* [x] Confirm deletions
* [x] Auto-save successful changes

### Structure and testing

* [x] Separate menu handling
* [x] Separate inventory logic
* [x] Separate validation
* [x] Separate display functions
* [x] Separate JSON storage
* [x] Add pytest coverage
* [x] Add project documentation
* [x] Publish Git tag `v0.1.0`
* [x] Publish GitHub Release `v0.1.0`

---

## v0.2.0: PostgreSQL Persistence

### Database foundation

* [x] Install and configure Psycopg 3
* [x] Create PostgreSQL development database
* [x] Create separate PostgreSQL test database
* [x] Create dedicated `hit` schema
* [x] Create `hit.items` table
* [x] Use an identity-generated primary key
* [x] Add required-field constraints
* [x] Add non-negative quantity constraints
* [x] Add default empty notes
* [x] Store the schema in `sql/schema.sql`

### Database connectivity

* [x] Read the database URL from `DATABASE_URL`
* [x] Keep credentials outside source code
* [x] Add a dedicated connection layer
* [x] Add a database connection diagnostic script
* [x] Add an explicit connection timeout
* [x] Handle missing configuration
* [x] Handle unavailable PostgreSQL connections gracefully

### Repository layer

* [x] Create `item_repository.py`
* [x] Return PostgreSQL rows as dictionaries
* [x] Create inventory items
* [x] Retrieve all inventory items
* [x] Retrieve one item by ID
* [x] Search inventory items
* [x] Update inventory items
* [x] Delete inventory items
* [x] Retrieve low-stock items
* [x] Return created, updated, and deleted records
* [x] Return `None` for missing IDs

### Secure SQL

* [x] Use parameterized SQL statements
* [x] Keep user values separate from SQL structure
* [x] Avoid SQL string interpolation
* [x] Escape literal search wildcard characters
* [x] Use an allowlist for sort options
* [x] Use Psycopg SQL composition for sort expressions
* [x] Reject unsupported sort keys
* [x] Preserve database constraints as the final integrity boundary

### Search and sorting

* [x] Search by name
* [x] Search by category
* [x] Search by location
* [x] Use case-insensitive `ILIKE`
* [x] Support partial matching
* [x] Treat user-supplied `%` and `_` literally
* [x] Sort text fields case-insensitively
* [x] Sort quantities numerically
* [x] Use item ID as a stable secondary sort
* [x] Evaluate low-stock status in PostgreSQL

### Application integration

* [x] Create `inventory_workflows.py`
* [x] Connect the console application to PostgreSQL
* [x] Remove the in-memory inventory list from `app.py`
* [x] Remove JSON loading from the active application
* [x] Remove JSON saving from the active application
* [x] Make PostgreSQL the source of truth
* [x] Preserve console functionality
* [x] Preserve validation and normalization
* [x] Replace “Save and exit” with normal exit
* [x] Add concise function docstrings

### Error handling

* [x] Add a dedicated database configuration exception
* [x] Catch expected Psycopg errors at the application boundary
* [x] Avoid exposing raw database errors to users
* [x] Return to the menu after recoverable failures
* [x] Recover after PostgreSQL is restarted
* [x] Prevent long connection hangs

### Integration testing

* [x] Register a pytest integration marker
* [x] Create isolated `hit_test` database
* [x] Redirect repository calls to the test database
* [x] Clean test data before and after each test
* [x] Reset generated IDs
* [x] Refuse destructive cleanup on non-test databases
* [x] Test complete CRUD lifecycle
* [x] Test multi-field search
* [x] Test case-insensitive search
* [x] Test numeric sorting
* [x] Test low-stock retrieval
* [x] Test PostgreSQL constraint enforcement
* [x] Support separate unit and integration test runs
* [x] Support a complete test-suite run

### JSON migration

* [x] Create JSON-to-PostgreSQL migration script
* [x] Support migration dry runs
* [x] Validate complete JSON documents
* [x] Require a top-level list
* [x] Reject missing required fields
* [x] Reject invalid and duplicate item IDs
* [x] Reject negative quantities
* [x] Preserve existing item IDs
* [x] Require an empty target table
* [x] Require explicit confirmation
* [x] Import all records in one transaction
* [x] Roll back failed migrations
* [x] Reset the PostgreSQL identity sequence
* [x] Test migration validation logic

### Legacy cleanup

* [x] Remove the JSON runtime storage module
* [x] Remove the obsolete in-memory inventory service
* [x] Remove tests for deleted runtime code
* [x] Retain `sample_inventory.json`
* [x] Retain JSON migration tooling
* [x] Remove temporary repository check scripts
* [x] Retain the database diagnostic script

### Documentation and release

* [x] Update README for PostgreSQL architecture
* [x] Update database plan
* [x] Update backlog
* [x] Review `.gitignore`
* [x] Check tracked files for credentials
* [x] Run unit tests
* [x] Run integration tests
* [x] Run complete test suite
* [x] Perform application smoke test
* [x] Perform stopped-database test
* [x] Perform migration dry run
* [x] Merge the feature branch into `main`
* [x] Create and push annotated Git tag `v0.2.0`
* [x] Publish GitHub Release `v0.2.0`

---

## v0.3.0: FastAPI Foundation

### FastAPI setup

* [x] Add FastAPI
* [x] Add Uvicorn
* [x] Add `httpx2` for endpoint testing
* [x] Create the FastAPI application structure
* [x] Add application title and version metadata
* [x] Add `GET /health`
* [x] Preserve the existing console application
* [x] Document local API startup
* [x] Add a PyCharm Uvicorn run configuration locally
* [x] Keep `.idea` excluded from Git

### API structure

* [x] Create `src/api/main.py`
* [x] Create API routers
* [x] Create API dependency functions
* [x] Create Pydantic schemas
* [x] Create global API exception handlers
* [x] Keep HTTP concerns out of repository code
* [x] Keep SQL isolated inside `item_repository.py`
* [x] Keep the console and API as separate interfaces

### Application service layer

* [x] Create `item_service.py`
* [x] Route API operations through the service layer
* [x] Keep FastAPI imports out of the service layer
* [x] Reuse existing repository operations
* [x] Merge partial updates with stored item data
* [x] Allowlist fields that may be updated
* [x] Return simple application outcomes to the API layer

### Pydantic models and validation

* [x] Create item-creation request model
* [x] Create item-update request model
* [x] Create item-response model
* [x] Keep request and response contracts separate
* [x] Trim surrounding whitespace
* [x] Reject blank required text
* [x] Reject negative quantities
* [x] Reject empty update bodies
* [x] Reject `null` for required update fields
* [x] Allow optional notes to be cleared
* [x] Filter internal fields from API responses
* [x] Validate item IDs as positive integers

### Read endpoints

* [x] Add `GET /health`
* [x] Add `GET /items`
* [x] Add `GET /items/{item_id}`
* [x] Return `404` for missing items
* [x] Return `422` for invalid item IDs
* [x] Return validated item responses

### Write endpoints

* [x] Add `POST /items`
* [x] Return `201 Created`
* [x] Add `PATCH /items/{item_id}`
* [x] Support partial updates
* [x] Preserve omitted fields
* [x] Add `DELETE /items/{item_id}`
* [x] Return `204 No Content`
* [x] Return an empty body after successful deletion
* [x] Return `404` for missing update and delete targets

### API error handling

* [x] Convert missing `DATABASE_URL` into a safe `503` response
* [x] Convert Psycopg operational failures into a safe `503` response
* [x] Keep database configuration details out of public responses
* [x] Log PostgreSQL operational failures on the server
* [x] Preserve `500` behavior for programming defects
* [x] Avoid broad `except Exception` handling
* [x] Keep `/health` independent from PostgreSQL

### Automated testing

* [x] Add automated health-endpoint test
* [x] Add list-endpoint tests
* [x] Add single-item endpoint tests
* [x] Add creation-endpoint tests
* [x] Add update-endpoint tests
* [x] Add deletion-endpoint tests
* [x] Add API error-handler tests
* [x] Add application-service unit tests
* [x] Use FastAPI dependency overrides
* [x] Use pytest monkeypatching
* [x] Test successful requests
* [x] Test invalid input
* [x] Test missing records
* [x] Test database configuration failures
* [x] Test database operational failures
* [x] Verify invalid requests do not reach the service
* [x] Preserve PostgreSQL integration tests against `hit_test`
* [x] Support PowerShell-compatible API test selection
* [x] Run the complete test suite after each slice

### Manual verification

* [x] Verify `/docs`
* [x] Verify `/openapi.json`
* [x] Verify real-database item listing
* [x] Verify real-database item retrieval
* [x] Verify item creation through the API
* [x] Verify partial update through the API
* [x] Verify deletion through the API
* [x] Verify missing-item responses
* [x] Verify invalid-path responses
* [x] Verify database-unavailable `503`
* [x] Verify console behavior remains intact

### Documentation and release preparation

* [x] Update README for v0.3.0
* [x] Document console and API architectures
* [x] Document API endpoints and status codes
* [x] Document local Uvicorn startup
* [x] Document API testing commands
* [x] Update backlog for v0.3.0
* [x] Review `DATABASE_PLAN.md`
* [x] Run `git diff --check`
* [x] Check tracked files for credentials and private data
* [x] Run the complete normal test suite
* [x] Run PostgreSQL integration tests with `TEST_DATABASE_URL`
* [x] Perform final API CRUD smoke test
* [x] Perform final console regression test
* [x] Commit release documentation
* [x] Push the FastAPI feature branch
* [x] Merge the feature branch into `main`
* [x] Run the complete test suite on `main`
* [x] Create and push annotated Git tag `v0.3.0`
* [x] Publish GitHub Release `v0.3.0`

---

## v0.4.0: Dockerized Local Development

### Docker foundation

* [x] Create a Docker feature branch
* [x] Add a `Dockerfile` for the FastAPI application
* [x] Select a Python base image
* [x] Install application dependencies inside the image
* [x] Add `.dockerignore`
* [x] Keep `.env` outside the image
* [x] Build the FastAPI application image
* [x] Run `GET /health` from the container
* [x] Preserve the existing FastAPI application behavior

### Docker Compose foundation

* [x] Add `docker-compose.yml`
* [x] Add an `api` service
* [x] Build the API image through Docker Compose
* [x] Expose the API development port
* [x] Start the API with `docker compose up --build`
* [x] Start the API in detached mode
* [x] Verify `GET /health`
* [x] Stop the API with `docker compose down`

### PostgreSQL Compose service

* [x] Add a PostgreSQL service named `db`
* [x] Use PostgreSQL 18
* [x] Configure local development database name, user, and password
* [x] Add a persistent named PostgreSQL volume
* [x] Use the PostgreSQL 18 Docker volume layout
* [x] Verify PostgreSQL starts inside Docker Compose
* [x] Verify direct `psql` access inside the database container
* [x] Verify current database and current user
* [x] Preserve existing local PostgreSQL and integration-test behaviour outside Docker Compose

### API-to-database connectivity

* [x] Add `DATABASE_URL` to the API service environment
* [x] Configure the API to use the Compose service name `db`
* [x] Preserve the existing `src.database` public interface
* [x] Preserve `DatabaseConfigurationError`
* [x] Preserve `get_connection`
* [x] Add a database connectivity helper
* [x] Add `GET /db-health`
* [x] Verify `GET /db-health` from the host machine
* [x] Verify the API container can connect to the PostgreSQL container
* [x] Keep `GET /health` independent from PostgreSQL

### Environment configuration

* [x] Add `.env.example`
* [x] Add local `.env` support
* [x] Keep `.env` ignored by Git
* [x] Use Compose variable interpolation
* [x] Move local Docker database settings out of `docker-compose.yml`
* [x] Verify resolved configuration with `docker compose config`
* [x] Keep real credentials and private configuration outside Git

### Testing and verification

* [x] Run existing pytest suite after Docker changes
* [x] Run Docker image build smoke test
* [x] Run Docker Compose startup smoke test
* [x] Verify `GET /health`
* [x] Verify `GET /db-health`
* [x] Verify direct PostgreSQL access through `docker compose exec db psql`
* [x] Verify clean shutdown with `docker compose down`
* [x] Verify `.env` is not tracked
* [x] Push Docker feature branch to GitHub for backup

### Documentation and release preparation

* [x] Update README for v0.4.0
* [x] Document Docker local development workflow
* [x] Document `.env.example` and local `.env` setup
* [x] Document Docker Compose startup commands
* [x] Document `/health` and `/db-health` smoke tests
* [x] Document direct PostgreSQL access through Docker Compose
* [x] Document `docker compose down`
* [x] Warn about `docker compose down -v`
* [x] Update backlog for v0.4.0
* [x] Review `DATABASE_PLAN.md` and update only if outdated
* [x] Confirm documented project structure matches the repository
* [x] Run `git diff --check`
* [x] Check tracked files for credentials and private data
* [x] Run `python -m pip check`
* [x] Run `python -m compileall src`
* [x] Run tests without `TEST_DATABASE_URL`
* [x] Run tests with the isolated `hit_test` database
* [x] Run final Docker Compose smoke test
* [x] Run final API smoke test
* [x] Run final console regression test
* [x] Commit release documentation
* [x] Push the Docker feature branch
* [x] Open and review the pull request
* [x] Merge the feature branch into `main`
* [x] Rerun all tests on `main`
* [x] Create and push annotated Git tag `v0.4.0`
* [x] Publish GitHub Release `v0.4.0`
* [x] Verify that credentials and private data are absent from GitHub

---

## v0.5.0: Continuous Integration

### Goal

Add automated checks so that project behavior is verified whenever code is pushed or a pull request is opened.

This milestone introduced continuous integration without expanding into production deployment or automated delivery.

### GitHub Actions foundation

* [x] Add a GitHub Actions workflow
* [x] Run the workflow on pull requests
* [x] Run the workflow on pushes
* [x] Install Python 3.14
* [x] Install project dependencies
* [x] Run non-integration Python tests
* [x] Report pass/fail status in GitHub
* [x] Keep the workflow small and understandable
* [x] Configure read-only repository permissions

### PostgreSQL integration job

* [x] Add a PostgreSQL 18 service
* [x] Create an isolated `hit_test` database
* [x] Apply `sql/schema.sql`
* [x] Run PostgreSQL integration tests
* [x] Preserve the `_test` database-name cleanup safeguard
* [x] Verify repository and database behavior in CI

### Docker build job

* [x] Add Docker image build validation
* [x] Build the FastAPI image on a clean Ubuntu runner
* [x] Verify that the Dockerfile and build context remain valid
* [x] Keep runtime deployment outside the v0.5.0 scope

### Verification and release

* [x] Verify that a deliberately failing test causes CI to fail
* [x] Restore the test suite after failure verification
* [x] Document all three CI jobs
* [x] Preserve console, API, PostgreSQL, and Docker Compose behavior
* [x] Run the complete local test suite
* [x] Merge the CI pull request into `main`
* [x] Create and push the annotated `v0.5.0` tag
* [x] Publish the GitHub Release

### Later CI improvements

* [ ] Add dependency checks to CI
* [ ] Run `python -m pip check` in CI
* [ ] Run `python -m compileall src` in CI
* [ ] Add linting after a project standard is chosen
* [ ] Configure protected-branch rules when appropriate
* [ ] Add coverage reporting when it provides useful evidence

---

# Completed Release Milestone

## v0.6.0: Inventory Domain Model

### Goal

Expand HIT beyond quantity-only inventory by introducing separate tracking modes for consumable supplies and individually tracked durable assets.

The release adds the first explicit schema-upgrade path while preserving existing v0.5.0 data and quantity-based API compatibility.

### Domain model

* [x] Define `quantity` and `individual` tracking modes
* [x] Keep quantity tracking as the default for existing and legacy records
* [x] Require non-negative `quantity` and `minimum_quantity` values for quantity-tracked items
* [x] Require `NULL` quantity fields for individually tracked assets
* [x] Exclude individual assets from low-stock results
* [x] Keep the model inside the existing single-table architecture

### PostgreSQL migrations and constraints

* [x] Add `sql/migrations/001_add_tracking_mode.sql`
* [x] Add `sql/migrations/002_add_tracking_mode_quantity_rules.sql`
* [x] Backfill existing inventory records to quantity tracking
* [x] Add the `tracking_mode` default
* [x] Add the allowed-values constraint
* [x] Add the `tracking_mode` `NOT NULL` rule
* [x] Relax the previous quantity-column `NOT NULL` rules
* [x] Add a combined constraint matching quantity fields to the selected tracking mode
* [x] Update `sql/schema.sql` to represent the final v0.6.0 schema
* [x] Add a frozen `tests/integration/fixtures/schema_v0_5_0.sql` fixture
* [x] Verify that the v0.5.0 schema upgrades without data loss

### Application layers

* [x] Expose `tracking_mode` through repository results
* [x] Expose `tracking_mode` through service outcomes
* [x] Expose `tracking_mode` through API request and response schemas
* [x] Add Pydantic validation for tracking-mode and quantity combinations
* [x] Support creation of quantity-tracked supplies
* [x] Support creation of individually tracked assets
* [x] Support atomic API transitions between tracking modes
* [x] Preserve tracking mode during console updates
* [x] Preserve legacy JSON import behavior through quantity tracking
* [x] Keep SQL isolated inside the repository layer

### Testing

* [x] Add migration upgrade tests
* [x] Add PostgreSQL tracking-mode constraint tests
* [x] Add repository tests for both tracking modes
* [x] Add service-layer tracking-mode tests
* [x] Add API creation and update tests
* [x] Add full-stack individual-item API tests
* [x] Verify low-stock exclusion for individual assets
* [x] Run the complete suite with 67 passing tests
* [x] Merge feature pull request #7 into `main`

### Documentation

* [x] Update the current release number in `README.md`
* [x] Add the v0.6.0 milestone and version-history entries
* [x] Document quantity and individual item structures
* [x] Document valid API creation payloads
* [x] Document atomic tracking-mode transitions
* [x] Update the documented PostgreSQL schema
* [x] Document sequential migration behavior
* [x] Update the documented project structure
* [x] Update `BACKLOG.md` for v0.6.0

### Release lock

* [x] Freeze the v0.6.0 feature set
* [x] Merge the completed feature work into `main`
* [x] Create `release/v0.6.0`
* [x] Review `DATABASE_PLAN.md`
* [x] Confirm all current documentation matches the repository
* [x] Run `git diff --check`
* [x] Inspect `git status`
* [x] Run `python -m pip check`
* [x] Run `python -m compileall src`
* [x] Run tests without `TEST_DATABASE_URL`
* [x] Run the complete suite against the isolated `hit_test` database
* [x] Run the final Docker image build
* [x] Run the final Docker Compose smoke test
* [x] Run the final API smoke test
* [x] Run the final console regression test
* [x] Verify that credentials and private inventory data are absent from tracked files
* [x] Commit the release documentation
* [x] Push `release/v0.6.0`
* [x] Open and review the release pull request
* [x] Confirm all GitHub Actions jobs pass
* [x] Merge the release pull request into `main`
* [x] Synchronize local `main`
* [x] Rerun the complete test suite on `main`
* [x] Create and push the annotated `v0.6.0` tag
* [x] Publish the GitHub Release

The v0.6.0 release lock is complete.

---

# Current Release Milestone

## v0.7.0: Reproducible Docker Startup

### Goal

Make HIT start reliably in a clean Docker environment without requiring manual database setup.

A developer should be able to clone the repository, configure `.env`, run Docker Compose, and receive a working API backed by an initialized PostgreSQL database.

### Docker readiness and startup

* [x] Add a PostgreSQL health check using `pg_isready`
* [x] Start the API only after PostgreSQL is healthy
* [x] Add an API health check using the existing `/health` endpoint
* [x] Keep PostgreSQL internal to the Compose network
* [x] Verify `docker compose config`

### Fresh database initialization

* [x] Mount `sql/schema.sql` read-only into `/docker-entrypoint-initdb.d/001-schema.sql`
* [x] Initialize the HIT schema automatically for a fresh Docker volume
* [x] Verify `hit.items` exists after first-run startup
* [x] Verify PostgreSQL executes the initialization script on a fresh volume
* [x] Verify existing volumes skip initialization
* [x] Verify persisted data survives container recreation

### Failure and recovery verification

* [x] Verify a broken PostgreSQL health probe becomes unhealthy
* [x] Verify an unhealthy PostgreSQL dependency blocks API cold start
* [x] Verify a broken API health endpoint becomes unhealthy
* [x] Verify both health checks recover after configuration is restored
* [x] Reproduce and diagnose a shell-level `DATABASE_URL` override
* [x] Verify corrected environment configuration requires API container recreation
* [x] Verify clear failure behavior when PostgreSQL itself cannot start
* [x] Verify `depends_on: service_healthy` controls startup ordering rather than runtime supervision

### Automated and release verification

* [x] Run tests without `TEST_DATABASE_URL` and confirm integration-test skips are intentional
* [x] Run the complete suite against an isolated PostgreSQL `hit_test` database
* [x] Confirm 67 passing automated tests
* [x] Perform a final fresh-volume Docker lifecycle verification
* [x] Verify `/health`
* [x] Verify `/db-health`
* [x] Verify automatic schema initialization
* [x] Update README, backlog, database plan, and Living Learning Library
* [x] Review application/configuration version references
* [x] Run `git diff --check`
* [x] Run `python -m pip check`
* [x] Run `python -m compileall src`
* [x] Run final console regression test
* [x] Verify tracked files contain no credentials or private inventory data
* [ ] Prepare and review the v0.7.0 release pull request
* [ ] Confirm GitHub Actions passes
* [ ] Merge release work into `main`
* [ ] Rerun release verification on exact `main`
* [ ] Create and push the annotated `v0.7.0` tag
* [ ] Publish the GitHub Release
* [ ] Create the v0.7.0 → v0.8.0 canonical handover

### Scope guardrails preserved

* [x] No Alembic
* [x] No SQLAlchemy
* [x] No authentication
* [x] No frontend work
* [x] No Azure deployment
* [x] No unrelated API feature expansion
* [x] PostgreSQL schema and v0.6.0 domain behavior preserved

---

# Later Technical Milestones

## Docker improvements

Completed in v0.7.0:

* [x] Add PostgreSQL health check
* [x] Add application health check
* [x] Start the API only after PostgreSQL is healthy
* [x] Apply `sql/schema.sql` automatically in a clean Docker environment
* [x] Use PostgreSQL's first-run `/docker-entrypoint-initdb.d/` mechanism for schema initialization
* [x] Verify first-run database creation
* [x] Verify repeat startup without data loss
* [x] Verify persistent data after container restart
* [x] Verify failed database startup behavior

Later:

* [ ] Consider a non-root application user in the Docker image
* [ ] Document image build commands separately if needed
* [ ] Add controlled migration execution only when the migration workflow requires it

## API query capabilities

* [ ] Add search query parameters
* [ ] Add a low-stock endpoint or query parameter
* [ ] Add approved sorting options
* [ ] Add pagination
* [ ] Add focused tests for query combinations
* [ ] Document query behavior

## Database migration tooling

The first explicit SQL migrations were introduced in v0.6.0. More tooling should be added only when migration complexity justifies it.

* [x] Introduce sequential schema migrations when required
* [x] Add a migration that introduces `tracking_mode`
* [x] Add a migration that introduces tracking-mode quantity rules
* [x] Test a schema upgrade from a frozen earlier release
* [x] Preserve existing records during the upgrade
* [x] Document the migration behavior
* [ ] Add an automated migration runner
* [ ] Add a schema-version or migration-history table
* [ ] Define upgrade failure and rollback procedures
* [ ] Evaluate Alembic when the project’s migration needs warrant another dependency
* [ ] Add automated migration execution to deployment only after the process is understood

## Frontend foundation

* [ ] Select a small initial frontend approach
* [ ] Display inventory items in a browser
* [ ] Add create, update, and delete forms
* [ ] Connect the frontend only through the API
* [ ] Add clear validation and error feedback
* [ ] Preserve API and frontend separation

## Authentication foundation

* [ ] Define authentication requirements
* [ ] Add secure password handling
* [ ] Add token-based authentication
* [ ] Protect selected API endpoints
* [ ] Add authentication tests
* [ ] Add authorization tests

## Users and households

* [ ] Add a user model
* [ ] Add a household model
* [ ] Associate inventory items with a household
* [ ] Define household roles and permissions
* [ ] Prevent cross-household data access
* [ ] Add migration and isolation tests

## Audit and stock history

* [ ] Define stock-movement events
* [ ] Record item creation, updates, and deletion
* [ ] Preserve quantity-change history
* [ ] Add audit queries
* [ ] Add tests for history integrity

## Azure deployment

* [ ] Complete Azure Fundamentals preparation
* [ ] Select the initial Azure hosting service
* [ ] Deploy the PostgreSQL-backed API
* [ ] Configure managed secrets
* [ ] Configure environment variables
* [ ] Add production health checks
* [ ] Configure logging and monitoring
* [ ] Document deployment
* [ ] Review backup and recovery options

## AI-assisted capabilities

* [ ] Define a useful, bounded AI-assisted feature
* [ ] Keep deterministic inventory operations independent from AI
* [ ] Add privacy and consent considerations
* [ ] Add evaluation criteria before implementation
* [ ] Avoid adding AI solely for portfolio decoration

---

# Development Principles

1. Python remains the central application language.
2. PostgreSQL remains the source of truth.
3. Direct SQL knowledge remains important.
4. User values use parameterized statements.
5. Dynamic SQL structure uses strict allowlists.
6. Credentials and private data stay outside Git.
7. Database constraints protect core integrity.
8. Integration tests use an isolated database.
9. Destructive tools contain explicit safeguards.
10. Every version remains runnable and documented.
11. New technology must solve a current engineering problem.
12. Portfolio evidence takes priority over endless course consumption.
13. Security is designed into every layer.
14. Complexity grows one tested step at a time.
15. Interfaces should share application rules rather than duplicate them.
16. Public API errors must not expose internal infrastructure details.
17. Feature breadth should not outrun architectural understanding.
18. Local development should be reproducible without hidden manual setup where practical.
19. CI/CD should be added incrementally and only after the local workflow is stable.
20. Docker is used to make development repeatable, not to hide architectural confusion.
21. Domain distinctions should remain explicit across validation, application, repository, and database layers.
22. Schema changes should be sequential, testable, and preserve existing data.
23. Individually tracked assets should not be forced into quantity-based behavior.
24. Release documentation must describe the current system rather than only its history.

---

# Immediate Next Action

Complete the v0.7.0 Lock and release sequence.

After v0.7.0 is released, select the v0.8.0 objective from the remaining roadmap based on the next strongest backend/data learning need. Do not broaden v0.7.0 during Lock.
