import sqlite3

DB_PATH = "data/peekrakshak.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Delete the demo case or any temporary test case from the cases table
cursor.execute("DELETE FROM cases WHERE case_id LIKE '%DEMO%' OR case_id LIKE '%CASE_DEMO%';")
conn.commit()
conn.close()

print("Demo cases deleted successfully from the database!")