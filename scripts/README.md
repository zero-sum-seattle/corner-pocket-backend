# Database Scripts 🎱

Helper scripts for managing your Corner Pocket database.

## Seed Script

Populates the database with sample data for development.

### Usage

```bash
# Make sure PostgreSQL is running
docker compose up -d db

# Run migrations first (if not already done)
poetry run alembic upgrade head

# Seed the database
poetry run python scripts/seed_db.py
```

### What it creates

The seed script creates:
- **3 users**: Fast Eddie, Minnesota Fats, and Vincent
- **3 matches**: 
  - Match 1: Eddie vs Fats (APPROVED, 9-ball, race to 5) - 6 games
  - Match 2: Eddie vs Vincent (PENDING, 8-ball, race to 7) - 3 games  
  - Match 3: Vincent vs Fats (APPROVED, 10-ball, race to 3) - 4 games
- **2 approvals**: For the approved matches

Perfect for testing the API and UI!

### Warning ⚠️

This script does **not** clear existing data. If you run it multiple times, you'll get duplicate users with integrity errors. To start fresh:

```bash
# Drop and recreate the database
docker compose down -v
docker compose up -d db
poetry run alembic upgrade head
poetry run python scripts/seed_db.py
```

