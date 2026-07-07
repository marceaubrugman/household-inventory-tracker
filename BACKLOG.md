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

**Current release candidate: v0.4.0**

HIT is a PostgreSQL-backed Python inventory application with two interfaces:

* a menu-driven console application
* a FastAPI REST API

The current implementation includes:

* complete inventory CRUD through both interfaces
* database-backed search, sorting, and low-stock monitoring in the console
* validated FastAPI request and response models
* secure parameterized SQL
* PostgreSQL constraints
* application, service, repository, and database layers
* controlled API error handling
* JSON migration tooling
* Dockerized local development for the FastAPI application and PostgreSQL
* `.env.example` for local Docker configuration
* unit, API, service, migration, and PostgreSQL integration tests

PostgreSQL remains the application’s source of truth.

The JSON runtime used in v0.1.0 has been removed. JSON remains supported only as a migration source.

Docker Compose is now available for local development. It starts the FastAPI API service and a PostgreSQL 18 database service together.

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
* [ ] Review `DATABASE_PLAN.md` and update only if outdated
* [ ] Confirm documented project structure matches the repository
* [ ] Run `git diff --check`
* [ ] Check tracked files for credentials and private data
* [ ] Run `python -m pip check`
* [ ] Run `python -m compileall src`
* [ ] Run tests without `TEST_DATABASE_URL`
* [ ] Run tests with the isolated `hit_test` database
* [ ] Run final Docker Compose smoke test
* [ ] Run final API smoke test
* [ ] Run final console regression test
* [ ] Commit release documentation
* [ ] Push the Docker feature branch
* [ ] Open and review the pull request
* [ ] Merge the feature branch into `main`
* [ ] Rerun all tests on `main`
* [ ] Create and push annotated Git tag `v0.4.0`
* [ ] Publish GitHub Release `v0.4.0`
* [ ] Verify that credentials and private data are absent from GitHub

---

# Current Priority

## Complete and publish v0.4.0

Before beginning new feature development:

* [x] freeze the v0.4.0 feature set
* [x] add Dockerfile
* [x] add `.dockerignore`
* [x] add Docker Compose for the API service
* [x] add PostgreSQL service to Docker Compose
* [x] connect FastAPI to Compose PostgreSQL
* [x] move Docker configuration into `.env` and `.env.example`
* [x] verify `GET /health`
* [x] verify `GET /db-health`
* [x] update `README.md`
* [x] update `BACKLOG.md`
* [ ] review `DATABASE_PLAN.md`
* [ ] confirm documented project structure matches the repository
* [ ] run `git diff --check`
* [ ] inspect `git status`
* [ ] run `python -m pip check`
* [ ] run `python -m compileall src`
* [ ] run tests without `TEST_DATABASE_URL`
* [ ] run tests with the isolated `hit_test` database
* [ ] run the final Docker Compose smoke test
* [ ] run the final API smoke test
* [ ] run the final console regression test
* [ ] commit release documentation
* [ ] push the feature branch
* [ ] open and review the pull request
* [ ] merge into `main`
* [ ] rerun all tests on `main`
* [ ] create and push `v0.4.0`
* [ ] publish the GitHub Release
* [ ] verify that credentials and private data are absent from GitHub

No new feature development should begin until the release is complete.

---

# Next Major Milestone

## v0.5.0: Continuous Integration

### Goal

Add automated checks so that tests can run through GitHub Actions when code is pushed or a pull request is opened.

This milestone introduces CI/CD concepts gradually, starting with continuous integration only.

### GitHub Actions foundation

* [ ] Add a GitHub Actions workflow
* [ ] Run the workflow on pull requests
* [ ] Run the workflow on pushes to `main`
* [ ] Install Python
* [ ] Install project dependencies
* [ ] Run unit and service tests
* [ ] Run API tests
* [ ] Report pass/fail status in GitHub
* [ ] Keep the workflow small and understandable

### Later CI improvements

* [ ] Add dependency checks
* [ ] Run `python -m pip check`
* [ ] Run `python -m compileall src`
* [ ] Add linting when a linting standard is chosen
* [ ] Add a PostgreSQL test service
* [ ] Run integration tests in CI
* [ ] Build the Docker image in CI
* [ ] Block merging when checks fail

---

# Later Technical Milestones

## Docker improvements

* [ ] Add PostgreSQL health check
* [ ] Add application health check
* [ ] Start the API only after PostgreSQL is healthy
* [ ] Apply `sql/schema.sql` automatically in a clean Docker environment
* [ ] Decide how schema initialization is triggered
* [ ] Verify first-run database creation
* [ ] Verify repeat startup without data loss
* [ ] Verify persistent data after container restart
* [ ] Verify failed database startup behavior
* [ ] Consider a non-root application user in the Docker image
* [ ] Document image build commands separately if needed

## API query capabilities

* [ ] Add search query parameters
* [ ] Add low-stock endpoint or query parameter
* [ ] Add approved sorting options
* [ ] Add pagination
* [ ] Add focused tests for query combinations
* [ ] Document query behavior

## Database migrations

* [ ] Introduce formal schema migrations when required
* [ ] Evaluate Alembic
* [ ] Create a baseline migration
* [ ] Test schema upgrades
* [ ] Document migration commands

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

* [ ] Add user model
* [ ] Add household model
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

* [ ] Complete Azure fundamentals preparation
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

---

# Immediate Next Action

Complete the v0.4.0 release checklist:

1. review `DATABASE_PLAN.md`
2. check whether `menu.py` or `src/api/main.py` still expose `v0.3.0`
3. run final documentation, dependency, and test checks
4. perform the Docker Compose, API, and console smoke tests
5. commit and push the release documentation
6. open and review the pull request
7. merge the Docker feature branch into `main`
8. tag and publish `v0.4.0`
