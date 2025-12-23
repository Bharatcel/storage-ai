"""
Test CSV mapping with the new format
"""
import csv
from datetime import datetime

CSV_FILE = r"c:\Users\sharma.25274\Downloads\DC1IOPSUAT-20231227-2004-DriveFileDetails.csv"

def test_mapping():
    print("=" * 80)
    print("TESTING CSV COLUMN MAPPING")
    print("=" * 80)
    
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Test first 5 rows
        for i, row in enumerate(reader, 1):
            if i > 5:
                break
            
            print(f"\n📄 Row {i}:")
            print(f"  ServerName: {row.get('ServerName') or row.get('Hostname')}")
            print(f"  Drive: {row.get('Drive') or row.get('DriveLetter')}")
            print(f"  FileName: {row.get('FileName')}")
            print(f"  Extension: {row.get('Extension') or row.get('FileType')}")
            print(f"  Directory: {(row.get('Directory') or row.get('Path'))[:50]}...")
            
            # Calculate sizes
            size_kb_str = row.get('FileSizeKB', '0') or '0'
            size_kb = float(size_kb_str.replace(',', ''))
            size_mb = size_kb / 1024
            size_gb = size_kb / (1024 * 1024)
            print(f"  Size: {size_kb:,.2f} KB = {size_mb:.2f} MB = {size_gb:.6f} GB")
            
            # Test dates
            created = row.get('CreatedDate') or row.get('CreatedTime')
            modified = row.get('ModifiedDate') or row.get('LastModified')
            accessed = row.get('AccessedDate') or row.get('LastAccessed')
            
            print(f"  Created: {created}")
            print(f"  Modified: {modified}")
            print(f"  Accessed: {accessed}")
            
            # Try parsing dates
            if modified:
                try:
                    # Try format: 12/27/2023 8:04:45 PM
                    if '/' in modified:
                        parsed = datetime.strptime(modified, '%m/%d/%Y %I:%M:%S %p')
                        print(f"    ✓ Parsed as: {parsed}")
                    else:
                        parsed = datetime.strptime(modified.split('.')[0], '%Y-%m-%d %H:%M:%S')
                        print(f"    ✓ Parsed as: {parsed}")
                except Exception as e:
                    print(f"    ⚠️  Parse error: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_mapping()
