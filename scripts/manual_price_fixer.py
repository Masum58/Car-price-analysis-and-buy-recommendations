"""
Manual price fixer - helps you update prices
"""
import json

print("\n" + "="*70)
print("🔧 MANUAL PRICE FIXER")
print("="*70 + "\n")

# Load needs review cars
with open('../data/raw/cars_data_real_needs_review.json', 'r', encoding='utf-8') as f:
    review_cars = json.load(f)

# Load original data
with open('../data/raw/cars_data.json', 'r', encoding='utf-8') as f:
    all_cars = json.load(f)

print(f"Found {len(review_cars)} cars needing price fix\n")

fixed_count = 0

for review_car in review_cars:
    title = review_car.get('title', '')[:60]
    url = review_car.get('url', 'No URL')
    
    # Skip if no brand (too incomplete)
    if not review_car.get('brand'):
        print(f"⏭️  Skipping: {title} (no brand)\n")
        continue
    
    print(f"🚗 {title}")
    print(f"   Year: {review_car.get('year_numeric')}")
    print(f"   Mileage: {review_car.get('mileage_numeric')} km")
    print(f"   URL: {url[:60]}...")
    
    # Ask for price
    price_input = input(f"\n   💰 Enter price (or press Enter to skip): €")
    
    if price_input.strip():
        try:
            price = float(price_input.replace(',', '').replace(' ', ''))
            
            # Update in main data
            for car in all_cars:
                if (car.get('title') == review_car.get('title') and
                    car.get('year_numeric') == review_car.get('year_numeric')):
                    car['price_numeric'] = price
                    print(f"   ✅ Updated price to €{price:,.0f}")
                    fixed_count += 1
                    break
        except:
            print(f"   ❌ Invalid price, skipping")
    
    print()

# Save updated data
if fixed_count > 0:
    with open('../data/raw/cars_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_cars, f, indent=2, ensure_ascii=False)
    
    print("="*70)
    print(f"✅ Updated {fixed_count} cars with prices!")
    print("="*70)
    print("\nNext steps:")
    print("1. python clean_real_data_only.py")
    print("2. python verify_real_data.py")
    print("="*70 + "\n")
else:
    print("No cars updated.\n")