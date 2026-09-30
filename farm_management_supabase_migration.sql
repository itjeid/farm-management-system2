-- ============================================================
-- FARM MANAGEMENT SYSTEM
-- SQLite -> Supabase PostgreSQL migration
-- Generated from the existing instance/farm.db
--
-- IMPORTANT:
-- 1. This file contains the existing records from farm.db.
-- 2. Existing primary-key IDs are preserved.
-- 3. Existing foreign-key relationships are preserved.
-- 4. This SQL does NOT modify the original SQLite database.
-- 5. Review the generated file before executing it.
-- ============================================================

BEGIN;

-- Remove previous copies of these tables in this migration target.
DROP TABLE IF EXISTS "ledger_entries" CASCADE;
DROP TABLE IF EXISTS "health_records" CASCADE;
DROP TABLE IF EXISTS "productions" CASCADE;
DROP TABLE IF EXISTS "labor_activities" CASCADE;
DROP TABLE IF EXISTS "labor_advances" CASCADE;
DROP TABLE IF EXISTS "animals" CASCADE;
DROP TABLE IF EXISTS "workers" CASCADE;
DROP TABLE IF EXISTS "ledger_accounts" CASCADE;
DROP TABLE IF EXISTS "expenses" CASCADE;
DROP TABLE IF EXISTS "income" CASCADE;
DROP TABLE IF EXISTS "users" CASCADE;

-- ============================================================
-- CREATE TABLES
-- ============================================================
CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY,
    "username" VARCHAR(80) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "role" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMP
);

CREATE TABLE "workers" (
    "id" INTEGER PRIMARY KEY,
    "worker_id" VARCHAR(50) NOT NULL,
    "full_name" VARCHAR(150) NOT NULL,
    "phone" VARCHAR(30),
    "role" VARCHAR(100),
    "start_date" DATE,
    "salary" DOUBLE PRECISION,
    "status" VARCHAR(30),
    "created_at" TIMESTAMP
);

CREATE TABLE "animals" (
    "id" INTEGER PRIMARY KEY,
    "animal_id" VARCHAR(50) NOT NULL,
    "animal_type" VARCHAR(20) NOT NULL,
    "breed" VARCHAR(100),
    "gender" VARCHAR(20),
    "date_of_birth" DATE,
    "health_status" VARCHAR(100),
    "purchase_price" DOUBLE PRECISION,
    "created_at" TIMESTAMP
);

CREATE TABLE "expenses" (
    "id" INTEGER PRIMARY KEY,
    "category" VARCHAR(100) NOT NULL,
    "description" VARCHAR(255),
    "amount" DOUBLE PRECISION NOT NULL,
    "expense_date" DATE NOT NULL,
    "created_at" TIMESTAMP
);

CREATE TABLE "income" (
    "id" INTEGER PRIMARY KEY,
    "income_date" DATE NOT NULL,
    "income_type" VARCHAR(100) NOT NULL,
    "description" VARCHAR(255),
    "quantity" DOUBLE PRECISION,
    "unit_price" DOUBLE PRECISION,
    "total_amount" DOUBLE PRECISION NOT NULL,
    "customer" VARCHAR(150),
    "notes" TEXT,
    "created_at" TIMESTAMP
);

CREATE TABLE "ledger_accounts" (
    "id" INTEGER PRIMARY KEY,
    "name" VARCHAR(120) NOT NULL,
    "account_type" VARCHAR(50) NOT NULL,
    "opening_balance" DOUBLE PRECISION NOT NULL,
    "created_at" TIMESTAMP
);

CREATE TABLE "health_records" (
    "id" INTEGER PRIMARY KEY,
    "animal_id" INTEGER NOT NULL,
    "record_date" DATE NOT NULL,
    "health_status" VARCHAR(50) NOT NULL,
    "signs" TEXT,
    "vaccination" VARCHAR(150),
    "medicine_used" VARCHAR(150),
    "veterinarian" VARCHAR(150),
    "notes" TEXT,
    "created_at" TIMESTAMP
);

CREATE TABLE "productions" (
    "id" INTEGER PRIMARY KEY,
    "animal_id" INTEGER NOT NULL,
    "production_date" DATE NOT NULL,
    "morning_quantity" DOUBLE PRECISION,
    "evening_quantity" DOUBLE PRECISION,
    "total_quantity" DOUBLE PRECISION,
    "created_at" TIMESTAMP
);

CREATE TABLE "labor_activities" (
    "id" INTEGER PRIMARY KEY,
    "worker_id" INTEGER NOT NULL,
    "activity_date" DATE NOT NULL,
    "activity" VARCHAR(200) NOT NULL,
    "hours_worked" DOUBLE PRECISION,
    "payment" DOUBLE PRECISION,
    "description" TEXT,
    "created_at" TIMESTAMP
);

CREATE TABLE "labor_advances" (
    "id" INTEGER PRIMARY KEY,
    "worker_id" INTEGER NOT NULL,
    "advance_date" DATE NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "notes" TEXT,
    "created_at" TIMESTAMP
);

CREATE TABLE "ledger_entries" (
    "id" INTEGER PRIMARY KEY,
    "account_id" INTEGER NOT NULL,
    "entry_date" DATE NOT NULL,
    "description" VARCHAR(255) NOT NULL,
    "debit" DOUBLE PRECISION NOT NULL,
    "credit" DOUBLE PRECISION NOT NULL,
    "source_type" VARCHAR(50),
    "source_id" INTEGER,
    "created_at" TIMESTAMP
);

-- ============================================================
-- FOREIGN KEYS
-- ============================================================
ALTER TABLE "health_records" ADD CONSTRAINT "fk_health_records_animal_id" FOREIGN KEY ("animal_id") REFERENCES "animals" ("id");
ALTER TABLE "productions" ADD CONSTRAINT "fk_productions_animal_id" FOREIGN KEY ("animal_id") REFERENCES "animals" ("id");
ALTER TABLE "labor_activities" ADD CONSTRAINT "fk_labor_activities_worker_id" FOREIGN KEY ("worker_id") REFERENCES "workers" ("id");
ALTER TABLE "labor_advances" ADD CONSTRAINT "fk_labor_advances_worker_id" FOREIGN KEY ("worker_id") REFERENCES "workers" ("id");
ALTER TABLE "ledger_entries" ADD CONSTRAINT "fk_ledger_entries_account_id" FOREIGN KEY ("account_id") REFERENCES "ledger_accounts" ("id");

-- ============================================================
-- EXISTING DATA
-- ============================================================

-- users: 1 existing record(s)
INSERT INTO "users" ("id", "username", "password_hash", "role", "created_at") VALUES (1, 'admin', 'scrypt:32768:8:1$OjC4Ru0qZanFv7Ym$5f180c41527d39ead3abc062f2c04043e5f340d71b9283d9a4a5579ab3be66697319a4006258f568ad9ae9063e3b1edb78106f70b99b349757599a87bc7414b8', 'user', '2026-08-20 10:38:43.705645');

-- workers: 2 existing record(s)
INSERT INTO "workers" ("id", "worker_id", "full_name", "phone", "role", "start_date", "salary", "status", "created_at") VALUES (3, 'LAB03', 'MUNYANEZA Musa', '0787170036', 'Farm worker', '2026-09-01', 50000.0, 'Active', '2026-09-01 11:07:57.362937');
INSERT INTO "workers" ("id", "worker_id", "full_name", "phone", "role", "start_date", "salary", "status", "created_at") VALUES (5, 'LAB05', 'KAMANA Cassienne', '0783955079', 'Farm worker', '2026-09-08', 70000.0, 'Active', '2026-09-13 13:40:31.713364');

-- animals: 5 existing record(s)
INSERT INTO "animals" ("id", "animal_id", "animal_type", "breed", "gender", "date_of_birth", "health_status", "purchase_price", "created_at") VALUES (1, 'COW01', 'Cow', 'RUGANGO', 'Female', '2024-11-05', 'Recovered', 2200000.0, '2026-08-19 12:31:55.823585');
INSERT INTO "animals" ("id", "animal_id", "animal_type", "breed", "gender", "date_of_birth", "health_status", "purchase_price", "created_at") VALUES (2, 'COW02', 'Cow', 'INDIBORI', 'Female', '2025-02-19', 'Recovered', 2000000.0, '2026-08-19 12:33:09.596774');
INSERT INTO "animals" ("id", "animal_id", "animal_type", "breed", "gender", "date_of_birth", "health_status", "purchase_price", "created_at") VALUES (3, 'COW03', 'Cow', 'IMBABAZI', 'Female', '2024-12-19', 'Healthy', 2300000.0, '2026-08-19 12:34:05.654068');
INSERT INTO "animals" ("id", "animal_id", "animal_type", "breed", "gender", "date_of_birth", "health_status", "purchase_price", "created_at") VALUES (4, 'COW04', 'Cow', 'INYANA', 'Female', '2025-09-19', 'Healthy', 2000000.0, '2026-08-19 12:35:43.973157');
INSERT INTO "animals" ("id", "animal_id", "animal_type", "breed", "gender", "date_of_birth", "health_status", "purchase_price", "created_at") VALUES (5, 'COW05', 'Cow', 'FIRIZONE', 'Female', '2025-09-19', 'Healthy', 2100000.0, '2026-08-19 12:37:22.668978');

-- expenses: 11 existing record(s)
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (1, 'Feed', 'KAWUNGA, OIL,ONIONS,BEANS', 20600.0, '2026-08-16', '2026-08-19 12:40:34.771128');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (2, 'Other', 'FOOD FOR EATING', 20600.0, '2026-08-03', '2026-08-19 12:42:13.342171');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (3, 'Other', 'fethching water', 1000.0, '2026-08-08', '2026-08-20 12:49:29.981423');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (4, 'Feed', 'IBIRYO', 148000.0, '2026-07-15', '2026-08-20 17:31:54.442708');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (5, 'Feed', 'UMUNYU', 42000.0, '2026-07-17', '2026-08-20 17:32:23.990344');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (6, 'Labor', '', 120000.0, '2026-08-02', '2026-08-20 17:43:31.782466');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (7, 'Labor', 'salary for GASOMINARI', 50000.0, '2026-08-30', '2026-08-30 15:28:00.511720');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (8, 'Labor', 'salary for MUGISHA', 50000.0, '2026-08-30', '2026-08-30 15:28:38.717328');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (9, 'Feed', '100 of brand nd 100kgs ', 40000.0, '2026-08-29', '2026-08-31 13:20:18.074770');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (10, 'Feed', '100kgs of sondore', 15000.0, '2026-08-26', '2026-08-31 13:21:02.929134');
INSERT INTO "expenses" ("id", "category", "description", "amount", "expense_date", "created_at") VALUES (11, 'Other', 'shitingi 3
', 36000.0, '2026-08-31', '2026-08-31 13:24:04.248424');

-- income: 3 existing record(s)
INSERT INTO "income" ("id", "income_date", "income_type", "description", "quantity", "unit_price", "total_amount", "customer", "notes", "created_at") VALUES (1, '2026-08-18', 'Milk', 'milk for five days', 10.0, 700.0, 7000.0, 'Darius', '', '2026-08-20 13:48:09.467140');
INSERT INTO "income" ("id", "income_date", "income_type", "description", "quantity", "unit_price", "total_amount", "customer", "notes", "created_at") VALUES (2, '2026-08-18', 'Milk', '', 15.0, 700.0, 10500.0, 'Darius', '', '2026-08-20 13:49:50.815389');
INSERT INTO "income" ("id", "income_date", "income_type", "description", "quantity", "unit_price", "total_amount", "customer", "notes", "created_at") VALUES (3, '2026-08-29', 'Milk', 'milik for 4 days', 16.0, 700.0, 11200.0, 'Darius', '', '2026-08-31 13:23:03.785347');

-- ledger_accounts: 5 existing record(s)
INSERT INTO "ledger_accounts" ("id", "name", "account_type", "opening_balance", "created_at") VALUES (1, 'Cash', 'Asset', 0.0, '2026-09-12 15:12:14.286056');
INSERT INTO "ledger_accounts" ("id", "name", "account_type", "opening_balance", "created_at") VALUES (2, 'Farm Income', 'Income', 0.0, '2026-09-12 15:12:14.288807');
INSERT INTO "ledger_accounts" ("id", "name", "account_type", "opening_balance", "created_at") VALUES (3, 'Farm Expenses', 'Expense', 0.0, '2026-09-12 15:12:14.289649');
INSERT INTO "ledger_accounts" ("id", "name", "account_type", "opening_balance", "created_at") VALUES (4, 'Labor Cost', 'Expense', 0.0, '2026-09-12 15:12:14.290253');
INSERT INTO "ledger_accounts" ("id", "name", "account_type", "opening_balance", "created_at") VALUES (5, 'Labor Advances', 'Asset', 0.0, '2026-09-12 15:12:14.290735');

-- health_records: 8 existing record(s)
INSERT INTO "health_records" ("id", "animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes", "created_at") VALUES (1, 2, '2026-07-25', 'Sick', 'weakness, high cough,swelling of lymph nodes', '', 'butolex 125ml, oxytetracycline 150 ml,noxolgine 120ml', 'SHUMBUSHO Seth', '', '2026-08-20 12:39:07.642657');
INSERT INTO "health_records" ("id", "animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes", "created_at") VALUES (2, 2, '2026-08-29', 'Sick', 'nasol discharge, weakness,high cough,inappettence,lacrimation,', '', 'butolex 25ml, oxytetracyline 50 ml,phenybit25ml', 'SHUMBUSHO Seth', '', '2026-08-31 13:15:42.719571');
INSERT INTO "health_records" ("id", "animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes", "created_at") VALUES (3, 2, '2026-06-27', 'Sick', 'mappettence,small amount of feed intake, yellowish vive', '', 'butolex 25ml, oxytetracycline 50 ml, novolgine 20ml', 'SHUMBUSHO Seth', '', '2026-09-28 18:18:01.654646');
INSERT INTO "health_records" ("id", "animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes", "created_at") VALUES (4, 1, '2026-06-24', 'Sick', 'inappettence,high cough,lacrimation,small amount of feed intake, yellowish vive', '', 'butolex 25ml, oxytetracyline 20 ml,phenybit25ml', 'SHUMBUSHO Seth', '', '2026-09-28 18:21:04.305247');
INSERT INTO "health_records" ("id", "animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes", "created_at") VALUES (5, 1, '2026-06-25', 'Under Treatment', 'inappettence,high cough,lacrimation,small amount of feed intake, yellowish vive', '', 'cobesia12ml, oxytetracyline 20 ml,phenybit25ml', 'SHUMBUSHO Seth', '', '2026-09-28 18:23:12.907364');
INSERT INTO "health_records" ("id", "animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes", "created_at") VALUES (6, 1, '2026-06-26', 'Under Treatment', 'inappettence,high cough,lacrimation,small amount of feed intake, yellowish vive', '', 'cobesia12ml, oxytetracyline 20 ml,phenybit25ml', 'SHUMBUSHO Seth', '', '2026-09-28 18:24:38.407417');
INSERT INTO "health_records" ("id", "animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes", "created_at") VALUES (7, 1, '2026-08-28', 'Recovered', '', '', '', 'SHUMBUSHO Seth', '', '2026-09-28 18:25:56.375312');
INSERT INTO "health_records" ("id", "animal_id", "record_date", "health_status", "signs", "vaccination", "medicine_used", "veterinarian", "notes", "created_at") VALUES (8, 2, '2026-08-28', 'Recovered', '', '', '', 'SHUMBUSHO Seth', '', '2026-09-28 18:26:56.163026');

-- productions: 14 existing record(s)
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (1, 2, '2026-08-19', 5.0, 5.0, 10.0, '2026-08-19 12:38:30.685850');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (2, 2, '2026-08-18', 5.0, 5.0, 10.0, '2026-08-19 12:38:58.317605');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (3, 2, '2026-08-18', 5.0, 4.0, 9.0, '2026-08-30 15:31:01.933805');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (4, 2, '2026-08-19', 5.0, 4.0, 9.0, '2026-08-30 15:31:44.730510');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (5, 2, '2026-08-20', 5.0, 4.0, 9.0, '2026-08-30 15:32:37.280202');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (6, 2, '2026-08-21', 4.0, 3.0, 7.0, '2026-08-30 15:33:00.816650');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (7, 2, '2026-08-22', 4.0, 3.0, 7.0, '2026-08-30 15:33:20.831144');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (8, 2, '2026-08-23', 4.0, 3.0, 7.0, '2026-08-30 15:33:41.569773');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (9, 2, '2026-08-24', 4.0, 3.0, 7.0, '2026-08-30 15:34:01.549031');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (10, 2, '2026-08-25', 4.0, 3.0, 7.0, '2026-08-30 15:34:24.214694');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (11, 2, '2026-08-26', 4.0, 3.0, 7.0, '2026-08-30 15:34:44.250444');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (12, 2, '2026-08-27', 4.0, 3.0, 7.0, '2026-08-30 15:35:01.357696');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (13, 2, '2026-08-28', 4.0, 3.0, 7.0, '2026-08-30 15:35:27.174605');
INSERT INTO "productions" ("id", "animal_id", "production_date", "morning_quantity", "evening_quantity", "total_quantity", "created_at") VALUES (14, 2, '2026-08-29', 4.0, 0.0, 4.0, '2026-08-30 15:36:07.344499');

-- labor_activities: 1 existing record(s)
INSERT INTO "labor_activities" ("id", "worker_id", "activity_date", "activity", "hours_worked", "payment", "description", "created_at") VALUES (7, 3, '2026-09-01', 'KUVOMA, KWAHIRA ISASO', 0.0, 50000.0, '', '2026-09-01 11:08:46.716639');

-- labor_advances: 3 existing record(s)
INSERT INTO "labor_advances" ("id", "worker_id", "advance_date", "amount", "notes", "created_at") VALUES (1, 3, '2026-09-06', 5000.0, '', '2026-09-13 13:41:01.599153');
INSERT INTO "labor_advances" ("id", "worker_id", "advance_date", "amount", "notes", "created_at") VALUES (2, 3, '2026-09-13', 2000.0, '', '2026-09-13 13:41:45.637264');
INSERT INTO "labor_advances" ("id", "worker_id", "advance_date", "amount", "notes", "created_at") VALUES (4, 5, '2026-09-11', 18000.0, '', '2026-09-13 13:43:04.863153');

-- ledger_entries: 0 existing record(s)
-- No records to insert.

-- ============================================================
-- SEQUENCE / ID SAFETY
-- ============================================================
-- IDs are deliberately stored as INTEGER PRIMARY KEY values.
-- The Flask application will continue using the existing IDs.

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
SELECT 'users' AS table_name, COUNT(*) AS record_count FROM "users";
SELECT 'workers' AS table_name, COUNT(*) AS record_count FROM "workers";
SELECT 'animals' AS table_name, COUNT(*) AS record_count FROM "animals";
SELECT 'expenses' AS table_name, COUNT(*) AS record_count FROM "expenses";
SELECT 'income' AS table_name, COUNT(*) AS record_count FROM "income";
SELECT 'ledger_accounts' AS table_name, COUNT(*) AS record_count FROM "ledger_accounts";
SELECT 'health_records' AS table_name, COUNT(*) AS record_count FROM "health_records";
SELECT 'productions' AS table_name, COUNT(*) AS record_count FROM "productions";
SELECT 'labor_activities' AS table_name, COUNT(*) AS record_count FROM "labor_activities";
SELECT 'labor_advances' AS table_name, COUNT(*) AS record_count FROM "labor_advances";
SELECT 'ledger_entries' AS table_name, COUNT(*) AS record_count FROM "ledger_entries";

-- Expected total records from the source database: 53
-- The source record counts are also listed in the generated report.

COMMIT;
