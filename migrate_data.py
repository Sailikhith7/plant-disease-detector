# migrate_data.py
import os
import sqlite3
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# 1. Connect to Neon Cloud Postgres
POSTGRES_URL = os.getenv("DATABASE_URL")
if not POSTGRES_URL:
    raise ValueError("DATABASE_URL not found in .env file!")

if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

pg_engine = create_engine(POSTGRES_URL)

# 2. Table creation schemas for PostgreSQL
TABLE_SCHEMAS = [
    """
    CREATE TABLE IF NOT EXISTS cases (
        case_id VARCHAR(100) PRIMARY KEY,
        farmer_id VARCHAR(100),
        farmer_name VARCHAR(255),
        district VARCHAR(100),
        crop VARCHAR(100),
        disease_detected VARCHAR(255),
        confidence FLOAT,
        severity VARCHAR(50),
        latitude FLOAT,
        longitude FLOAT,
        image_url TEXT,
        status VARCHAR(50),
        created_at TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expert_responses (
        id SERIAL PRIMARY KEY,
        case_id VARCHAR(100),
        expert_response TEXT,
        created_at TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS alert_dispatches (
        id SERIAL PRIMARY KEY,
        district VARCHAR(100),
        crop VARCHAR(100),
        disease VARCHAR(255),
        target_phone VARCHAR(50),
        officer_message TEXT,
        delivery_channel VARCHAR(50),
        status VARCHAR(50),
        dispatched_at TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS farmers (
        id SERIAL PRIMARY KEY,
        farmer_id VARCHAR(100) UNIQUE,
        name VARCHAR(255),
        phone VARCHAR(50),
        district VARCHAR(100),
        crop VARCHAR(100)
    );
    """
]

# Create tables in Neon
print("1. Creating tables in Neon PostgreSQL...")
with pg_engine.begin() as pg_conn:
    for schema in TABLE_SCHEMAS:
        pg_conn.execute(text(schema))
print("Tables created successfully!")

# 3. Connect to local SQLite & migrate data
sqlite_path = "data/peekrakshak.db"
sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_cursor = sqlite_conn.cursor()

# Migrate order: 'cases' before 'expert_responses' to prevent foreign key conflicts
migrate_order = ["cases", "farmers", "expert_responses", "alert_dispatches"]

print("\n2. Transferring records to Neon PostgreSQL...")
with pg_engine.begin() as pg_conn:
    for table_name in migrate_order:
        try:
            sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in sqlite_cursor.fetchall()]
            
            sqlite_cursor.execute(f"SELECT * FROM {table_name};")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"Table '{table_name}': 0 records found in SQLite.")
                continue

            col_names = ", ".join([f'"{c}"' for c in columns])
            placeholders = ", ".join([f":{c}" for c in columns])
            
            insert_stmt = text(f"""
                INSERT INTO {table_name} ({col_names})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING;
            """)

            for row in rows:
                row_dict = dict(zip(columns, row))
                pg_conn.execute(insert_stmt, row_dict)
            
            print(f"Table '{table_name}': Migrated {len(rows)} records.")
        except Exception as e:
            print(f"Error migrating table '{table_name}': {e}")

sqlite_conn.close()
print("\nCloud migration completed successfully!")