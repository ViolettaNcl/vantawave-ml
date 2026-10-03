# PostgreSQL Mode

VantaWave v0.9 uses SQLite by default, but the same SQLAlchemy ORM can run
against PostgreSQL.

Install:

```powershell
pip install -e ".[dev,postgres]"
```

Set the connection URL:

```powershell
$env:VANTAWAVE_DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/vantawave"
```

Apply migrations:

```powershell
alembic upgrade head
```

Validate:

```powershell
python scripts/init_database.py
python -m uvicorn vantawave.api.main:app --reload
```

Then check:

`GET /db/health`

Psycopg 3 is used instead of the legacy psycopg2 adapter.
