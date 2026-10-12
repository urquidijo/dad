import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def run_migration():
    print(f"Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    # 1. Read and run schema.sql
    print("Executing scripts/schema.sql...")
    with open("scripts/schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cur.execute(schema_sql)
    print("Schema created successfully!")

    # 2. Read and run seed.sql
    print("Executing scripts/seed.sql...")
    with open("scripts/seed.sql", "r", encoding="utf-8") as f:
        seed_sql = f.read()
    cur.execute(seed_sql)
    print("Seed data inserted successfully!")

    # 3. Check tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
    tables = [row[0] for row in cur.fetchall()]
    print(f"\nTables in database: {tables}")

    # 4. Check product count
    cur.execute("SELECT sku, name, list_price, base_cost FROM products;")
    products = cur.fetchall()
    print("\nProducts in database:")
    for p in products:
        print(f"  [{p[0]}] {p[1]} | MSRP: ${p[2]} | Cost: ${p[3]}")

    cur.close()
    conn.close()
    print("\nMigration completed successfully!")

if __name__ == "__main__":
    run_migration()
