# Household Inventory Tracker v0.1

A modular Python console application for tracking household items, storage locations, stock levels, and restock needs.

## Overview

Household Inventory Tracker is part of my transition into Python Data / Backend Engineering.

The original v0 milestone focused on building a clean and readable console application with:

- modular Python code
- CRUD-style inventory management
- input validation
- JSON-based persistence
- basic automated testing

Version 0.1 improves the usability, reliability, and test coverage of that original MVP.

## What's new in v0.1

- Automatic saving after adding, updating, or deleting an item
- Expanded search across item name, category, and location
- Sortable inventory listing by name, category, location, or quantity
- Graceful cancellation when updating or deleting an item
- Consistent text normalization for item names, categories, and locations
- Improved notes editing with keep, replace, and clear options
- Expanded pytest coverage for search, sorting, normalization, and JSON persistence

## Features

### Add items

Each inventory item contains:

- Unique ID
- Name
- Category
- Storage location
- Current quantity
- Minimum quantity
- Optional notes

Names, categories, and locations are normalized when entered to improve consistency.

### List items

Display all stored items in a readable format.

Items can be sorted by:

- Name
- Category
- Location
- Quantity

Sorting changes only the display order. Item IDs remain stable.

### Search

Search across:

- Item name
- Category
- Location

Search behavior is:

- Case-insensitive
- Based on partial matches

### Update items

Update an existing item by ID.

During an update:

- Press Enter to keep the current value
- Enter a new value to replace the current value
- Enter `-` to clear the notes field
- Enter `q` at the ID prompt to cancel

### Delete items

Delete an item by ID with confirmation.

The deletion flow can also be cancelled by entering `q` at the ID prompt.

### Low-stock view

Show items where:

```text
quantity <= minimum quantity
```

This helps identify items that have reached or fallen below their desired stock threshold.

### JSON persistence

- Inventory data is loaded when the application starts
- Changes are saved automatically after add, update, and delete actions
- Inventory is also saved when the application exits normally
- Runtime data is stored in `inventory.json`

The runtime `inventory.json` file is excluded from Git because it contains local user data.

## Project structure

```text
household-inventory-tracker/
├── app.py
├── README.md
├── BACKLOG.md
├── DATABASE_PLAN.md
├── requirements.txt
├── sample_inventory.json
├── src/
│   ├── __init__.py
│   ├── menu.py
│   ├── inventory_service.py
│   ├── storage.py
│   ├── validators.py
│   └── display.py
└── tests/
    ├── __init__.py
    ├── test_inventory_service.py
    ├── test_storage.py
    └── test_validators.py
```

## Module responsibilities

- `app.py` manages the main application flow
- `menu.py` displays the menu and receives menu choices
- `inventory_service.py` contains inventory operations and business rules
- `storage.py` loads and saves JSON data
- `validators.py` validates, normalizes, and interprets user input
- `display.py` formats inventory output
- `BACKLOG.md` records possible future improvements
- `DATABASE_PLAN.md` describes the planned evolution toward PostgreSQL

## Technologies used

- Python
- JSON
- pytest
- Git and GitHub
- PyCharm

The application itself uses only the Python standard library. `pytest` is the only current external dependency and is used for automated testing.

## How to run the application

### 1. Clone the repository

```bash
git clone https://github.com/marceaubrugman/household-inventory-tracker.git
cd household-inventory-tracker
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

#### macOS or Linux

```bash
source .venv/bin/activate
```

### 4. Install the test dependency

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

## Sample data

The repository includes:

```text
sample_inventory.json
```

This file contains example inventory data for demonstration purposes.

The application itself reads and writes:

```text
inventory.json
```

To start with the included sample data, copy or rename `sample_inventory.json` to `inventory.json` before running the application.

Keep the original sample file if you want to preserve a reusable example dataset.

## Tests

The project uses `pytest` for automated testing.

Current tests cover:

- ID generation
- Item search by name, category, and location
- Case-insensitive search behavior
- Item lookup by ID
- Low-stock filtering
- Numeric quantity sorting
- Text normalization
- JSON save/load persistence

### Run the complete test suite

From the project root, run:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

The storage tests use pytest's temporary-file support, so they do not modify the application's real `inventory.json` file.

## Design principles practiced

This project was built to practice:

- Modular Python structure
- Separation of concerns
- Validation and data normalization
- CRUD operations
- Filtering and sorting
- JSON serialization and deserialization
- Defensive programming
- Automated testing
- Git-based development
- Incremental feature development

## Current limitations

Version 0.1 is intentionally small and focused.

Current limitations include:

- Console interface only
- Single local inventory
- JSON file storage
- No user accounts
- No advanced filtering
- No database connection
- No web or API interface

## Future development

Possible future improvements include:

- Grouping items by category or location
- Reusable defaults for common categories and storage locations
- Advanced filtering
- CSV import and export
- Timestamps for item creation and updates
- Stock-change history
- PostgreSQL persistence
- FastAPI endpoints
- Docker containerization
- Azure deployment

The planned PostgreSQL evolution is documented in `DATABASE_PLAN.md`.

## Project status

**Household Inventory Tracker v0.1 is complete.**

This version serves as the stable JSON-based console foundation for future database-backed and API-based iterations.

## Author

**Marceau Brugman**

- GitHub: [github.com/marceaubrugman](https://github.com/marceaubrugman)
- Portfolio repository: [Household Inventory Tracker](https://github.com/marceaubrugman/household-inventory-tracker)
