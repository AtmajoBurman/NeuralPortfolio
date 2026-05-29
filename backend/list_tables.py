import asyncio
from sqlalchemy import text
from app.database import engine

async def main():
    async with engine.connect() as conn:
        # PostgreSQL query to get all table names in the public schema
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        result = await conn.execute(query)
        tables = result.fetchall()
        
        print("\n--- Tables in your Database ---")
        for table in tables:
            print(f"- {table[0]}")
        print("-------------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())
