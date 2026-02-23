import csv
import os

INPUT_FILE = 'Workiz_Export_Raw.csv'

def extract_unique_job_types():
    print(f"[INFO] Scanning '{INPUT_FILE}' for unique Job Types...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] File not found. Please ensure '{INPUT_FILE}' is in the same directory.")
        return

    job_types = set()
    try:
        with open(INPUT_FILE, mode='r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                job_type = row.get('JobType', '').strip()
                if job_type: # Only add if it's not an empty string
                    job_types.add(job_type)
        
        print("\n[SUCCESS] Found the following unique Job Types:")
        print("--- COPY THE LIST BELOW ---")
        
        # Print sorted list for easy copy-pasting
        for job_type in sorted(list(job_types)):
            print(job_type)
            
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == '__main__':
    extract_unique_job_types()