import sqlite3
from pathlib import Path

# ============================================================
# FARM MANAGEMENT SYSTEM
# SQLite -> Supabase PostgreSQL migration generator
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "farm.db"
OUTPUT_SQL = BASE_DIR / "farm_management_supabase_migration.sql"
OUTPUT_REPORT = BASE_DIR / "farm_management_migration_report.txt"

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"SQLite database was not found:\n{DB_PATH}\n\n"
        "Make sure this script is inside the farm_management_system folder."
    )

# Exact schema obtained from the existing SQLite database.
TABLES = {
    "users": [
        ("id", "INTEGER", True, True),
        ("username", "VARCHAR(80)", True, False),
        ("password_hash", "VARCHAR(255)", True, False),
        ("role", "VARCHAR(30)", True, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "workers": [
        ("id", "INTEGER", True, True),
        ("worker_id", "VARCHAR(50)", True, False),
        ("full_name", "VARCHAR(150)", True, False),
        ("phone", "VARCHAR(30)", False, False),
        ("role", "VARCHAR(100)", False, False),
        ("start_date", "DATE", False, False),
        ("salary", "DOUBLE PRECISION", False, False),
        ("status", "VARCHAR(30)", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "animals": [
        ("id", "INTEGER", True, True),
        ("animal_id", "VARCHAR(50)", True, False),
        ("animal_type", "VARCHAR(20)", True, False),
        ("breed", "VARCHAR(100)", False, False),
        ("gender", "VARCHAR(20)", False, False),
        ("date_of_birth", "DATE", False, False),
        ("health_status", "VARCHAR(100)", False, False),
        ("purchase_price", "DOUBLE PRECISION", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "expenses": [
        ("id", "INTEGER", True, True),
        ("category", "VARCHAR(100)", True, False),
        ("description", "VARCHAR(255)", False, False),
        ("amount", "DOUBLE PRECISION", True, False),
        ("expense_date", "DATE", True, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "income": [
        ("id", "INTEGER", True, True),
        ("income_date", "DATE", True, False),
        ("income_type", "VARCHAR(100)", True, False),
        ("description", "VARCHAR(255)", False, False),
        ("quantity", "DOUBLE PRECISION", False, False),
        ("unit_price", "DOUBLE PRECISION", False, False),
        ("total_amount", "DOUBLE PRECISION", True, False),
        ("customer", "VARCHAR(150)", False, False),
        ("notes", "TEXT", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "ledger_accounts": [
        ("id", "INTEGER", True, True),
        ("name", "VARCHAR(120)", True, False),
        ("account_type", "VARCHAR(50)", True, False),
        ("opening_balance", "DOUBLE PRECISION", True, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "health_records": [
        ("id", "INTEGER", True, True),
        ("animal_id", "INTEGER", True, False),
        ("record_date", "DATE", True, False),
        ("health_status", "VARCHAR(50)", True, False),
        ("signs", "TEXT", False, False),
        ("vaccination", "VARCHAR(150)", False, False),
        ("medicine_used", "VARCHAR(150)", False, False),
        ("veterinarian", "VARCHAR(150)", False, False),
        ("notes", "TEXT", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "productions": [
        ("id", "INTEGER", True, True),
        ("animal_id", "INTEGER", True, False),
        ("production_date", "DATE", True, False),
        ("morning_quantity", "DOUBLE PRECISION", False, False),
        ("evening_quantity", "DOUBLE PRECISION", False, False),
        ("total_quantity", "DOUBLE PRECISION", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "labor_activities": [
        ("id", "INTEGER", True, True),
        ("worker_id", "INTEGER", True, False),
        ("activity_date", "DATE", True, False),
        ("activity", "VARCHAR(200)", True, False),
        ("hours_worked", "DOUBLE PRECISION", False, False),
        ("payment", "DOUBLE PRECISION", False, False),
        ("description", "TEXT", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "labor_advances": [
        ("id", "INTEGER", True, True),
        ("worker_id", "INTEGER", True, False),
        ("advance_date", "DATE", True, False),
        ("amount", "DOUBLE PRECISION", True, False),
        ("notes", "TEXT", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
    "ledger_entries": [
        ("id", "INTEGER", True, True),
        ("account_id", "INTEGER", True, False),
        ("entry_date", "DATE", True, False),
        ("description", "VARCHAR(255)", True, False),
        ("debit", "DOUBLE PRECISION", True, False),
        ("credit", "DOUBLE PRECISION", True, False),
        ("source_type", "VARCHAR(50)", False, False),
        ("source_id", "INTEGER", False, False),
        ("created_at", "TIMESTAMP", False, False),
    ],
}

# Foreign keys in the existing application structure.
FOREIGN_KEYS = [
    ("health_records", "animal_id", "animals", "id"),
    ("productions", "animal_id", "animals", "id"),
    ("labor_activities", "worker_id", "workers", "id"),
    ("labor_advances", "worker_id", "workers", "id"),
    ("ledger_entries", "account_id", "ledger_accounts", "id"),
]

# Parents must be inserted before children.
INSERT_ORDER = [
    "users",
    "workers",
    "animals",
    "expenses",
    "income",
    "ledger_accounts",
    "health_records",
    "productions",
    "labor_activities",
    "labor_advances",
    "ledger_entries",
]

# Drop children before parents.
DROP_ORDER = [
    "ledger_entries",
    "health_records",
    "productions",
    "labor_activities",
    "labor_advances",
    "animals",
    "workers",
    "ledger_accounts",
    "expenses",
    "income",
    "users",
]


def sql_value(value):
    """Convert a SQLite value to a safe PostgreSQL SQL literal."""
    if value is None:
        return "NULL"

    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"

    if isinstance(value, (int, float)):
        return str(value)

    # SQLite normally returns dates/timestamps as strings in this database.
    text = str(value)

    # PostgreSQL standard single-quote escaping.
    return "'" + text.replace("'", "''") + "'"


def quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # Verify that the expected tables actually exist.
        actual_tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table'"
            ).fetchall()
        }

        missing = set(TABLES) - actual_tables
        if missing:
            raise RuntimeError(
                "The following expected tables are missing from farm.db: "
                + ", ".join(sorted(missing))
            )

        counts = {}
        rows_by_table = {}

        for table in INSERT_ORDER:
            rows = conn.execute(
                f'SELECT * FROM {quote_identifier(table)} ORDER BY id'
            ).fetchall()

            counts[table] = len(rows)
            rows_by_table[table] = rows

        total = sum(counts.values())

        sql = []
        sql.append("-- ============================================================")
        sql.append("-- FARM MANAGEMENT SYSTEM")
        sql.append("-- SQLite -> Supabase PostgreSQL migration")
        sql.append("-- Generated from the existing instance/farm.db")
        sql.append("--")
        sql.append("-- IMPORTANT:")
        sql.append("-- 1. This file contains the existing records from farm.db.")
        sql.append("-- 2. Existing primary-key IDs are preserved.")
        sql.append("-- 3. Existing foreign-key relationships are preserved.")
        sql.append("-- 4. This SQL does NOT modify the original SQLite database.")
        sql.append("-- 5. Review the generated file before executing it.")
        sql.append("-- ============================================================")
        sql.append("")
        sql.append("BEGIN;")
        sql.append("")

        # Drop only the migration's tables.
        sql.append("-- Remove previous copies of these tables in this migration target.")
        for table in DROP_ORDER:
            sql.append(
                f"DROP TABLE IF EXISTS {quote_identifier(table)} CASCADE;"
            )
        sql.append("")

        # Create tables.
        sql.append("-- ============================================================")
        sql.append("-- CREATE TABLES")
        sql.append("-- ============================================================")

        for table in INSERT_ORDER:
            definitions = []

            for name, pg_type, not_null, primary_key in TABLES[table]:
                definition = f"{quote_identifier(name)} {pg_type}"

                if primary_key:
                    definition += " PRIMARY KEY"
                elif not_null:
                    definition += " NOT NULL"

                definitions.append(definition)

            sql.append(f"CREATE TABLE {quote_identifier(table)} (")
            sql.append("    " + ",\n    ".join(definitions))
            sql.append(");")
            sql.append("")

        # Add foreign keys.
        sql.append("-- ============================================================")
        sql.append("-- FOREIGN KEYS")
        sql.append("-- ============================================================")

        for table, column, parent, parent_column in FOREIGN_KEYS:
            constraint = f"fk_{table}_{column}"
            sql.append(
                f"ALTER TABLE {quote_identifier(table)} "
                f"ADD CONSTRAINT {quote_identifier(constraint)} "
                f"FOREIGN KEY ({quote_identifier(column)}) "
                f"REFERENCES {quote_identifier(parent)} "
                f"({quote_identifier(parent_column)});"
            )

        sql.append("")

        # Insert records.
        sql.append("-- ============================================================")
        sql.append("-- EXISTING DATA")
        sql.append("-- ============================================================")

        for table in INSERT_ORDER:
            rows = rows_by_table[table]

            sql.append("")
            sql.append(
                f"-- {table}: {len(rows)} existing record(s)"
            )

            if not rows:
                sql.append("-- No records to insert.")
                continue

            column_names = [item[0] for item in TABLES[table]]
            columns = ", ".join(
                quote_identifier(name) for name in column_names
            )

            for row in rows:
                values = ", ".join(
                    sql_value(row[name]) for name in column_names
                )

                sql.append(
                    f"INSERT INTO {quote_identifier(table)} "
                    f"({columns}) VALUES ({values});"
                )

        sql.append("")
        sql.append("-- ============================================================")
        sql.append("-- SEQUENCE / ID SAFETY")
        sql.append("-- ============================================================")
        sql.append("-- IDs are deliberately stored as INTEGER PRIMARY KEY values.")
        sql.append("-- The Flask application will continue using the existing IDs.")
        sql.append("")

        # Verification queries.
        sql.append("-- ============================================================")
        sql.append("-- VERIFICATION QUERIES")
        sql.append("-- ============================================================")

        for table in INSERT_ORDER:
            sql.append(
                f"SELECT '{table}' AS table_name, "
                f"COUNT(*) AS record_count "
                f"FROM {quote_identifier(table)};"
            )

        sql.append("")
        sql.append(
            f"-- Expected total records from the source database: {total}"
        )
        sql.append(
            "-- The source record counts are also listed in the generated report."
        )
        sql.append("")
        sql.append("COMMIT;")
        sql.append("")

        OUTPUT_SQL.write_text("\n".join(sql), encoding="utf-8")

        report = []
        report.append("FARM MANAGEMENT SYSTEM")
        report.append("DATABASE MIGRATION REPORT")
        report.append("=" * 60)
        report.append(f"Source database: {DB_PATH}")
        report.append("")
        report.append("SOURCE RECORD COUNTS")
        report.append("-" * 60)

        for table in INSERT_ORDER:
            report.append(f"{table}: {counts[table]}")

        report.append("-" * 60)
        report.append(f"TOTAL: {total}")
        report.append("")
        report.append("Expected source totals:")
        report.append("animals: 5")
        report.append("expenses: 11")
        report.append("health_records: 8")
        report.append("income: 3")
        report.append("labor_activities: 1")
        report.append("labor_advances: 3")
        report.append("ledger_accounts: 5")
        report.append("ledger_entries: 0")
        report.append("productions: 14")
        report.append("users: 1")
        report.append("workers: 2")
        report.append("TOTAL: 53")
        report.append("")
        report.append(
            "The migration preserves the existing primary-key IDs and "
            "foreign-key relationships."
        )
        report.append(
            "The original farm.db is never modified by this script."
        )

        OUTPUT_REPORT.write_text("\n".join(report), encoding="utf-8")

        print()
        print("=" * 60)
        print("MIGRATION FILE GENERATED SUCCESSFULLY")
        print("=" * 60)
        print(f"Source database : {DB_PATH}")
        print(f"SQL file        : {OUTPUT_SQL}")
        print(f"Report file     : {OUTPUT_REPORT}")
        print()
        print("Record counts:")
        for table in INSERT_ORDER:
            print(f"  {table:<20} {counts[table]}")
        print("-" * 35)
        print(f"  {'TOTAL':<20} {total}")
        print()
        print("Your original farm.db has NOT been modified.")
        print()

    finally:
        conn.close()


if __name__ == "__main__":
    main()
