# Household Inventory Tracker Backlog

## v0.1 candidates
- Improve README with sample data note cleanup
- Add a few more basic pytest tests
- Review and polish user-facing messages
- Consider saving automatically after add/update/delete
- Improve list/search output formatting if needed

## v1 candidates
- Add sorting options (name, category, location, quantity)
- Add grouping options (by category, by location)
- Add smart default values for common fields
- Add optional category-to-location mapping
- Improve search to include category and location
- Add ability to clear notes during update
- Add export/import options

## Database version
- Replace JSON persistence with SQLite or PostgreSQL
- Create items table schema
- Map current item structure to relational storage
- Reuse existing app logic where possible
- Compare console version vs database-backed version

## API / backend version
- Build FastAPI version of the project
- Add CRUD endpoints
- Add low-stock endpoint
- Use PostgreSQL as the storage layer
- Containerize with Docker

## Nice future ideas
- Automatic restock suggestions
- Smarter low-stock rules per category
- Better terminal formatting
- Demo mode / sample data mode