"""
Test script to analyze the sample CSV file structure
"""
import csv
import os
from datetime import datetime
from collections import defaultdict

# Path to your CSV file
CSV_FILE = r"c:\Users\sharma.25274\Downloads\DC1IOPSUAT-20231227-2004-DriveFileDetails.csv"

def analyze_csv_structure():
    """Analyze CSV file structure and sample data"""
    print("=" * 80)
    print("CSV FILE ANALYSIS")
    print("=" * 80)
    
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: File not found: {CSV_FILE}")
        return
    
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Get headers
        headers = reader.fieldnames
        print(f"\n📋 HEADERS FOUND ({len(headers)} columns):")
        for i, header in enumerate(headers, 1):
            print(f"  {i}. {header}")
        
        # Expected headers by our code
        expected_headers = [
            'ServerName', 'Drive', 'Directory', 'FileName', 'Extension',
            'SizeBytes', 'SizeMB', 'SizeGB', 
            'CreatedDate', 'ModifiedDate', 'AccessedDate', 'FileCount'
        ]
        
        print(f"\n✅ EXPECTED HEADERS:")
        for header in expected_headers:
            status = "✓" if header in headers else "✗ MISSING"
            print(f"  {status} {header}")
        
        # Read sample rows
        sample_rows = []
        total_rows = 0
        total_size_gb = 0
        extensions = defaultdict(int)
        servers = set()
        
        for row in reader:
            total_rows += 1
            if len(sample_rows) < 5:
                sample_rows.append(row)
            
            # Collect statistics
            if row.get('SizeGB'):
                try:
                    total_size_gb += float(row.get('SizeGB', 0))
                except:
                    pass
            
            if row.get('Extension'):
                extensions[row.get('Extension')] += 1
            
            if row.get('ServerName'):
                servers.add(row.get('ServerName'))
        
        print(f"\n📊 FILE STATISTICS:")
        print(f"  Total Rows: {total_rows:,}")
        print(f"  Total Size: {total_size_gb:.2f} GB")
        print(f"  Unique Servers: {len(servers)}")
        print(f"  Unique Extensions: {len(extensions)}")
        
        print(f"\n🔝 TOP 10 FILE EXTENSIONS:")
        sorted_ext = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]
        for ext, count in sorted_ext:
            print(f"  {ext or 'NO_EXTENSION'}: {count:,} files")
        
        print(f"\n🖥️  SERVERS FOUND:")
        for server in sorted(servers):
            print(f"  - {server}")
        
        print(f"\n📄 SAMPLE DATA (First 5 rows):")
        for i, row in enumerate(sample_rows, 1):
            print(f"\n  Row {i}:")
            for key in ['ServerName', 'Drive', 'FileName', 'Extension', 'SizeGB', 'ModifiedDate']:
                value = row.get(key, 'N/A')
                print(f"    {key}: {value}")
        
        # Test date parsing
        print(f"\n📅 DATE FORMAT CHECK:")
        if sample_rows:
            for date_field in ['CreatedDate', 'ModifiedDate', 'AccessedDate']:
                sample_date = sample_rows[0].get(date_field)
                if sample_date:
                    print(f"  {date_field}: {sample_date}")
                    # Try parsing
                    try:
                        parsed = datetime.strptime(sample_date, '%Y-%m-%d %H:%M:%S')
                        print(f"    ✓ Parsed successfully as: {parsed}")
                    except:
                        try:
                            parsed = datetime.strptime(sample_date.split('.')[0], '%Y-%m-%d %H:%M:%S')
                            print(f"    ✓ Parsed successfully (with microseconds trimmed)")
                        except Exception as e:
                            print(f"    ✗ Parse failed: {e}")
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    analyze_csv_structure()
