"""
Quick summary of all data files
"""
import json
import os

files = {
    'Real Scraped (Raw)': '../data/raw/cars_data.json',
    'Real API Ready': '../data/raw/cars_data_real_api_ready.json',
    'Real All': '../data/raw/cars_data_real_all.json',
    'Real Needs Review': '../data/raw/cars_data_real_needs_review.json',
    'Mixed (Old)': '../data/raw/cars_data_api_ready.json',
    'Sample (Fake)': '../data/raw/cars_data_sample.json'
}

print("\n" + "="*60)
print("📊 DATA FILES SUMMARY")
print("="*60 + "\n")

for name, filepath in files.items():
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            count = len(data)
            
            # Check data source
            sources = set(car.get('data_source', 'unknown') for car in data)
            
            print(f"{name:25s}: {count:3d} cars")
            print(f"{'':25s}  Sources: {', '.join(sources)}")
            print()
        except:
            print(f"{name:25s}: Error reading")
    else:
        print(f"{name:25s}: Not found")

print("="*60)
print("\n✅ Use for production: cars_data_real_api_ready.json")
print("⚠️ Avoid: cars_data_api_ready.json (mixed data)")
print("\n" + "="*60 + "\n")