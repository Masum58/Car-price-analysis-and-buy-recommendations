"""
🚗 Enhanced Car Data Cleaning & Combining Script
=================================================
এই script:
- Problem data আর clean sample data দুটোই combine করবে
- Fuel type predict করবে (যদি missing থাকে)
- সব data normalize করবে
- Final master file তৈরি করবে
"""

import json
import pandas as pd
from datetime import datetime
import re

def load_all_sources():
    """সব data source থেকে data load করো"""
    all_cars = []
    
    # 1. Sample data (clean এবং fuel_type আছে)
    try:
        with open('../data/raw/cars_data_sample.json', 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
            for car in sample_data:
                car['data_source'] = 'sample_clean'
            all_cars.extend(sample_data)
            print(f"✓ Sample data (clean): {len(sample_data)} cars")
    except FileNotFoundError:
        print("⚠️ cars_data_sample.json পাওয়া যায়নি")
    except Exception as e:
        print(f"✗ Sample load error: {e}")
    
    # 2. Scraped JSON data (problem data)
    try:
        with open('../data/raw/cars_data.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            for car in json_data:
                car['data_source'] = 'scraped_2dehands'
            all_cars.extend(json_data)
            print(f"✓ Scraped data: {len(json_data)} cars")
    except FileNotFoundError:
        print("⚠️ cars_data.json পাওয়া যায়নি")
    except Exception as e:
        print(f"✗ JSON load error: {e}")
    
    # 3. CSV data (optional)
    try:
        csv_data = pd.read_csv('../data/raw/cars_data.csv', encoding='utf-8')
        csv_cars = csv_data.to_dict('records')
        for car in csv_cars:
            car['data_source'] = 'scraped_csv'
        all_cars.extend(csv_cars)
        print(f"✓ CSV data: {len(csv_cars)} cars")
    except FileNotFoundError:
        print("⚠️ cars_data.csv পাওয়া যায়নি")
    except Exception as e:
        print(f"✗ CSV load error: {e}")
    
    print(f"\n📊 মোট load: {len(all_cars)} cars\n")
    return all_cars

def extract_brand_from_title(title):
    """Title থেকে brand বের করো"""
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
    """
    Fuel type predict করো title আর brand থেকে
    """
    title = str(car.get('title', '')).lower()
    brand = str(car.get('brand', '')).lower()
    
    # Tesla = always electric
    if 'tesla' in brand or 'tesla' in title:
        return 'electric'
    
    # Keywords for fuel types
    if 'hybrid' in title or 'phev' in title or 'plug-in' in title:
        return 'hybrid'
    
    if 'electric' in title or 'ev' in title or 'e-tron' in title:
        return 'electric'
    
    # Diesel indicators
    if any(word in title for word in ['tdi', 'cdi', 'diesel', 'dci', 'hdi', 'crdi']):
        return 'diesel'
    
    # Petrol indicators (most common, so last)
    if any(word in title for word in ['tsi', 'tfsi', 'vti', 'benzine', 'petrol', 'essence']):
        return 'petrol'
    
    # Default: diesel (most common in EU used cars)
    return 'diesel'

def fix_confused_values(car):
    """Price আর Mileage confused হলে fix করো"""
    price = car.get('price_numeric')
    mileage = car.get('mileage_numeric')
    year = car.get('year_numeric')
    
    # Rule 1: Price আর mileage একই + বড়
    if price and mileage and price == mileage and price > 50000:
        car['mileage_numeric'] = price
        car['price_numeric'] = None
        car['needs_manual_review'] = True
        car['fix_applied'] = 'price_mileage_confused'
        return car
    
    # Rule 2: Price unrealistic বড়
    if price and price > 200000 and not mileage:
        car['mileage_numeric'] = price
        car['price_numeric'] = None
        car['needs_manual_review'] = True
        car['fix_applied'] = 'price_too_high'
        return car
    
    # Rule 3: Price খুব ছোট (model number)
    if price and price < 500:
        title = str(car.get('title', ''))
        if str(int(price)) in title:
            car['price_numeric'] = None
            car['needs_manual_review'] = True
            car['fix_applied'] = 'model_as_price'
            return car
    
    # Rule 4: Year confusion
    if year and mileage and year == mileage and year < 10000:
        car['year_numeric'] = None
        car['needs_manual_review'] = True
        car['fix_applied'] = 'year_mileage_confused'
        return car
    
    return car

def validate_car(car):
    """Data validate করো"""
    issues = []
    
    # Year validation
    year = car.get('year_numeric')
    if year:
        if year < 1990 or year > 2025:
            issues.append(f"Invalid year: {year}")
            car['year_numeric'] = None
    
    # Mileage validation
    mileage = car.get('mileage_numeric')
    if mileage:
        if mileage < 0 or mileage > 500000:
            issues.append(f"Invalid mileage: {mileage}")
            car['mileage_numeric'] = None
    
    # Price validation
    price = car.get('price_numeric')
    if price:
        if price < 100 or price > 500000:
            issues.append(f"Suspicious price: {price}")
            car['needs_manual_review'] = True
    
    # Brand extraction
    if not car.get('brand') and car.get('title'):
        extracted_brand = extract_brand_from_title(car['title'])
        if extracted_brand:
            car['brand'] = extracted_brand
            issues.append(f"Brand extracted: {extracted_brand}")
    
    # Fuel type prediction
    if not car.get('fuel_type'):
        predicted_fuel = predict_fuel_type(car)
        car['fuel_type'] = predicted_fuel
        car['fuel_type_predicted'] = True
        issues.append(f"Fuel type predicted: {predicted_fuel}")
    
    if issues:
        car['validation_notes'] = '; '.join(issues)
    
    return car

def clean_car_data(car):
    """একটা car clean করো"""
    
    # 1. Fix confused values
    car = fix_confused_values(car)
    
    # 2. Validate
    car = validate_car(car)
    
    # 3. Handle NaN/None
    for key in ['brand', 'year_numeric', 'mileage_numeric', 'price_numeric', 'fuel_type']:
        if key in car:
            val = car[key]
            if pd.isna(val) or val == '' or val == 'nan':
                car[key] = None
    
    # 4. Add timestamp
    car['cleaned_at'] = datetime.now().isoformat()
    
    return car

def remove_duplicates(cars):
    """Duplicate remove করো"""
    print("🔍 Duplicate খুঁজছি...")
    
    seen = set()
    unique_cars = []
    duplicates = 0
    
    for car in cars:
        title = str(car.get('title', '')).lower().strip()
        year = car.get('year_numeric')
        mileage = car.get('mileage_numeric')
        
        # More robust key
        key = (title, year, mileage)
        
        if key not in seen:
            seen.add(key)
            unique_cars.append(car)
        else:
            duplicates += 1
    
    print(f"✓ {duplicates} duplicate বাদ")
    print(f"✓ Unique: {len(unique_cars)}\n")
    
    return unique_cars

def calculate_derived_fields(car):
    """Extra fields calculate করো"""
    
    # Age
    year = car.get('year_numeric')
    if year:
        car['age'] = 2025 - int(year)
    
    # Is electric/hybrid
    fuel = car.get('fuel_type', '').lower()
    car['is_electric'] = fuel == 'electric'
    car['is_hybrid'] = fuel == 'hybrid'
    car['is_eco'] = fuel in ['electric', 'hybrid']
    
    # Premium brand
    brand = str(car.get('brand', '')).lower()
    car['is_premium'] = brand in ['bmw', 'mercedes', 'audi', 'tesla', 'porsche']
    
    return car

def generate_stats(cars):
    """Statistics তৈরি করো"""
    print("\n" + "="*60)
    print("📈 COMBINED DATA STATISTICS")
    print("="*60 + "\n")
    
    df = pd.DataFrame(cars)
    
    print(f"মোট গাড়ি: {len(df)}")
    
    # By source
    if 'data_source' in df.columns:
        print(f"\nData Sources:")
        for source, count in df['data_source'].value_counts().items():
            print(f"  - {source}: {count} cars")
    
    # Completeness
    print(f"\nData Completeness:")
    print(f"  - Brand: {df['brand'].notna().sum()} ({df['brand'].notna().sum()/len(df)*100:.1f}%)")
    print(f"  - Year: {df['year_numeric'].notna().sum()} ({df['year_numeric'].notna().sum()/len(df)*100:.1f}%)")
    print(f"  - Mileage: {df['mileage_numeric'].notna().sum()} ({df['mileage_numeric'].notna().sum()/len(df)*100:.1f}%)")
    print(f"  - Price: {df['price_numeric'].notna().sum()} ({df['price_numeric'].notna().sum()/len(df)*100:.1f}%)")
    print(f"  - Fuel type: {df['fuel_type'].notna().sum()} ({df['fuel_type'].notna().sum()/len(df)*100:.1f}%)")
    
    # Fuel distribution
    if 'fuel_type' in df.columns:
        print(f"\nFuel Type Distribution:")
        for fuel, count in df['fuel_type'].value_counts().items():
            print(f"  - {fuel}: {count} cars")
    
    # Price range
    valid_prices = df['price_numeric'].dropna()
    if len(valid_prices) > 0:
        print(f"\nPrice Range (valid):")
        print(f"  - Min: €{valid_prices.min():.0f}")
        print(f"  - Max: €{valid_prices.max():.0f}")
        print(f"  - Mean: €{valid_prices.mean():.0f}")
        print(f"  - Median: €{valid_prices.median():.0f}")
    
    # Manual review needed
    if 'needs_manual_review' in df.columns:
        review_count = df['needs_manual_review'].sum()
        print(f"\n⚠️ Manual review needed: {review_count} cars")
    
    print("\n" + "="*60 + "\n")

def main():
    print("\n" + "="*60)
    print("🚗 ENHANCED DATA CLEANING & COMBINING")
    print("="*60 + "\n")
    
    # Load all
    all_cars = load_all_sources()
    
    if not all_cars:
        print("❌ কোনো data নেই!")
        return
    
    # Clean
    print("🧹 Cleaning...")
    cleaned_cars = [clean_car_data(car) for car in all_cars]
    print(f"✓ {len(cleaned_cars)} cars cleaned\n")
    
    # Remove duplicates
    unique_cars = remove_duplicates(cleaned_cars)
    
    # Add derived fields
    print("📊 Calculating extra fields...")
    final_cars = [calculate_derived_fields(car) for car in unique_cars]
    print(f"✓ Done\n")
    
    # Stats
    generate_stats(final_cars)
    
    # Save
    print("💾 Saving...")
    
    # Master JSON
    with open('cars_data_master.json', 'w', encoding='utf-8') as f:
        json.dump(final_cars, f, indent=2, ensure_ascii=False)
    print("✓ cars_data_master.json")
    
    # Master CSV
    df = pd.DataFrame(final_cars)
    df.to_csv('cars_data_master.csv', index=False, encoding='utf-8')
    print("✓ cars_data_master.csv")
    
    # Review file
    review_needed = [
        car for car in final_cars 
        if car.get('needs_manual_review')
    ]
    
    if review_needed:
        with open('cars_needs_review_master.json', 'w', encoding='utf-8') as f:
            json.dump(review_needed, f, indent=2, ensure_ascii=False)
        print(f"⚠️ cars_needs_review_master.json ({len(review_needed)} items)")
    
    # Clean only (ready for API)
    clean_only = [
        car for car in final_cars
        if not car.get('needs_manual_review') and 
           car.get('price_numeric') and
           car.get('mileage_numeric') and
           car.get('year_numeric')
    ]
    
    with open('../data/raw/cars_data_api_ready.json', 'w', encoding='utf-8') as f:
        json.dump(clean_only, f, indent=2, ensure_ascii=False)
    print(f"✅ cars_data_api_ready.json ({len(clean_only)} cars - ready for API)")
    
    print("\n" + "="*60)
    print("✅ DONE!")
    print("="*60)
    print(f"""
Files created:
  📁 cars_data_master.json       - All data combined & cleaned
  📁 cars_data_master.csv        - Same, CSV format
  📁 cars_data_api_ready.json    - Only complete, clean cars
  📁 cars_needs_review_master.json - Needs manual review

Next steps:
  1. Use cars_data_api_ready.json in your API
  2. Review cars_needs_review_master.json
  3. Update prices manually where needed
""")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()