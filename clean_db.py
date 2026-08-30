import sqlite3
import os
import glob
from backend.database import Base, engine

DB_PATH = "data/peekrakshak.db"
UPLOADS_DIR = "uploads"

print("1. Recreating clean database tables via SQLAlchemy schema...")
Base.metadata.create_all(bind=engine)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("2. Inspecting table structures...")
cursor.execute("PRAGMA table_info(cases);")
case_columns = [col[1] for col in cursor.fetchall()]
print(f"Available columns in 'cases': {case_columns}")

# Clear existing records safely
try:
    cursor.execute("DELETE FROM cases;")
    cursor.execute("DELETE FROM farmers;")
except Exception as e:
    print(f"Note during clear: {e}")
conn.commit()

print("3. Inserting clean, professional demo cases dynamically...")
# Map sample values safely based on what columns actually exist in your database
sample_farmer_name = "Ramesh Patil"
sample_district = "Amravati"

try:
    # Try inserting using common column variations
    if "case_id" in case_columns:
        cursor.execute("""
            INSERT INTO cases (case_id, crop, status) 
            VALUES (?, ?, ?)
        """, ("CASE_DEMO_01", "cotton", "Pending Expert"))
    elif "id" in case_columns:
        cursor.execute("""
            INSERT INTO cases (id, crop, status) 
            VALUES (?, ?, ?)
        """, ("CASE_DEMO_01", "cotton", "Pending Expert"))
    
    conn.commit()
    print("Demo case inserted successfully!")
except Exception as e:
    print(f"Custom insert skipped (schema variation notice): {e}")

conn.close()

print("4. Clearing junk files from uploads folder...")
files = glob.glob(os.path.join(UPLOADS_DIR, "*"))
for f in files:
    if not f.endswith(".gitkeep"):
        try:
            os.remove(f)
            print(f"Deleted junk upload: {f}")
        except Exception as e:
            print(f"Could not delete {f}: {e}")

print("Cleanup completed successfully! Your dashboard is now fresh and ready.")