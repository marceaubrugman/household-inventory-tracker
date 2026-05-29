# Household Inventory Tracker v0

A Python console application for tracking household items, their storage locations, stock levels, and restock needs.

## Overview

This project is part of my transition into Python Data / Backend Engineering.  
The goal of v0 was to build a clean, modular console application with practical inventory features, input validation, and JSON-based persistence.

The app allows a user to:

- add inventory items
- list all items
- search items by name
- update existing items
- delete items
- view low-stock items
- save and load inventory data from JSON

## Features

### Current MVP features

- **Add item**
  - name
  - category
  - location
  - quantity
  - minimum quantity
  - notes

- **List all items**
  - displays stored items in a readable format

- **Search by name**
  - case-insensitive
  - partial matches supported

- **Update item**
  - update an item by ID
  - press Enter to keep the current value

- **Delete item**
  - delete an item by ID with confirmation

- **Low-stock view**
  - shows items where quantity is less than or equal to minimum quantity

- **JSON persistence**
  - inventory is loaded on startup
  - inventory is saved on exit
  - Note: The app uses inventory.json as its working file. sample_inventory.json is included as example data and can be copied/renamed to inventory.json before running the app.

## Project structure

```text
household-inventory-tracker/
├── app.py
├── README.md
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
    └── test_inventory_service.py
