"""
Manual Car Data Entry Tool - AutoScout24 Version
Browser থেকে দেখে Terminal এ data enter করো - খুবই সহজ!

Usage:
1. cd scripts
2. python manual_entry_autoscout.py
3. Browser: https://www.autoscout24.be/ (or .de)
4. Enter data from browser
"""

import json
import os
from datetime import datetime


def add_car_manually():
    """Add one car with all fields"""
    print("\n" + "="*60)
    print("🚗 MANUAL CAR ENTRY - AutoScout24")
    print("="*60 + "\n")
    print("Open AutoScout24 in browser and enter details:\n")
    
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
        mileage_input = input("  Mileage in km (e.g., 85000): ").strip()
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
    print("  Fuel options: diesel, petrol, electric, hybrid")
    fuel_input = input("  Fuel Type: ").strip().lower()
    if fuel_input in ['diesel', 'petrol', 'electric', 'hybrid', 'benzin', 'benzine']:
        if fuel_input in ['benzin', 'benzine']:
            car['fuel_type'] = 'petrol'
        else:
            car['fuel_type'] = fuel_input
    else:
        car['fuel_type'] = None
    
    # 1. Gearbox ✅
    print("  Gearbox options: manual, automatic")
    gearbox_input = input("  Gearbox: ").strip().lower()
    if 'manual' in gearbox_input or 'handgeschakeld' in gearbox_input or 'schaltgetriebe' in gearbox_input:
        car['gearbox'] = "Manual"
    elif 'automatic' in gearbox_input or 'automaat' in gearbox_input or 'automatik' in gearbox_input:
        car['gearbox'] = "Automatic"
    else:
        car['gearbox'] = None
    
    # 2. First Registration ✅
    car['first_registration'] = input("  First Registration (e.g., 03/2018): ").strip() or None
    
    # 7. Power ✅
    car['power'] = input("  Power (e.g., 150 HP or 110 kW): ").strip() or None
    
    # 9. Seats ✅
    try:
        seats_input = input("  Seats (e.g., 5): ").strip()
        car['seats'] = int(seats_input) if seats_input else None
    except:
        car['seats'] = None
    
    # ============================================
    # 3. IMAGES (Multiple) ✅
    # ============================================
    print("\n📸 IMAGES:")
    print("  Enter image URLs (one per line, empty to finish):")
    print("  Tip: Right-click image → Copy image address")
    
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
    # 4. FEATURES / EQUIPMENT ✅
    # ============================================
    print("\n✨ FEATURES / EQUIPMENT:")
    print("  Enter features (one per line, empty to finish):")
    print("  Examples: Navigation, Leather seats, Parking sensors")
    
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
    seller_info['name'] = input("  Seller Name: ").strip() or None
    seller_info['location'] = input("  Location (City/Country): ").strip() or None
    seller_info['phone'] = input("  Phone Number: ").strip() or None
    
    car['seller_info'] = seller_info
    
    # ============================================
    # DESCRIPTION (Optional)
    # ============================================
    print("\n📝 DESCRIPTION (optional):")
    print("  Enter brief description or press Enter to skip:")
    car['description'] = input("  Description: ").strip() or None
    
    # ============================================
    # METADATA
    # ============================================
    car['scraped_at'] = datetime.now().isoformat()
    car['source'] = 'manual_entry_autoscout24'
    
    # ============================================
    # SUMMARY & CONFIRMATION
    # ============================================
    print("\n" + "="*60)
    print("📊 SUMMARY:")
    print("="*60)
    print(f"  Title: {car.get('title')}")
    print(f"  Brand: {car.get('brand')}")
    print(f"  Year: {car.get('year_numeric')}")
    print(f"  Mileage: {car.get('mileage_numeric')} km")
    print(f"  Price: €{car.get('price_numeric')}")
    print(f"  Fuel: {car.get('fuel_type')}")
    print(f"  Gearbox: {car.get('gearbox')}")
    print(f"  Power: {car.get('power')}")
    print(f"  Seats: {car.get('seats')}")
    print(f"  Registration: {car.get('first_registration')}")
    print(f"  Images: {car.get('image_count')}")
    print(f"  Features: {car.get('feature_count')}")
    print(f"  Seller: {car.get('seller_info', {}).get('name')}")
    print("="*60)
    
    # Confirm
    confirm = input("\n💾 Save this car? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled - car not saved")
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
            print(f"\n📂 Loaded {len(cars)} existing cars")
        except Exception as e:
            print(f"\n⚠️  Could not load existing data: {e}")
    
    # Add new car
    cars.append(car)
    
    # Save
    try:
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(cars, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved successfully!")
        print(f"📊 Total cars in database: {len(cars)}")
        return True
        
    except Exception as e:
        print(f"\n❌ Save error: {e}")
        return False


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🚗 MANUAL CAR DATA COLLECTION - AutoScout24")
    print("="*60)
    print("\n📋 INSTRUCTIONS:")
    print("  1. Open browser:")
    print("     - https://www.autoscout24.be/")
    print("     - https://www.autoscout24.de/")
    print("  2. Search for cars")
    print("  3. Click on a car to see details")
    print("  4. Enter the details here")
    print("  5. Repeat for more cars")
    print("\n💡 TIP: Keep browser and terminal side-by-side")
    print("="*60 + "\n")
    
    total_added = 0
    
    while True:
        if add_car_manually():
            total_added += 1
            print(f"\n🎉 Cars added this session: {total_added}")
        else:
            print(f"\n⚠️  Car not saved")
        
        # Ask for another
        print("\n" + "-"*60)
        again = input("➕ Add another car? (y/n): ").strip().lower()
        if again != 'y':
            break
    
    # ============================================
    # SESSION COMPLETE
    # ============================================
    print("\n" + "="*60)
    print(f"✅ SESSION COMPLETE!")
    print("="*60)
    print(f"  Cars added: {total_added}")
    
    if total_added > 0:
        print("\n🎯 NEXT STEPS:")
        print("  1. cd scripts (if not already there)")
        print("  2. python clean_real_data_only.py")
        print("  3. python show_data_summary.py")
        print("\n📊 This will:")
        print("  - Clean and validate your data")
        print("  - Show statistics")
        print("  - Prepare for API use")
    else:
        print("\n💡 No cars added this session")
        print("   Run again anytime to add cars!")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user (Ctrl+C)")
        print("✅ Data saved up to last completed car\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")