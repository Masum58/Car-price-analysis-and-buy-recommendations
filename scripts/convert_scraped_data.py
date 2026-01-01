"""
Convert AutoScout24 Scraped Data to API Format
Fixes: Price negative, analysis issues, recommendation problems

Input: scrapers/output.json (from autoscout24_working_scraper.py)
Output: data/raw/cars_data.json (API-compatible)
"""

import json
import os
import re
from datetime import datetime


def extract_price(price_str):
    """Extract numeric price from string like '€ 3,950'"""
    if not price_str:
        return None
    
    try:
        # Remove all non-digits
        numbers = re.findall(r'\d+', price_str.replace(',', '').replace('.', ''))
        if numbers:
            return int(numbers[0])
        return None
    except:
        return None


def extract_mileage(mileage_str):
    """Extract numeric mileage from '239,000 km'"""
    if not mileage_str:
        return None
    
    try:
        numbers = re.findall(r'\d+', mileage_str.replace(',', '').replace('.', ''))
        if numbers:
            km = int(numbers[0])
            # If mileage is in range 1-999, it's likely in thousands
            if km < 1000:
                km *= 1000
            return km
        return None
    except:
        return None


def extract_year(registration_str):
    """Extract year from '11/2015'"""
    if not registration_str:
        return None
    
    try:
        # Match 4-digit year
        match = re.search(r'(20\d{2}|19\d{2})', registration_str)
        if match:
            return int(match.group(1))
        return None
    except:
        return None


def extract_power(power_str):
    """Extract power in kW from '55 kW (75 hp)'"""
    if not power_str:
        return None
    
    try:
        # Extract kW value
        match = re.search(r'(\d+)\s*kW', power_str)
        if match:
            return int(match.group(1))
        return None
    except:
        return None


def extract_brand(title):
    """Extract brand from car title"""
    if not title:
        return None
    
    title_lower = title.lower()
    
    brands = {
        'audi': 'Audi',
        'bmw': 'BMW',
        'mercedes': 'Mercedes-Benz',
        'volkswagen': 'Volkswagen',
        'vw': 'VW',
        'toyota': 'Toyota',
        'hyundai': 'Hyundai',
        'kia': 'Kia',
        'volvo': 'Volvo',
        'renault': 'Renault',
        'citroen': 'Citroen',
        'peugeot': 'Peugeot',
        'ford': 'Ford',
        'opel': 'Opel',
        'seat': 'SEAT',
        'skoda': 'Skoda',
        'mazda': 'Mazda',
        'honda': 'Honda',
        'nissan': 'Nissan',
        'fiat': 'Fiat',
        'lancia': 'Lancia',
        'alfa romeo': 'Alfa Romeo',
        'suzuki': 'Suzuki'
    }
    
    for key, value in brands.items():
        if key in title_lower:
            return value
    
    return None


def normalize_fuel_type(fuel_str):
    """Normalize fuel type to lowercase"""
    if not fuel_str:
        return None
    
    fuel_lower = fuel_str.lower()
    
    if 'diesel' in fuel_lower:
        return 'diesel'
    elif any(w in fuel_lower for w in ['gasoline', 'benzine', 'petrol']):
        return 'petrol'
    elif 'electric' in fuel_lower or 'elektrisch' in fuel_lower:
        return 'electric'
    elif 'hybrid' in fuel_lower:
        return 'hybrid'
    else:
        return fuel_lower


def convert_scraped_car(scraped_car):
    """Convert one scraped car to API format"""
    
    # Extract basic data
    basic = scraped_car.get('Basic_Data', {})
    history = scraped_car.get('Vehicle_History', {})
    technical = scraped_car.get('Technical_Data', {})
    energy = scraped_car.get('Energy_Consumption', {})
    
    # Build API-compatible car
    api_car = {
        # Basic fields
        "title": scraped_car.get('car_title'),
        "subtitle": scraped_car.get('car_subtitle'),
        "url": scraped_car.get('details_url'),
        
        # Numeric fields (CRITICAL for ML)
        "price_numeric": extract_price(scraped_car.get('price')),
        "mileage_numeric": extract_mileage(history.get('Mileage')),
        "year_numeric": extract_year(history.get('First_registration')),
        "power_kw": extract_power(technical.get('Power')),
        
        # Brand & fuel (CRITICAL for recommendations)
        "brand": extract_brand(scraped_car.get('car_title')),
        "fuel_type": normalize_fuel_type(energy.get('Fuel_type')),
        
        # Important specs
        "gearbox": technical.get('Gearbox'),
        "first_registration": history.get('First_registration'),
        "seats": basic.get('Seats'),
        "doors": basic.get('Doors'),
        
        # Images & features
        "images": scraped_car.get('all_images', []),
        "image_count": len(scraped_car.get('all_images', [])),
        
        # Seller info
        "seller_info": scraped_car.get('seller_info', {}),
        
        # Full original data (for reference)
        "raw_data": {
            "Basic_Data": basic,
            "Vehicle_History": history,
            "Technical_Data": technical,
            "Energy_Consumption": energy,
            "Colour_and_Upholstery": scraped_car.get('Colour_and_Upholstery', {})
        },
        
        # Metadata
        "scraped_at": scraped_car.get('scraped_at') or datetime.now().isoformat(),
        "source": "autoscout24_working_scraper",
        "data_version": "2.0"
    }
    
    return api_car


def validate_car(car):
    """Check if car has minimum required fields"""
    required = ['price_numeric', 'year_numeric', 'brand']
    
    for field in required:
        if not car.get(field):
            return False, f"Missing {field}"
    
    # Price should be reasonable
    if car['price_numeric'] < 100 or car['price_numeric'] > 1000000:
        return False, "Price out of range"
    
    # Year should be reasonable
    if car['year_numeric'] < 1990 or car['year_numeric'] > 2026:
        return False, "Year out of range"
    
    return True, "OK"


def convert_all_data(input_file, output_file):
    """Main conversion function"""
    
    print("\n" + "="*60)
    print("🔄 Converting AutoScout24 Data to API Format")
    print("="*60 + "\n")
    
    # Read scraped data
    print(f"📂 Reading: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)
    
    print(f"✅ Loaded {len(scraped_data)} scraped cars\n")
    
    # Load existing cars (to avoid duplicates)
    existing_cars = []
    existing_urls = set()
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_cars = json.load(f)
            existing_urls = {c.get('url') for c in existing_cars if c.get('url')}
        print(f"📂 Found {len(existing_cars)} existing cars in API\n")
    
    # Convert each car
    print("🔄 Converting cars...")
    print("-" * 60)
    
    converted_cars = []
    skipped = 0
    errors = 0
    
    for i, scraped_car in enumerate(scraped_data, 1):
        url = scraped_car.get('details_url')
        title = scraped_car.get('car_title', 'Unknown')[:40]
        
        # Skip if already exists
        if url in existing_urls:
            print(f"[{i:2d}] ⏭️  {title} - Already exists")
            skipped += 1
            continue
        
        # Convert
        try:
            api_car = convert_scraped_car(scraped_car)
            
            # Validate
            is_valid, reason = validate_car(api_car)
            
            if is_valid:
                converted_cars.append(api_car)
                price = api_car.get('price_numeric', 0)
                year = api_car.get('year_numeric', '?')
                brand = api_car.get('brand', '?')
                print(f"[{i:2d}] ✅ {title} - {brand} {year} €{price:,}")
            else:
                print(f"[{i:2d}] ⚠️  {title} - Invalid: {reason}")
                errors += 1
        
        except Exception as e:
            print(f"[{i:2d}] ❌ {title} - Error: {e}")
            errors += 1
    
    print("-" * 60 + "\n")
    
    # Combine with existing
    all_cars = existing_cars + converted_cars
    
    # Save
    print(f"💾 Saving to: {output_file}")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_cars, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("✅ CONVERSION COMPLETE!")
    print("="*60)
    print(f"  Total scraped: {len(scraped_data)}")
    print(f"  Converted: {len(converted_cars)}")
    print(f"  Skipped (duplicates): {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total in API: {len(all_cars)}")
    print("="*60)
    
    # Show sample
    if converted_cars:
        print("\n📊 Sample converted car:")
        print("-" * 60)
        sample = converted_cars[0]
        print(f"Title: {sample.get('title')}")
        print(f"Brand: {sample.get('brand')}")
        print(f"Year: {sample.get('year_numeric')}")
        print(f"Price: €{sample.get('price_numeric'):,}")
        print(f"Mileage: {sample.get('mileage_numeric'):,} km")
        print(f"Fuel: {sample.get('fuel_type')}")
        print(f"Gearbox: {sample.get('gearbox')}")
        print("-" * 60)
    
    print("\n🎯 Next steps:")
    print("  1. Test API: uvicorn app.main:app --reload")
    print("  2. Verify: http://localhost:8000/cars/list")
    print("  3. Test analysis: http://localhost:8000/test-analysis/")
    print("="*60 + "\n")


if __name__ == "__main__":
    # File paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    input_file = os.path.join(project_root, 'scrapers', 'output.json')
    output_file = os.path.join(project_root, 'data', 'raw', 'cars_data.json')
    
    # Convert
    convert_all_data(input_file, output_file)