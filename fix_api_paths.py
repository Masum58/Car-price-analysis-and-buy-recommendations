"""
Fix paths in app files
"""
import os

files_to_fix = [
    'app/ai_calculations.py',
    'app/routes.py',
]

replacements = {
    "'cars_data_real_api_ready.json'": "'../data/raw/cars_data_real_api_ready.json'",
    '"cars_data_real_api_ready.json"': '"../data/raw/cars_data_real_api_ready.json"',
    "'cars_data.json'": "'../data/raw/cars_data.json'",
    '"cars_data.json"': '"../data/raw/cars_data.json"',
}

print("\n🔧 Fixing API file paths...\n")

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"⏭️  {filepath} not found")
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
        else:
            print(f"⏭️  {filepath} (no changes)")
    
    except Exception as e:
        print(f"❌ Error in {filepath}: {e}")

print("\n✅ Done! Restart API:\n   uvicorn app.main:app --reload\n")