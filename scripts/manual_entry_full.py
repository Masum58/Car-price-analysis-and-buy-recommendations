"""
Manual Car Data Entry Tool - All Client Fields
Browser থেকে দেখে Terminal এ data enter করো - খুবই সহজ!

Usage:
1. cd scripts
2. python manual_entry_full.py
3. Browser: https://www.2dehands.be/l/auto-s/
4. Enter data from browser
"""

import json
import os
from datetime import datetime


def add_car_manually():
    """Add one car with all fields"""
    print("\n" + "="*60)
    print("🚗 MANUAL CAR ENTRY - ALL FIELDS")
    print("="*60 + "\n")
    print("Open 2dehands.be in browser and enter details:\n")
    
    car = {}
    
    # ============================================
    # BASIC INFO
    # ============================================
    print("📋 BASIC INFO:")
    
    car['title'] = input("  Title: ").strip() or None
    car['url'] = input("  URL: ").strip() or None
    car['brand'] = input("  Brand (e.g., BMW): ").strip() or None
    
    # ============================================
    # NUMBERS
    # ============================================
    print("\n💰 NUMBERS:")
    
    # Year
    try:
        year_input = input("  Year (e.g., 2018): ").strip()
        car['year_numeric'] = int(year_input) if year_input else None
    except:
        car['year_numeric'] = None
    
    # Mileage
    try:
        mileage_input = input("  Mileage (e.g., 85000): ").strip()
        car['mileage_numeric'] = int(mileage_input) if mileage_input else None
    except:
        car['mileage_numeric'] = None
    
    # Price
    try:
        price_input = input("  Price (e.g., 15000): ").strip()
        car['price_numeric'] = int(price_input) if price_input else None
    except:
        car['price_numeric'] = None
    
    # ============================================
    # SPECIFICATIONS (Client Requirements)
    # ============================================
    print("\n⚙️  SPECIFICATIONS:")
    
    # 6. Fuel Type ✅
    fuel_input = input("  Fuel (diesel/petrol/electric/hybrid): ").strip().lower()
    if fuel_input in ['diesel', 'petrol', 'electric', 'hybrid']:
        car['fuel_type'] = fuel_input
    else:
        car['fuel_type'] = None
    
    # 1. Gearbox ✅
    gearbox_input = input("  Gearbox (manual/automatic): ").strip().lower()
    if gearbox_input == 'manual':
        car['gearbox'] = "Manual"
    elif gearbox_input == 'automatic':
        car['gearbox'] = "Automatic"
    else:
        car['gearbox'] = None
    
    # 2. First Registration ✅
    car['first_registration'] = input("  First Registration (e.g., 03/2018): ").strip() or None
    
    # 7. Power ✅
    car['power'] = input("  Power (e.g., 150 HP): ").strip() or None
    
    # 9. Seats ✅
    try:
        seats_input = input("  Seats (e.g., 5): ").strip()
        car['seats'] = int(seats_input) if seats_input else None
    except:
        car['seats'] = None
    
    # ============================================
    # 3. IMAGES (Optional) ✅
    # ============================================
    print("\n📸 IMAGES:")
    print("  Enter image URLs (one per line, empty to finish):")
    
    images = []
    i = 1
    while True:
        img_url = input(f"    Image {i}: ").strip()
        if not img_url:
            break
        images.append(img_url)
        i += 1
    
    car['images'] = images
    car['image_count'] = len(images)
    
    # ============================================
    # 4. FEATURES (Optional) ✅
    # ============================================
    print("\n✨ FEATURES:")
    print("  Enter features (one per line, empty to finish):")
    
    features = []
    i = 1
    while True:
        feature = input(f"    Feature {i}: ").strip()
        if not feature:
            break
        features.append(feature)
        i += 1
    
    car['features'] = features
    car['feature_count'] = len(features)
    
    # ============================================
    # 5. SELLER INFO ✅
    # ============================================
    print("\n👤 SELLER INFO:")
    
    seller_info = {}
    seller_info['name'] = input("  Name: ").strip() or None
    seller_info['location'] = input("  Location: ").strip() or None
    seller_info['phone'] = input("  Phone: ").strip() or None
    
    car['seller_info'] = seller_info
    
    # ============================================
    # DESCRIPTION (Optional)
    # ============================================
    print("\n📝 DESCRIPTION (optional):")
    car['description'] = input("  Description: ").strip() or None
    
    # ============================================
    # METADATA
    # ============================================
    car['scraped_at'] = datetime.now().isoformat()
    car['source'] = 'manual_entry'
    
    # ============================================
    # SUMMARY & CONFIRMATION
    # ============================================
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(f"  Title: {car.get('title')}")
    print(f"  Brand: {car.get('brand')}")
    print(f"  Year: {car.get('year_numeric')}")
    print(f"  Price: €{car.get('price_numeric')}")
    print(f"  Gearbox: {car.get('gearbox')}")
    print(f"  Power: {car.get('power')}")
    print(f"  Images: {car.get('image_count')}")
    print(f"  Features: {car.get('feature_count')}")
    print("="*60)
    
    # Confirm
    confirm = input("\nSave this car? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return False
    
    # ============================================
    # SAVE TO PROJECT
    # ============================================
    
    # Get project paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_file = os.path.join(project_root, 'data', 'raw', 'cars_data.json')
    
    # Load existing cars
    cars = []
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                cars = json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load existing data: {e}")
    
    # Add new car
    cars.append(car)
    
    # Save
    try:
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(cars, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved! Total cars: {len(cars)}")
        return True
        
    except Exception as e:
        print(f"\n❌ Save error: {e}")
        return False


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🚗 MANUAL CAR DATA COLLECTION TOOL")
    print("="*60)
    print("\nUSAGE:")
    print("  1. Open browser: https://www.2dehands.be/l/auto-s/")
    print("  2. Find a car listing")
    print("  3. Enter details here")
    print("  4. Repeat for more cars")
    print("="*60 + "\n")
    
    total_added = 0
    
    while True:
        if add_car_manually():
            total_added += 1
            print(f"\n✅ Total cars added this session: {total_added}")
        
        # Ask for another
        again = input("\nAdd another car? (y/n): ").strip().lower()
        if again != 'y':
            break
    
    # ============================================
    # SESSION COMPLETE
    # ============================================
    print("\n" + "="*60)
    print(f"✅ SESSION COMPLETE - Added {total_added} car(s)")
    print("="*60)
    
    if total_added > 0:
        print("\n🎯 Next Steps:")
        print("  1. python clean_real_data_only.py")
        print("  2. python show_data_summary.py")
        print("="*60 + "\n")
    else:
        print("\n💡 Tip: Run again anytime to add more cars!")
        print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
        print("Data saved up to last completed car.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")