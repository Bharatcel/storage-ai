import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=aznprd-neu-ghub-sql01-01.database.windows.net;'
    'DATABASE=aznprd-neu-ghub-sqldb01;'
    'UID=sqladmin;'
    'PWD=0M2NkOo1c2OMqlwxrbw03o6G18WExijA'
)
cursor = conn.cursor()

# Get extension distribution for NULL date files
print("=" * 60)
print("EXTENSION DISTRIBUTION FOR FILES WITH NULL DATES")
print("=" * 60)
cursor.execute('''
    SELECT extension, COUNT(*) as count
    FROM dbo.tpsm_file_metadata
    WHERE project_id = 16 AND modified_date IS NULL
    GROUP BY extension
    ORDER BY COUNT(*) DESC
''')
print(f"{'Extension':<15} {'Count':>15}")
print("-" * 35)
total_null = 0
for row in cursor.fetchall():
    ext = row[0] if row[0] else '(no extension)'
    count = row[1]
    total_null += count
    print(f"{ext:<15} {count:>15,}")
print("-" * 35)
print(f"{'TOTAL':<15} {total_null:>15,}")

print("\n" + "=" * 60)
print("EXTENSION DISTRIBUTION FOR FILES WITH DATES")
print("=" * 60)
cursor.execute('''
    SELECT extension, COUNT(*) as count
    FROM dbo.tpsm_file_metadata
    WHERE project_id = 16 AND modified_date IS NOT NULL
    GROUP BY extension
    ORDER BY COUNT(*) DESC
''')
print(f"{'Extension':<15} {'Count':>15}")
print("-" * 35)
total_with_dates = 0
for row in cursor.fetchall():
    ext = row[0] if row[0] else '(no extension)'
    count = row[1]
    total_with_dates += count
    print(f"{ext:<15} {count:>15,}")
print("-" * 35)
print(f"{'TOTAL':<15} {total_with_dates:>15,}")

print("\n" + "=" * 60)
print(f"SUMMARY: {total_null:,} files without dates, {total_with_dates:,} files with dates")
print("=" * 60)

conn.close()
