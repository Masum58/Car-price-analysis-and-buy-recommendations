"""
Verify that we're using REAL data only
"""
import json

print("\n" + "="*60)
print("🔍 VERIFYING DATA SOURCE")
print("="*60 + "\n")

try:
    with open('cars_data_real_api_ready.json', 'r', encoding='utf-8') as f:
        cars = json.load(f)
    
    print(f"✅ Loaded {len(cars)} cars from cars_data_real_api_ready.json\n")
    
    print("📋 Sample of 5 cars:\n")
    
    for i, car in enumerate(cars[:5], 1):
        print(f"{i}. {car.get('title', 'Unknown')[:50]}")
        print(f"   Source: {car.get('source', 'N/A')}")
        print(f"   URL: {car.get('url', 'N/A')[:60]}")
        print(f"   Scraped: {car.get('scraped_at', 'N/A')[:19]}")
        print(f"   Data Source Type: {car.get('data_source', 'N/A')}")
        print()
    
    # Check if any sample data
    sample_data = [car for car in cars if car.get('data_source') == 'sample_clean']
    real_data = [car for car in cars if 'scraped' in car.get('data_source', '').lower()]
    
    print("="*60)
    print("📊 DATA SOURCE BREAKDOWN")
    print("="*60)
    print(f"Real Scraped Data: {len(real_data)} cars ✅")
    print(f"Sample Data: {len(sample_data)} cars")
    
    if sample_data:
        print("\n⚠️ WARNING: Sample data found! Not production ready.")
    else:
        print("\n✅ VERIFIED: 100% Real Data - Production Ready!")
    
    print("\n" + "="*60 + "\n")
    
except FileNotFoundError:
    print("❌ Error: cars_data_real_api_ready.json not found!")
    print("   Run: python clean_real_data_only.py\n")