"""
Run Phase 5 against your DB with the same payload Zapier sends (job FH17QU, Barbara Rago).
Usage: python run_phase5_test_local.py
"""
import json
import sys
# Import main only (avoid the module-level "else: output = main(input_data)")
sys.path.insert(0, ".")
from zapier_phase5_FLATTENED_FINAL import main

input_data = {
    "job_uuid": "FH17QU",
    "property_id": "24935",
    "contact_id": "23220",
    "customer_city": "Hemet",
}
print("Running Phase 5 main() with Zapier payload (FH17QU, contact 23220, Hemet)...")
print()
result = main(input_data)
print()
print("=" * 70)
print("FINAL RESULT:")
print(json.dumps(result, indent=2))
