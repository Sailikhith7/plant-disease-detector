import os
import psycopg2

DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@localhost:5432/kisanmitra")

def run_seed():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        with open("data/seed_cases.sql", "r") as f:
            cur.execute(f.read())
        conn.commit()
        cur.close()
        conn.close()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == "__main__":
    run_seed()