# BookTracker Backend

FastAPI backend application for managing books with high-performance search and database optimization for millions of records.

## Features

- RESTful API for book management (CRUD operations)
- Advanced search functionality on title and author fields using PostgreSQL trigram indexes
- Data validation with detailed error responses (ISBN validation included)
- Database optimization for handling up to 10 million records
- Cursor-based pagination for efficient large dataset handling
- PostgreSQL GIN indexes with pg_trgm extension for fast text search

## Tech Stack

- Python + FastAPI
- PostgreSQL with pg_trgm extension
- SQLAlchemy ORM with async support
- Pydantic for data validation
- Alembic for database migrations
- MyPy for static type checking
- Black for code formatting
- Faker for test data generation
- pytest for testing
- Docker & Docker Compose

## Quick Start

### Prerequisites
- Docker
- Docker Compose

## Installation
1. Clone the repository
2. Copy `.env.` to `.env`
3. Build app with script
```shell
chmod +x scripts/install.sh && ./scripts/install.sh
```

## Run the app
Start the application:
```shell
chmod +x scripts/run.sh && ./scripts/run.sh
```

## Insert records to the database
Data is generated using `Faker`.

You can control how many records to insert by passing the `--count` argument.  
By default, it inserts 10_000 records.
```shell
docker exec -it book-tracker-fastapi bash -c "python3 scripts/generate_books.py --count 10000"
```

## Run tests
Start the application:
```shell
docker exec -it book-tracker-fastapi bash -c "pytest"
```

## Code Quality
Run type checking and formatting:
```shell
docker exec -it book-tracker-fastapi bash -c "./scripts/check.sh"
```

The check script runs:
- **Black** - code formatting
- **MyPy** - static type checking

## Access to Application / Swagger
The application will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/internal_api/docs (username: `admin`, password: `admin`)

## Stopping the Application
```shell
docker-compose down
```

## Database Migrations

Create new migration:
```shell
docker exec -it book-tracker-fastapi bash -c "./migrations/makemigrations.sh"
```

Apply migrations:
```shell
docker exec -it book-tracker-fastapi bash -c "./migrations/migrate.sh"
```

Rollback last migration:
```shell
docker exec -it book-tracker-fastapi bash -c "alembic downgrade -1"
```

## Performance Testing

The application includes a data generator for testing with large datasets:

```shell
# Generate 10 million test records (takes ~30 minutes)
python3 scripts/generate_books.py
```

**Search Performance Optimization:**
- Previously used vector search but it only supported exact matches, not ILIKE operations
- Switched to PostgreSQL trigram indexes with GIN for flexible substring search
- Force disables `enable_seqscan` and `enable_indexscan` to guarantee bitmap index scan usage
- Ensures consistent 60ms response time vs 10s+ with sequential scan on 10M records
- Settings applied locally per transaction to avoid affecting other queries