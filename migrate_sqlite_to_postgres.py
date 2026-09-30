import os
import sqlite3
from sqlalchemy import create_engine, MetaData, select, text

SOURCE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "instance", "farm.db"
)
TARGET = os.environ.get("DATABASE_URL")

if not TARGET:
    raise SystemExit(
        "Set DATABASE_URL to the Render PostgreSQL Internal Database URL before running this script."
    )

if TARGET.startswith("postgres://"):
    TARGET = TARGET.replace("postgres://", "postgresql://", 1)
if TARGET.startswith("postgresql://"):
    TARGET = TARGET.replace("postgresql://", "postgresql+psycopg://", 1)

print("SOURCE:", SOURCE)
print("TARGET: PostgreSQL configured")
print("This utility copies existing SQLite rows into PostgreSQL and never modifies the SQLite file.")

src = sqlite3.connect(SOURCE)
src.row_factory = sqlite3.Row
dst = create_engine(TARGET, pool_pre_ping=True)
metadata = MetaData()
metadata.reflect(bind=dst)

# Existing tables first; additive tables are included only if they already exist.
order = [
    "users", "animals", "workers", "income", "expenses",
    "health_records", "productions", "labor_activities",
    "labor_advances",
]

with dst.begin() as conn:
    for name in order:
        if name not in metadata.tables:
            print("Skipping missing PostgreSQL table:", name)
            continue

        rows = src.execute(f'SELECT * FROM "{name}"').fetchall()
        table = metadata.tables[name]
        if not rows:
            continue

        existing_ids = (
            {r[0] for r in conn.execute(select(table.c.id)).fetchall()}
            if "id" in table.c else set()
        )
        inserted = 0

        for row in rows:
            data = dict(row)
            if "id" in data and data["id"] in existing_ids:
                continue
            allowed = {c.name for c in table.columns}
            data = {k: v for k, v in data.items() if k in allowed}
            conn.execute(table.insert().values(**data))
            inserted += 1

        print(
            f"{name}: {inserted} row(s) copied; "
            f"{len(rows) - inserted} skipped as existing."
        )

    # Reset PostgreSQL sequences without touching source data.
    for name in order:
        if name not in metadata.tables or "id" not in metadata.tables[name].columns:
            continue
        try:
            sql = (
                "SELECT setval(pg_get_serial_sequence("
                + repr(name)
                + ", 'id'), COALESCE((SELECT MAX(id) FROM "
                + '"' + name + '"'
                + "), 1), true)"
            )
            conn.execute(text(sql))
        except Exception as error:
            print(f"Sequence reset skipped for {name}: {error}")

src.close()
print("Migration finished. Verify the live dashboard and reports before making more changes.")
