# Household Inventory Tracker Backlog

This backlog records completed milestones, planned improvements, and the longer-term evolution of Household Inventory Tracker.

The project will be developed incrementally, with Python remaining the central pillar.

---

## Completed: v0

- [x] Create modular Python console application
- [x] Add inventory items
- [x] List all inventory items
- [x] Search items by name
- [x] Update items by ID
- [x] Delete items by ID with confirmation
- [x] Show low-stock items
- [x] Validate required text fields
- [x] Validate non-negative numeric fields
- [x] Save inventory data to JSON
- [x] Load inventory data from JSON
- [x] Add sample inventory data
- [x] Add basic pytest coverage
- [x] Publish project to GitHub
- [x] Create initial README documentation
- [x] Create PostgreSQL evolution plan

---

## Completed: v0.1

### Reliability

- [x] Save automatically after adding an item
- [x] Save automatically after updating an item
- [x] Save automatically after deleting an item
- [x] Keep save-on-exit behavior

### Search and sorting

- [x] Expand search to item name, category, and location
- [x] Keep search case-insensitive
- [x] Support partial search matches
- [x] Sort inventory by name
- [x] Sort inventory by category
- [x] Sort inventory by location
- [x] Sort inventory by quantity
- [x] Keep item IDs stable regardless of display order

### User experience

- [x] Update application title to v0.1
- [x] Allow update flow to be cancelled with `q`
- [x] Allow delete flow to be cancelled with `q`
- [x] Normalize item names
- [x] Normalize categories
- [x] Normalize storage locations
- [x] Allow notes to be kept during an update
- [x] Allow notes to be replaced during an update
- [x] Allow notes to be cleared during an update

### Tests and documentation

- [x] Test expanded search behavior
- [x] Test category search
- [x] Test location search
- [x] Test numeric quantity sorting
- [x] Test text normalization
- [x] Test JSON save/load persistence
- [x] Update README for v0.1
- [x] Document completed v0.1 work

---

## Next candidates: v0.2

These improvements may be added before the PostgreSQL migration, but only when they support learning or usability without delaying the backend roadmap.

### Inventory views

- [ ] Group items by category
- [ ] Group items by storage location
- [ ] Add ascending and descending sort options
- [ ] Combine search results with sorting
- [ ] Add filtering by category
- [ ] Add filtering by location
- [ ] Add a dedicated out-of-stock view

### Data entry improvements

- [ ] Add reusable category suggestions
- [ ] Add reusable location suggestions
- [ ] Add category-to-location defaults
- [ ] Remember commonly used values
- [ ] Prevent accidental duplicate items
- [ ] Suggest updating quantity when a duplicate item is entered

### Data handling

- [ ] Export inventory to CSV
- [ ] Import inventory from CSV
- [ ] Create automatic JSON backups
- [ ] Add a command to restore from backup
- [ ] Add created and updated timestamps
- [ ] Add stock-change history

### Console experience

- [ ] Improve table-style console output
- [ ] Add clearer success and error messages
- [ ] Add confirmation before exiting with unsaved changes, if needed
- [ ] Add a return-to-menu option within longer workflows
- [ ] Review accessibility and prompt clarity

---

## PostgreSQL-backed version

The planned database evolution is described in `DATABASE_PLAN.md`.

### Database foundation

- [ ] Create PostgreSQL development database
- [ ] Create the initial `items` table
- [ ] Add primary key and data constraints
- [ ] Connect Python to PostgreSQL
- [ ] Move database configuration outside application code
- [ ] Add safe handling for database connection errors

### Replace JSON operations

- [ ] Insert items with SQL
- [ ] Retrieve and list items with SQL
- [ ] Search items with SQL
- [ ] Update items with SQL
- [ ] Delete items with SQL
- [ ] Retrieve low-stock items with SQL
- [ ] Add SQL sorting and filtering
- [ ] Let PostgreSQL generate item IDs

### Data migration

- [ ] Design a JSON-to-PostgreSQL migration script
- [ ] Import existing JSON inventory
- [ ] Validate migrated records
- [ ] Preserve stable item data during migration
- [ ] Keep the JSON version available as the v0.1 milestone

### Database testing

- [ ] Add tests for database access functions
- [ ] Add integration tests for PostgreSQL CRUD operations
- [ ] Use a separate test database
- [ ] Test database constraints
- [ ] Test transaction and rollback behavior

---

## FastAPI backend version

- [ ] Create FastAPI project structure
- [ ] Add Pydantic request and response models
- [ ] Add endpoint to create an item
- [ ] Add endpoint to retrieve all items
- [ ] Add endpoint to retrieve one item by ID
- [ ] Add endpoint to search items
- [ ] Add endpoint to update an item
- [ ] Add endpoint to delete an item
- [ ] Add endpoint for low-stock items
- [ ] Connect FastAPI to PostgreSQL
- [ ] Add API error handling
- [ ] Add API tests
- [ ] Generate and review OpenAPI documentation

---

## Docker and deployment

- [ ] Create Dockerfile for the backend
- [ ] Add PostgreSQL with Docker Compose
- [ ] Configure environment variables
- [ ] Add persistent database volumes
- [ ] Test the application in containers
- [ ] Add health-check endpoint
- [ ] Prepare Azure deployment
- [ ] Deploy a working backend version
- [ ] Add logging and basic monitoring

---

## Longer-term product ideas

These ideas belong to later product exploration and should not distract from the current backend/data learning path.

- [ ] Multiple households
- [ ] User accounts and authentication
- [ ] Shared household inventory
- [ ] Barcode support
- [ ] Expiry-date tracking
- [ ] Shopping-list generation
- [ ] Restock recommendations
- [ ] Inventory usage patterns
- [ ] Advanced household search
- [ ] Natural-language inventory queries
- [ ] AI-assisted categorization
- [ ] Image-based item recognition
- [ ] Web or mobile interface

---

## Current priority

The current priority is to preserve HIT v0.1 as a stable, tested JSON-based console application while preparing the next backend-focused evolution:

1. continue PostgreSQL learning
2. refine the database design
3. connect Python to PostgreSQL
4. replace JSON persistence incrementally
5. prepare the project for FastAPI, Docker, and Azure

The project should evolve one tested layer at a time rather than accumulating features without architectural purpose.
