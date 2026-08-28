import sqlite3
import os


DB_PATH = "data/peekrakshak.db"


FARMERS = [
    ("MH_YAV_003", "Ganesh Shinde", "9876543210", "Yavatmal", "Pusad", "Cotton"),
    ("MH_YAV_004", "Mahesh Pawar", "9876543211", "Yavatmal", "Darwha", "Cotton"),
    ("MH_YAV_005", "Vijay Rathod", "9876543212", "Yavatmal", "Wani", "Soybean"),
    ("MH_YAV_006", "Ashok Jadhav", "9876543213", "Yavatmal", "Digras", "Cotton"),
    ("MH_YAV_007", "Prakash Patil", "9876543214", "Yavatmal", "Pusad", "Soybean"),

    ("MH_NAG_001", "Sanjay Deshmukh", "9876543215", "Nagpur", "Katol", "Orange"),
    ("MH_NAG_002", "Dinesh Wankhede", "9876543216", "Nagpur", "Hingna", "Soybean"),
    ("MH_NAG_003", "Ramesh Gawande", "9876543217", "Nagpur", "Kalmeshwar", "Cotton"),
    ("MH_NAG_004", "Mohan Borkar", "9876543218", "Nagpur", "Umred", "Cotton"),
    ("MH_NAG_005", "Rajendra Kale", "9876543219", "Nagpur", "Ramtek", "Soybean"),

    ("MH_NAS_002", "Sachin More", "9876543220", "Nashik", "Niphad", "Tomato"),
    ("MH_NAS_003", "Rahul Shinde", "9876543221", "Nashik", "Sinnar", "Onion"),
    ("MH_NAS_004", "Kiran Pawar", "9876543222", "Nashik", "Yeola", "Grapes"),
    ("MH_NAS_005", "Vishal Patil", "9876543223", "Nashik", "Dindori", "Tomato"),

    ("MH_NAN_002", "Datta Jadhav", "9876543224", "Nanded", "Hadgaon", "Soybean"),
    ("MH_NAN_003", "Balaji Pawar", "9876543225", "Nanded", "Deglur", "Cotton"),
    ("MH_NAN_004", "Shankar More", "9876543226", "Nanded", "Kinwat", "Soybean"),
    ("MH_NAN_005", "Vivek Deshmukh", "9876543227", "Nanded", "Loha", "Cotton"),
]


def seed_farmers(cursor):
    print("Seeding farmers...")

    for farmer in FARMERS:
        farmer_id, name, phone, district, taluka, crop = farmer

        cursor.execute(
            """
            INSERT OR IGNORE INTO farmers
            (
                farmer_id,
                full_name,
                phone_number,
                district,
                taluka,
                primary_crop,
                telegram_chat_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                farmer_id,
                name,
                phone,
                district,
                taluka,
                crop,
                ""
            )
        )

    print(f"Processed {len(FARMERS)} demo farmers.")


def seed_pending_cases(cursor):
    print("Seeding Pending Expert cases...")

    cases = [
        ("CASE_EXP_001", "Yavatmal", "Cotton", "pink_bollworm", 0.91),
        ("CASE_EXP_002", "Yavatmal", "Cotton", "pink_bollworm", 0.88),
        ("CASE_EXP_003", "Nagpur", "Soybean", "soybean_rust", 0.79),
        ("CASE_EXP_004", "Nashik", "Tomato", "early_blight", 0.83),
        ("CASE_EXP_005", "Nanded", "Cotton", "leaf_curl", 0.76),
        ("CASE_EXP_006", "Yavatmal", "Soybean", "soybean_rust", 0.81),
        ("CASE_EXP_007", "Nashik", "Onion", "purple_blotch", 0.74),
        ("CASE_EXP_008", "Nagpur", "Cotton", "bollworm", 0.82),
    ]

    for case in cases:
        cursor.execute(
            """
            INSERT OR IGNORE INTO cases
            (
                case_id,
                district,
                crop,
                disease_detected,
                confidence,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                case[0],
                case[1],
                case[2],
                case[3],
                case[4],
                "PENDING_EXPERT"
            )
        )

    print(f"Processed {len(cases)} Pending Expert cases.")


def run_seed():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        seed_farmers(cursor)
        seed_pending_cases(cursor)

        conn.commit()

        print()
        print("Database seeded successfully!")

        cursor.execute("SELECT COUNT(*) FROM farmers")
        farmer_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM cases WHERE status = 'PENDING_EXPERT'"
        )
        pending_count = cursor.fetchone()[0]

        print(f"Total farmers: {farmer_count}")
        print(f"Pending Expert cases: {pending_count}")

    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    run_seed()