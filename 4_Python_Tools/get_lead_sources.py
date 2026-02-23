import csv
import os

INPUT_FILE = 'Workiz_Export_Raw.csv'

def extract_unique_sources():
    print(f"[INFO] Scanning '{INPUT_FILE}' for unique Lead Sources...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] File not found.")
        return

    sources = set()
    try:
        with open(INPUT_FILE, mode='r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row.get('JobSource', '').strip()
                if source:
                    sources.add(source)
        
        print("\n[SUCCESS] Found the following unique Lead Sources:")
        print("--- COPY THE LIST BELOW ---")
        
        for source in sorted(list(sources)):
            print(source)
            
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == '__main__':
    extract_unique_sources()