"""
Fix paths in ALL scripts
"""
import os
import glob

print("\n" + "="*60)
print("🔧 Fixing All Script Paths")
print("="*60 + "\n")

# All path replacements needed
replacements = {
    # Single quotes
    "'cars_data.json'": "'../data/raw/cars_data.json'",
    "'cars_data.csv'": "'../data/raw/cars_data.csv'",
    "'cars_data_real_api_ready.json'": "'../data/raw/cars_data_real_api_ready.json'",
    "'cars_data_real_api_ready.csv'": "'../data/raw/cars_data_real_api_ready.csv'",
    "'cars_data_real_all.json'": "'../data/raw/cars_data_real_all.json'",
    "'cars_data_real_needs_review.json'": "'../data/raw/cars_data_real_needs_review.json'",
    "'cars_data_api_ready.json'": "'../data/raw/cars_data_api_ready.json'",
    "'cars_data_sample.json'": "'../data/raw/cars_data_sample.json'",
    "'ml_model.joblib'": "'../data/ml_models/ml_model.joblib'",
    "'ml_model_encodings.json'": "'../data/ml_models/ml_model_encodings.json'",
    "'progress_log.json'": "'../logs/progress_log.json'",
    
    # Double quotes
    '"cars_data.json"': '"../data/raw/cars_data.json"',
    '"cars_data_real_api_ready.json"': '"../data/raw/cars_data_real_api_ready.json"',
    '"cars_data_real_all.json"': '"../data/raw/cars_data_real_all.json"',
    '"cars_data_real_needs_review.json"': '"../data/raw/cars_data_real_needs_review.json"',
}

# Fix all .py files in current directory
fixed_files = []
for file in glob.glob('*.py'):
    if file == 'fix_all_scripts.py':
        continue  # Skip self
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Apply all replacements
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
        
        # Save if changed
        if content != original:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file}")
            fixed_files.append(file)
        else:
            print(f"⏭️  Skipped: {file} (no changes needed)")
    
    except Exception as e:
        print(f"❌ Error in {file}: {e}")

print("\n" + "="*60)
print(f"✅ Fixed {len(fixed_files)} files!")
print("="*60)

if fixed_files:
    print("\nFixed files:")
    for f in fixed_files:
        print(f"  • {f}")

print("\n🎯 Now test:")
print("  python show_data_summary.py")
print("  python verify_real_data.py")
print("\n" + "="*60 + "\n")