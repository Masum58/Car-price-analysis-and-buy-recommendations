"""
AutoScout24 Scraper - WORKING VERSION with Manual URLs
All Client Requirements: Gearbox, Registration, Images, Features, Seller, Power, Seats

HOW TO USE:
1. Go to: https://www.autoscout24.de/lst (or .be if accessible)
2. Copy 10-20 car detail page URLs
3. Add URLs to CAR_URLS list below
4. Run: python autoscout24_final.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import random
import json
import os
import re
from datetime import datetime


# ============================================================
# 📋 ADD CAR URLs HERE - Copy from browser
# ============================================================
# Example URLs - REPLACE WITH YOUR OWN:

CAR_URLS = [
    # BMW 520d - GERMAN SITE
    "https://www.autoscout24.de/angebote/bmw-520-d-xdrive-touring-aut-diesel-schwarz-a1b2c3d4-e5f6-7890-abcd-1234567890ab",
    
    # Audi A6 - GERMAN SITE
    "https://www.autoscout24.de/angebote/audi-a6-avant-3-0-tdi-quattro-s-tronic-diesel-silber-b2c3d4e5-f6g7-8901-bcde-234567890abc",
    
    # Mercedes - GERMAN SITE
    "https://www.autoscout24.de/angebote/mercedes-benz-e-220-d-amg-line-9g-tronic-diesel-schwarz-c3d4e5f6-g7h8-9012-cdef-34567890abcd",
    
    # Add 7-17 more from .de site
]

# ============================================================


class AutoScout24FinalScraper:
    def __init__(self):
        """Initialize scraper"""
        self.driver_path = r"C:\Users\masum\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        self.driver = None
        self.cars = []
        
    def setup_driver(self):
        """Setup Chrome with anti-detection"""
        print("🔧 Setting up Chrome driver...")
        
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Better user agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Chrome ready\n")
        
    def scrape_car_detail(self, url):
        """Scrape detailed information from one car page"""
        print(f"🚗 Scraping: {url[:60]}...")
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(4, 7))  # Human-like delay
            
            data = {
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "source": "autoscout24_manual"
            }
            
            # ============================================
            # BASIC INFO
            # ============================================
            
            # Title
            try:
                title = self.driver.find_element(By.TAG_NAME, "h1").text.strip()
                data["title"] = title
                print(f"  ✓ Title: {title[:45]}...")
            except:
                data["title"] = None
                print(f"  ⚠️ Title: Not found")
            
            # Price
            try:
                price_selectors = [
                    "[class*='PriceInfo']",
                    "[class*='Price']",
                    "[data-testid*='price']",
                    "h2"
                ]
                
                price_text = None
                for selector in price_selectors:
                    try:
                        price_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_elem.text.strip()
                        if price_text and ('€' in price_text or 'EUR' in price_text or any(c.isdigit() for c in price_text)):
                            break
                    except:
                        continue
                
                data["price_text"] = price_text
                
                # Extract numeric price
                if price_text:
                    numbers = re.findall(r'\d+', price_text.replace('.', '').replace(',', ''))
                    if numbers:
                        data["price_numeric"] = int(numbers[0])
                        print(f"  ✓ Price: €{data['price_numeric']:,}")
                else:
                    data["price_numeric"] = None
                    print(f"  ⚠️ Price: Not found")
            except:
                data["price_text"] = None
                data["price_numeric"] = None
            
            # Description
            try:
                desc_selectors = [
                    "[class*='description']",
                    "[data-testid*='description']",
                    "p"
                ]
                for selector in desc_selectors:
                    try:
                        desc = self.driver.find_element(By.CSS_SELECTOR, selector).text
                        if desc and len(desc) > 50:
                            data["description"] = desc[:500]
                            break
                    except:
                        continue
            except:
                data["description"] = None
            
            # ============================================
            # SPECIFICATIONS (Client Requirements)
            # ============================================
            
            print("  📋 Extracting specifications...")
            
            try:
                # Find all dt/dd specification pairs
                dt_elements = self.driver.find_elements(By.CSS_SELECTOR, "dl dt")
                
                for dt in dt_elements:
                    try:
                        key = dt.text.lower()
                        
                        # Get corresponding value (next sibling dd)
                        try:
                            value = dt.find_element(By.XPATH, "following-sibling::dd[1]").text.strip()
                        except:
                            continue
                        
                        # Gearbox ⭐
                        if any(word in key for word in ["transmission", "gearbox", "getriebe", "versnellingsbak"]):
                            if any(word in value.lower() for word in ["manual", "handgeschakeld", "schaltgetriebe"]):
                                data["gearbox"] = "Manual"
                            elif any(word in value.lower() for word in ["automatic", "automaat", "automatik"]):
                                data["gearbox"] = "Automatic"
                            elif any(word in value.lower() for word in ["semi", "tiptronic"]):
                                data["gearbox"] = "Semi-Automatic"
                        
                        # Fuel Type ⭐
                        elif any(word in key for word in ["fuel", "brandstof", "kraftstoff"]):
                            value_lower = value.lower()
                            if "diesel" in value_lower:
                                data["fuel_type"] = "diesel"
                            elif any(word in value_lower for word in ["petrol", "benzine", "benzin", "gasoline"]):
                                data["fuel_type"] = "petrol"
                            elif any(word in value_lower for word in ["electric", "elektrisch", "elektro"]):
                                data["fuel_type"] = "electric"
                            elif "hybrid" in value_lower:
                                data["fuel_type"] = "hybrid"
                            elif "lpg" in value_lower or "cng" in value_lower:
                                data["fuel_type"] = "lpg/cng"
                        
                        # Power ⭐
                        elif any(word in key for word in ["power", "vermogen", "leistung", "pk", "hp", "kw"]):
                            data["power"] = value
                        
                        # Seats ⭐
                        elif any(word in key for word in ["seats", "zitplaatsen", "sitzplätze"]):
                            seats_match = re.search(r'(\d+)', value)
                            if seats_match:
                                data["seats"] = int(seats_match.group(1))
                        
                        # First Registration ⭐
                        elif any(word in key for word in ["registration", "inschrijving", "erstzulassung", "eerste"]):
                            data["first_registration"] = value
                        
                        # Mileage
                        elif any(word in key for word in ["mileage", "kilometerstand", "laufleistung"]):
                            km_match = re.search(r'([\d\.]+)', value.replace(',', '').replace(' ', ''))
                            if km_match:
                                mileage = int(km_match.group(1).replace('.', ''))
                                # Handle if in thousands
                                if mileage < 1000:
                                    mileage *= 1000
                                data["mileage_numeric"] = mileage
                        
                        # Year
                        elif any(word in key for word in ["year", "bouwjaar", "baujahr"]):
                            year_match = re.search(r'(20\d{2}|19\d{2})', value)
                            if year_match:
                                data["year_numeric"] = int(year_match.group(1))
                        
                        # Model Year (if different)
                        elif "model" in key and "year" in key:
                            year_match = re.search(r'(20\d{2}|19\d{2})', value)
                            if year_match and "year_numeric" not in data:
                                data["year_numeric"] = int(year_match.group(1))
                    
                    except Exception as e:
                        continue
                
                # Print what we found
                if data.get("gearbox"):
                    print(f"    ✓ Gearbox: {data['gearbox']}")
                if data.get("fuel_type"):
                    print(f"    ✓ Fuel: {data['fuel_type']}")
                if data.get("power"):
                    print(f"    ✓ Power: {data['power']}")
                if data.get("seats"):
                    print(f"    ✓ Seats: {data['seats']}")
                if data.get("first_registration"):
                    print(f"    ✓ Registration: {data['first_registration']}")
                if data.get("mileage_numeric"):
                    print(f"    ✓ Mileage: {data['mileage_numeric']:,} km")
                if data.get("year_numeric"):
                    print(f"    ✓ Year: {data['year_numeric']}")
            
            except Exception as e:
                print(f"  ⚠️ Error parsing specs: {e}")
            
            # ============================================
            # IMAGES ⭐
            # ============================================
            
            try:
                images = []
                img_elements = self.driver.find_elements(By.TAG_NAME, "img")
                
                for img in img_elements:
                    src = img.get_attribute("src")
                    if src and "http" in src:
                        # Filter for car images (not logos, icons, etc.)
                        if any(word in src.lower() for word in ["autoscout", "as24", "vehicle", "car", "auto"]):
                            if src not in images and "logo" not in src.lower():
                                images.append(src)
                
                data["images"] = images[:15]  # Max 15 images
                data["image_count"] = len(data["images"])
                print(f"  ✓ Images: {data['image_count']}")
                
            except:
                data["images"] = []
                data["image_count"] = 0
            
            # ============================================
            # FEATURES / EQUIPMENT ⭐
            # ============================================
            
            try:
                features = []
                
                # Try multiple selectors for features
                feature_selectors = [
                    "[class*='Equipment'] li",
                    "[class*='equipment'] li",
                    "[class*='Feature'] li",
                    "[class*='feature'] li",
                    "ul li"
                ]
                
                for selector in feature_selectors:
                    try:
                        feature_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for feat in feature_elements:
                            text = feat.text.strip()
                            # Filter meaningful features
                            if text and 3 < len(text) < 100:
                                if text not in features:
                                    # Avoid duplicates and generic text
                                    if not any(skip in text.lower() for skip in ["cookie", "accept", "mehr", "more", "show"]):
                                        features.append(text)
                        
                        if len(features) > 5:  # Found meaningful features
                            break
                    except:
                        continue
                
                data["features"] = features[:25]  # Max 25 features
                data["feature_count"] = len(data["features"])
                print(f"  ✓ Features: {data['feature_count']}")
                
            except:
                data["features"] = []
                data["feature_count"] = 0
            
            # ============================================
            # SELLER INFO ⭐
            # ============================================
            
            try:
                seller_info = {}
                
                # Seller name
                seller_selectors = [
                    "[class*='seller']",
                    "[class*='Seller']",
                    "[class*='dealer']",
                    "[class*='Dealer']",
                    "[class*='vendor']"
                ]
                
                for selector in seller_selectors:
                    try:
                        seller_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        seller_name = seller_elem.text.strip()
                        if seller_name and len(seller_name) > 2:
                            seller_info["name"] = seller_name
                            print(f"  ✓ Seller: {seller_name[:30]}")
                            break
                    except:
                        continue
                
                if not seller_info.get("name"):
                    seller_info["name"] = None
                
                # Location
                location_selectors = [
                    "[class*='location']",
                    "[class*='Location']",
                    "[class*='address']",
                    "[class*='Address']"
                ]
                
                for selector in location_selectors:
                    try:
                        location_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        location = location_elem.text.strip()
                        if location and len(location) > 2:
                            seller_info["location"] = location
                            break
                    except:
                        continue
                
                if not seller_info.get("location"):
                    seller_info["location"] = None
                
                # Phone (often hidden/clickable)
                try:
                    phone_elems = self.driver.find_elements(By.CSS_SELECTOR, "[href^='tel:'], [class*='phone'], [class*='Phone']")
                    for elem in phone_elems:
                        phone = elem.text or elem.get_attribute('href')
                        if phone:
                            phone = phone.replace('tel:', '').strip()
                            if phone and len(phone) > 5:
                                seller_info["phone"] = phone
                                break
                except:
                    pass
                
                if not seller_info.get("phone"):
                    seller_info["phone"] = None
                
                data["seller_info"] = seller_info
                
            except:
                data["seller_info"] = {"name": None, "location": None, "phone": None}
            
            # ============================================
            # EXTRACT BRAND FROM TITLE
            # ============================================
            
            if data.get("title"):
                title_lower = data["title"].lower()
                
                common_brands = [
                    'audi', 'bmw', 'mercedes', 'volkswagen', 'vw', 'ford', 
                    'opel', 'peugeot', 'renault', 'citroen', 'toyota',
                    'honda', 'nissan', 'mazda', 'volvo', 'fiat', 'seat',
                    'skoda', 'hyundai', 'kia', 'mitsubishi', 'suzuki',
                    'lexus', 'porsche', 'mini', 'alfa romeo', 'jeep'
                ]
                
                for brand in common_brands:
                    if brand in title_lower:
                        if brand == 'vw':
                            data["brand"] = "VW"
                        elif brand == 'alfa romeo':
                            data["brand"] = "Alfa Romeo"
                        else:
                            data["brand"] = brand.capitalize()
                        break
            
            # ============================================
            # SET DEFAULTS FOR MISSING FIELDS
            # ============================================
            
            data.setdefault("gearbox", None)
            data.setdefault("first_registration", None)
            data.setdefault("power", None)
            data.setdefault("seats", None)
            data.setdefault("fuel_type", None)
            data.setdefault("brand", None)
            data.setdefault("year_numeric", None)
            data.setdefault("mileage_numeric", None)
            
            print(f"  ✅ Complete: {data.get('brand', 'Unknown')} {data.get('year_numeric', '')}\n")
            return data
            
        except Exception as e:
            print(f"  ❌ Error scraping car: {e}\n")
            return None
    
    def save_to_project(self):
        """Save scraped data to project data folder"""
        print("\n💾 Saving data to project...")
        
        # Get project paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_file = os.path.join(project_root, 'data', 'raw', 'cars_data.json')
        
        # Load existing data
        existing_cars = []
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    existing_cars = json.load(f)
                print(f"  📂 Loaded {len(existing_cars)} existing cars")
            except:
                print("  ⚠️ Could not load existing data")
        
        # Remove duplicates by URL
        existing_urls = {car.get('url') for car in existing_cars if car.get('url')}
        new_cars = [car for car in self.cars if car.get('url') not in existing_urls]
        
        # Combine
        all_cars = existing_cars + new_cars
        
        # Save
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(all_cars, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Saved: {len(all_cars)} total cars ({len(new_cars)} new)\n")
        print(f"  📄 File: {data_file}")
        
        return len(new_cars)
    
    def run(self):
        """Main scraping function"""
        print("="*60)
        print("🚗 AutoScout24 Scraper - Manual URL Method")
        print("="*60)
        print(f"\nURLs to scrape: {len(CAR_URLS)}")
        
        if not CAR_URLS:
            print("\n❌ ERROR: No URLs in CAR_URLS list!")
            print("\n📋 How to add URLs:")
            print("  1. Open browser: https://www.autoscout24.de/lst")
            print("  2. Find 10-20 cars you want")
            print("  3. Right-click each car → Copy link address")
            print("  4. Edit this file: Add URLs to CAR_URLS list")
            print("  5. Run again: python autoscout24_final.py")
            return
        
        if len(CAR_URLS) == 1 and "example" in CAR_URLS[0].lower():
            print("\n⚠️ WARNING: Still using example URL!")
            print("   Replace with real car URLs from AutoScout24")
        
        print("\n" + "="*60)
        
        try:
            # Setup browser
            self.setup_driver()
            
            # Scrape each car
            for i, url in enumerate(CAR_URLS, 1):
                print(f"[{i}/{len(CAR_URLS)}]")
                
                car_data = self.scrape_car_detail(url)
                
                if car_data:
                    self.cars.append(car_data)
                else:
                    print(f"  ⚠️ Skipped (error)\n")
                
                # Human-like delay between cars
                if i < len(CAR_URLS):
                    delay = random.uniform(3, 6)
                    print(f"  ⏱️ Waiting {delay:.1f}s before next car...")
                    time.sleep(delay)
            
            # Save results
            print("="*60)
            
            if self.cars:
                new_count = self.save_to_project()
                
                print("\n" + "="*60)
                print("✅ SCRAPING COMPLETE!")
                print("="*60)
                print(f"  Cars scraped: {len(self.cars)}")
                print(f"  New cars added: {new_count}")
                print(f"  Success rate: {len(self.cars)}/{len(CAR_URLS)} ({len(self.cars)*100//len(CAR_URLS)}%)")
                print("\n🎯 Next steps:")
                print("  1. cd ..\scripts")
                print("  2. python clean_real_data_only.py")
                print("  3. python show_data_summary.py")
                print("="*60 + "\n")
            else:
                print("\n⚠️ No cars were scraped successfully")
            
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
        
        finally:
            if self.driver:
                print("🔒 Closing browser...")
                self.driver.quit()
                print("✅ Done!\n")


if __name__ == "__main__":
    print("\n")
    scraper = AutoScout24FinalScraper()
    scraper.run()