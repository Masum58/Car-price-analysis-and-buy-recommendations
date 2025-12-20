"""
Show the car that needs review
"""
import json

print("\n" + "="*60)
print("🚗 CAR NEEDING REVIEW")
print("="*60 + "\n")

try:
    with open('../data/raw/cars_data_real_needs_review.json', 'r') as f:
        cars = json.load(f)
    
    if len(cars) == 0:
        print("✅ No cars need review! All good!")
    else:
        for i, car in enumerate(cars, 1):
            print(f"Car #{i}:")
            print(f"   Title: {car.get('title', 'N/A')}")
            print(f"   Brand: {car.get('brand', '❌ MISSING')}")
            print(f"   Year: {car.get('year_numeric', '❌ MISSING')}")
            print(f"   Mileage: {car.get('mileage_numeric', '❌ MISSING')} km")
            print(f"   Price: €{car.get('price_numeric', '❌ MISSING')}")
            
            # What's wrong?
            issues = []
            if not car.get('brand'):
                issues.append("No brand")
            if not car.get('price_numeric'):
                issues.append("No price")
            if not car.get('year_numeric'):
                issues.append("No year")
            if not car.get('mileage_numeric'):
                issues.append("No mileage")
            
            print(f"\n   ⚠️  Issues: {', '.join(issues)}")
            print()
    
    print("="*60 + "\n")

except Exception as e:
    print(f"❌ Error: {e}\n")