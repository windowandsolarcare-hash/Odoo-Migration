# Quick test to actually mark Bev's opportunity as Won
from phase3d_mark_won import mark_opportunity_won

print("\n" + "="*70)
print("TESTING: Mark Opportunity #41 as Won")
print("="*70 + "\n")

result = mark_opportunity_won(41)

print("\n" + "="*70)
print("RESULT:")
print("="*70)
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
print("="*70 + "\n")

if result['success']:
    print("✅ Go check Odoo - opportunity should now be marked as Won!")
else:
    print("❌ Error occurred - check the details above")
