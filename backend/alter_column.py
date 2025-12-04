"""
Script to alter the business_criticality column to allow longer values
"""
from app.database import engine
from sqlalchemy import text

# SQL to alter the column
alter_sql = text("""
ALTER TABLE dbo.tpsm_projects
ALTER COLUMN business_criticality NVARCHAR(100) NOT NULL;
""")

try:
    with engine.connect() as conn:
        conn.execute(alter_sql)
        conn.commit()
        print("✅ Column business_criticality successfully altered to NVARCHAR(100)")
except Exception as e:
    print(f"❌ Error altering column: {e}")
