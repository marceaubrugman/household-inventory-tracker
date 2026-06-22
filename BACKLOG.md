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

**Current release candidate: v0.2.0**

HIT is a PostgreSQL-backed Python console application with:

* complete inventory CRUD
* database-backed search and sorting
* low-stock monitoring
* secure parameterized SQL
* PostgreSQL constraints
* graceful database connection handling
* JSON migration tooling
* unit and PostgreSQL integration tests

## Current Architecture

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

PostgreSQL is the application’s source of truth.

The JSON runtime used in v0.1.0 has been removed. JSON remains supported only as a migration source.

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

### Documentation

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

### Release operations

* [ ] Commit release documentation and cleanup
* [ ] Push PostgreSQL feature branch
* [ ] Merge feature branch into `main`
* [ ] Run complete test suite on `main`
* [ ] Run application from `main`
* [ ] Create annotated Git tag `v0.2.0`
* [ ] Push `main` and `v0.2.0`
* [ ] Verify GitHub repository and tag
* [ ] Publish a short LinkedIn milestone post

---

# Current Priority

## Complete the v0.2.0 release

Before beginning new feature development:

* [ ] confirm the documented project structure matches the repository
* [ ] confirm `README.md` matches the implementation
* [ ] confirm `DATABASE_PLAN.md` matches the implementation
* [ ] confirm this backlog matches completed work
* [ ] run `git diff --check`
* [ ] inspect `git status`
* [ ] commit the release preparation
* [ ] push the feature branch
* [ ] merge into `main`
* [ ] rerun all tests on `main`
* [ ] run the application on `main`
* [ ] create and push `v0.2.0`
* [ ] verify that credentials and private data are absent from GitHub

No new feature development should begin until the release is complete.

---

# Next Major Milestone

## v0.3.0: FastAPI Foundation

### Goal

Expose the PostgreSQL-backed inventory system through a web API while reusing the existing database and repository layers.

### FastAPI setup

* [ ] Add FastAPI
* [ ] Add an ASGI server such as Uvicorn
* [ ] Create the FastAPI application
* [ ] Add application metadata
* [ ] Add a health-check endpoint
* [ ] Document local API startup

### API models

* [ ] Create Pydantic item-creation model
* [ ] Create Pydantic item-update model
* [ ] Create Pydantic response model
* [ ] Define field constraints
* [ ] Keep API contracts separate from database records

### Read endpoints

* [ ] Add `GET /health`
* [ ] Add `GET /items`
* [ ] Add `GET /items/{item_id}`
* [ ] Add inventory search endpoint
* [ ] Add low-stock endpoint
* [ ] Support approved sorting options
* [ ] Return `404` for missing items

### Write endpoints

* [ ] Add `POST /items`
* [ ] Add item-update endpoint
* [ ] Add `DELETE /items/{item_id}`
* [ ] Return appropriate HTTP status codes
* [ ] Return structured validation errors

### API tests

* [ ] Add API unit tests
* [ ] Add API integration tests
* [ ] Test successful requests
* [ ] Test invalid input
* [ ] Test missing records
* [ ] Test database failures
* [ ] Continue using an isolated test database

### Documentation and release

* [ ] Add API instructions to README
* [ ] Document endpoints
* [ ] Add example requests and responses
* [ ] Update architecture documentation
* [ ] Run complete test suite
* [ ] Publish Git tag `v0.3.0`

---

# Later Technical Milestones

## Docker Compose

* [ ] Add Dockerfile for the Python application
* [ ] Add Docker Compose configuration
* [ ] Run application and PostgreSQL together
* [ ] Add PostgreSQL health check
* [ ] Add application health check
* [ ] Add persistent database volume
* [ ] Document environment variables
* [ ] Verify clean local startup

## Database migrations

* [ ] Introduce formal schema migrations when required
* [ ] Evaluate Alembic
* [ ] Create baseline migration
* [ ] Test schema upgrades
* [ ] Document migration commands

## Continuous integration

* [ ] Add GitHub Actions workflow
* [ ] Install dependencies
* [ ] Run unit tests
* [ ] Start PostgreSQL test service
* [ ] Run integration tests
* [ ] Run API tests
* [ ] Block merging when checks fail

## Authentication foundation

* [ ] Define authentication requirements
* [ ] Add secure password handling
* [ ] Add token-based authentication
* [ ] Protect selected API endpoints
* [ ] Add authentication tests
* [ ] Add authorization tests

## Azure deployment

* [ ] Complete Azure fundamentals preparation
* [ ] Select initial Azure hosting service
* [ ] Deploy the PostgreSQL-backed API
* [ ] Configure managed secrets
* [ ] Configure environment variables
* [ ] Add production health checks
* [ ] Configure logging and monitoring
* [ ] Document deployment
* [ ] Review backup and recovery options

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

---

# Immediate Next Action

Complete and publish `v0.2.0`.

After release:

1. design the smallest viable FastAPI foundation
2. implement the health endpoint first
3. reuse the tested PostgreSQL repository