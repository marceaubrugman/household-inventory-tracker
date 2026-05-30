# Household Inventory Tracker Database Plan

## Goal

Evolve Household Inventory Tracker from a Python console app with JSON persistence into a database-backed project using PostgreSQL.

The purpose of this plan is to bridge the current v0 application and a future backend/data-oriented version that uses relational storage instead of a local JSON file.

---

## Current application state

The current version of Household Inventory Tracker is a modular Python console app with:

- add item
- list items
- search by name
- update item by ID
- delete item by ID
- low-stock view
- JSON save/load persistence
- basic pytest tests

This version is considered the working v0 baseline.

---

## Current data model

The current application stores inventory items as JSON objects with the following structure:

```python
{
    "id": 1,
    "name": "Rice",
    "category": "Food",
    "location": "Pantry",
    "quantity": 2,
    "minimum_quantity": 3,
    "notes": ""
}
```

## First PostgreSQL table design

```sql

    CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    minimum_quantity INTEGER NOT NULL CHECK (minimum_quantity >= 0),
    notes TEXT
);
```