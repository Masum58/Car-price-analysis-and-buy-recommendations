"""
🌐 Clean ONLY Real Scraped Data (No Sample Data)
=================================================
For production use with real client data
"""

import json
import pandas as pd
from datetime import datetime
import os

def load_real_scraped_data_only():
    """Load ONLY real scraped data, exclude sample data"""
    all_cars = []
    
    print("📂 Loading REAL scraped data only...\n")
    
    # 1. JSON scraped data
    try:
        with open('../data/raw/cars_data.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            for car in json_data:
                car['data_source'] = 'real_scraped_2dehands'
            all_cars.extend(json_data)
            print(f"✓ cars_data.json: {len(json_data)} real cars")
    except FileNotFoundError:
        print("⚠️  cars_data.json not found")
    
    # 2. CSV scraped data
    try:
        csv_data = pd.read_csv('../data/raw/cars_data.csv', encoding='utf-8')
        csv_cars = csv_data.to_dict('records')
        for car in csv_cars:
            car['data_source'] = 'real_scraped_csv'
        all_cars.extend(csv_cars)
        print(f"✓ cars_data.csv: {len(csv_cars)} real cars")
    except FileNotFoundError:
        print("⚠️  cars_data.csv not found")
    
    # IMPORTANT: We're NOT loading cars_data_sample.json
    print("\n⚠️  Excluding sample data (cars_data_sample.json)")
    
    if not all_cars:
        print("\n❌ No real scraped data found!")
        print("   Run: python scrape_cars.py")
        return None
    
    print(f"\n📊 Total REAL cars loaded: {len(all_cars)}\n")
    return all_cars

def extract_brand_from_title(title):
    """Extract brand from title"""
    if not title or not isinstance(title, str):
        return None
    
    brands = [
        'BMW', 'Mercedes', 'Audi', 'Volkswagen', 'VW', 'Renault', 
        'Peugeot', 'Citroen', 'Fiat', 'Ford', 'Opel', 'Toyota',
        'Honda', 'Nissan', 'Mazda', 'Volvo', 'Seat', 'Skoda',
        'Hyundai', 'Kia', 'Tesla', 'Porsche', 'Dodge', 'Ranger'
    ]
    
    title_upper = title.upper()
    for brand in brands:
        if brand.upper() in title_upper:
            return brand
    
    return None

def predict_fuel_type(car):
    """Predict fuel type from title"""
    title = str(car.get('title', '')).lower()
    brand = str(car.get('brand', '')).lower()
    
    if 'tesla' in brand or 'tesla' in title:
        return 'electric'
    
    if 'hybrid' in title or 'phev' in title:
        return 'hybrid'
    
    if 'electric' in title or 'ev' in title:
        return 'electric'
    
    if any(word in title for word in ['tdi', 'cdi', 'diesel', 'dci', 'hdi']):
        return 'diesel'
    
    if any(word in title for word in ['tsi', 'tfsi', 'vti', 'benzine', 'petrol']):
        return 'petrol'
    
    return 'diesel'  # Most common in Europe

def fix_confused_values(car):
    """Fix price/mileage confusion"""
    price = car.get('price_numeric')
    mileage = car.get('mileage_numeric')
    year = car.get('year_numeric')
    
    # Price and mileage same + high value
    if price and mileage and price == mileage and price > 50000:
        car['mileage_numeric'] = price
        car['price_numeric'] = None
        car['needs_manual_review'] = True
        car['fix_note'] = 'price_mileage_confused'
        return car
    
    # Price too high, no mileage
    if price and price > 200000 and not mileage:
        car['mileage_numeric'] = price
        car['price_numeric'] = None
        car['needs_manual_review'] = True
        car['fix_note'] = 'price_too_high_moved_to_mileage'
        return car
    
    # Very low price (likely model number)
    if price and price < 500:
        title = str(car.get('title', ''))
        if str(int(price)) in title:
            car['price_numeric'] = None
            car['needs_manual_review'] = True
            car['fix_note'] = 'price_is_model_number'
            return car
    
    return car

def validate_and_clean_car(car):
    """Validate and clean car data"""
    
    # Fix confused values
    car = fix_confused_values(car)
    
    # Extract brand if missing
    if not car.get('brand'):
        brand = extract_brand_from_title(car.get('title', ''))
        if brand:
            car['brand'] = brand
    
    # Predict fuel type if missing
    if not car.get('fuel_type'):
        car['fuel_type'] = predict_fuel_type(car)
        car['fuel_type_predicted'] = True
    
    # Validate year
    year = car.get('year_numeric')
    if year and (year < 1990 or year > 2025):
        car['year_numeric'] = None
    
    # Validate mileage
    mileage = car.get('mileage_numeric')
    if mileage and (mileage < 0 or mileage > 500000):
        car['mileage_numeric'] = None
    
    # Validate price
    price = car.get('price_numeric')
    if price and (price < 100 or price > 500000):
        car['needs_manual_review'] = True
    
    # Handle NaN
    for key in ['brand', 'year_numeric', 'mileage_numeric', 'price_numeric', 'fuel_type']:
        if key in car:
            val = car[key]
            if pd.isna(val) or val == '' or val == 'nan':
                car[key] = None
    
    car['cleaned_at'] = datetime.now().isoformat()
    
    return car

def remove_duplicates(cars):
    """Remove duplicate entries"""
    print("🔍 Removing duplicates...")
    
    seen = set()
    unique_cars = []
    duplicates = 0
    
    for car in cars:
        title = str(car.get('title', '')).lower().strip()
        year = car.get('year_numeric')
        mileage = car.get('mileage_numeric')
        
        key = (title, year, mileage)
        
        if key not in seen:
            seen.add(key)
            unique_cars.append(car)
        else:
            duplicates += 1
    
    print(f"✓ Removed {duplicates} duplicates")
    print(f"✓ Unique cars: {len(unique_cars)}\n")
    
    return unique_cars

def calculate_derived_fields(car):
    """Calculate extra fields"""
    
    # Age
    year = car.get('year_numeric')
    if year:
        car['age'] = 2025 - int(year)
    
    # Eco flags
    fuel = car.get('fuel_type', '').lower()
    car['is_electric'] = fuel == 'electric'
    car['is_hybrid'] = fuel == 'hybrid'
    car['is_eco'] = fuel in ['electric', 'hybrid']
    
    # Premium brand
    brand = str(car.get('brand', '')).lower()
    car['is_premium'] = brand in ['bmw', 'mercedes', 'audi', 'tesla', 'porsche']
    
    return car

def generate_stats(cars):
    """Show statistics"""
    print("\n" + "="*70)
    print("📊 REAL SCRAPED DATA STATISTICS")
    print("="*70 + "\n")
    
    df = pd.DataFrame(cars)
    
    print(f"Total Real Cars: {len(df)}")
    
    # Completeness
    print(f"\nData Completeness:")
    for field in ['brand', 'year_numeric', 'mileage_numeric', 'price_numeric', 'fuel_type']:
        complete = df[field].notna().sum()
        pct = (complete / len(df)) * 100
        print(f"  - {field:20s}: {complete:3d}/{len(df)} ({pct:.1f}%)")
    
    # Needs review
    if 'needs_manual_review' in df.columns:
        review = df['needs_manual_review'].sum()
        print(f"\n⚠️  Needs manual review: {review} cars")
    
    # Price stats
    valid_prices = df['price_numeric'].dropna()
    if len(valid_prices) > 0:
        print(f"\n💰 Price Range:")
        print(f"  - Min: €{valid_prices.min():,.0f}")
        print(f"  - Max: €{valid_prices.max():,.0f}")
        print(f"  - Avg: €{valid_prices.mean():,.0f}")
    
    # Brand distribution
    if 'brand' in df.columns:
        brands = df['brand'].value_counts()
        print(f"\n🏷️  Top Brands:")
        for brand, count in brands.head(5).items():
            print(f"  - {brand}: {count} cars")
    
    print("\n" + "="*70 + "\n")

def main():
    print("\n" + "="*70)
    print("🌐 CLEAN REAL SCRAPED DATA ONLY")
    print("="*70 + "\n")
    
    # Load real data only
    cars = load_real_scraped_data_only()
    
    if not cars:
        print("\n❌ Please run scraper first: python scrape_cars.py")
        return
    
    # Clean
    print("🧹 Cleaning data...")
    cleaned = [validate_and_clean_car(car) for car in cars]
    print(f"✓ {len(cleaned)} cars cleaned\n")
    
    # Remove duplicates
    unique = remove_duplicates(cleaned)
    
    # Add derived fields
    print("📊 Adding derived fields...")
    final = [calculate_derived_fields(car) for car in unique]
    print(f"✓ Done\n")
    
    # Stats
    generate_stats(final)
    
    # Save files
    print("💾 Saving files...")
    
    # 1. Real data only (all)
    with open('../data/raw/cars_data_real_all.json', 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print("✓ cars_data_real_all.json (all real cars)")
    
    # 2. API-ready (complete data only)
    api_ready = [
        car for car in final
        if car.get('brand') and
           car.get('year_numeric') and
           car.get('mileage_numeric') and
           car.get('price_numeric') and
           not car.get('needs_manual_review')
    ]
    
    with open('../data/raw/cars_data_real_api_ready.json', 'w', encoding='utf-8') as f:
        json.dump(api_ready, f, indent=2, ensure_ascii=False)
    print(f"✓ cars_data_real_api_ready.json ({len(api_ready)} clean cars)")
    
    # 3. Needs review
    needs_review = [car for car in final if car.get('needs_manual_review')]
    
    if needs_review:
        with open('../data/raw/cars_data_real_needs_review.json', 'w', encoding='utf-8') as f:
            json.dump(needs_review, f, indent=2, ensure_ascii=False)
        print(f"⚠️  cars_data_real_needs_review.json ({len(needs_review)} cars)")
    
    # 4. CSV
    df = pd.DataFrame(api_ready)
    df.to_csv('../data/raw/cars_data_real_api_ready.csv', index=False, encoding='utf-8')
    print("✓ cars_data_real_api_ready.csv")
    
    print("\n" + "="*70)
    print("✅ REAL DATA CLEANING COMPLETE!")
    print("="*70)
    print(f"""
📊 Summary:
   Total real cars scraped: {len(final)}
   API-ready (clean): {len(api_ready)}
   Needs review: {len(needs_review)}
   
📁 Files created:
   ✓ cars_data_real_all.json (all real cars)
   ✓ cars_data_real_api_ready.json (production use) ⭐
   ✓ cars_data_real_api_ready.csv
   {'✓ cars_data_real_needs_review.json' if needs_review else ''}

🎯 Next step:
   Update ai_calculations.py to use:
   '../data/raw/cars_data_real_api_ready.json'
""")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()