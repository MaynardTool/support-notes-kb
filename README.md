# file: README.md
# Support Notes KB

A knowledge base / notes web application for application support engineers. Centralizes notes previously stored in OneNote/Notepad++ folders, makes them searchable, and allows multiple users to log in and create/update notes.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- uv package manager

## Quick Start with Docker

1. Start PostgreSQL with Docker:
```bash
docker-compose up -d postgres
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your settings (DATABASE_URL already configured for docker-compose)
```

3. Run the app using Python directly:
```bash
# Create virtual environment with uv
uv venv
uv sync

# Run migrations
flask db upgrade

# Create first admin user
flask create-admin --email admin@example.com --name "Admin" --password "admin123"

# Run the app
flask run
```

Visit http://localhost:5000

## Manual PostgreSQL Setup

If not using Docker:

1. Create database:
```sql
CREATE DATABASE notesdb;
CREATE USER notesuser WITH PASSWORD 'notespass';
GRANT ALL PRIVILEGES ON DATABASE notesdb TO notesuser;
```

2. Update DATABASE_URL in .env:
```
DATABASE_URL=postgresql://notesuser:notespass@localhost:5432/notesdb
```

## Commands

### Create Admin User
```bash
flask create-admin --email admin@example.com --name "Admin" --password "admin123"
```

### Run Migrations
```bash
flask db upgrade
```

### Create Migration
```bash
flask db migrate -m "description"
```

### Run Importers

Import .txt and .md files:
```bash
flask import-files --path /path/to/notes --tag-from-folders --default-tags "support"
```

Import OneNote HTML exports:
```bash
flask import-onenote --path /path/to/onenote/export
```

### Run Tests
```bash
pytest
```

## Features

- User authentication with Flask-Login
- Markdown editor (SimpleMDE) for note creation/editing
- Full-text search with PostgreSQL
- Tag management
- Import notes from .txt, .md, or OneNote HTML exports

## Security

- CSRF protection on all forms
- Password hashing with Werkzeug
- Secure session cookies
- XSS protection with bleach
- SQL injection prevention via SQLAlchemy
