"""
AutoScout24 Scraper - VPN Optimized Version
Use with VPN for better success rate

SETUP:
1. Connect VPN to Belgium or Germany
2. Add car URLs below
3. Run script
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
# 📋 CAR URLs - Add real URLs from browser
# ============================================================

CAR_URLS = [
    # Car 1: Audi A6 Avant
    "https://www.autoscout24.be/nl/aanbod/audi-a6-a6-avant-40-tdi-35-tdi-2-stuks-op-stock-diesel-zwart-c322d9e7-4543-43ae-b946-fdbd1d54c0fb",
    
    # Car 2: Mercedes-Benz C 200 d
    "https://www.autoscout24.be/nl/aanbod/mercedes-benz-c-200-c-200-d-amg-line-diesel-d2cd206b-886c-45dc-8144-3df0ec401af3",
    
    # Car 3: BMW X1 25e
    "https://www.autoscout24.be/nl/aanbod/bmw-x1-25e-full-led-prof-leer-head-up-zetelverw-cam-19-elektrisch-benzine-zwart-5bc667db-3b89-4f32-b610-4104238d2054"
]


class VPNOptimizedScraper:
    def __init__(self):
        self.driver_path = r"C:\Users\masum\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        self.driver = None
        self.cars = []
        
    def setup_driver(self):
        """Setup Chrome with VPN-friendly settings"""
        print("🔧 Setting up Chrome (VPN mode)...")
        
        options = Options()
        
        # Anti-detection settings
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Better user agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Use system proxy (VPN)
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        
        # Accept language
        options.add_argument("--lang=de-DE,de,en-US,en")
        options.add_argument("--accept-lang=de-DE,de,en-US,en")
        
        # Disable automation flags
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # Enable JavaScript
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
        })
        
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Execute stealth scripts
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome ready with VPN settings\n")
        
        # Check IP location
        self.check_ip_location()
        
    def check_ip_location(self):
        """Verify VPN is working"""
        print("🌍 Checking IP location...")
        try:
            self.driver.get("https://api.ipify.org?format=json")
            time.sleep(2)
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            if "ip" in page_text.lower():
                print(f"  ℹ️  Current IP detected")
                print(f"  💡 Make sure VPN is connected!")
            
            # Go to AutoScout24 to test access
            print("\n🔍 Testing AutoScout24 access...")
            self.driver.get("https://www.autoscout24.de/")
            time.sleep(3)
            
            title = self.driver.title
            if "autoscout24" in title.lower():
                print(f"  ✅ AutoScout24 accessible!")
                print(f"  📄 Page: {title[:50]}\n")
            else:
                print(f"  ⚠️  Unusual page: {title}")
                print(f"  💡 Check VPN connection!\n")
                
        except Exception as e:
            print(f"  ⚠️  Could not verify: {e}\n")
    
    def human_like_delay(self, min_sec=3, max_sec=7):
        """Random human-like delay"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    def scrape_car(self, url):
        """Scrape one car with VPN-optimized approach"""
        print(f"🚗 Loading: {url[:60]}...")
        
        try:
            # Navigate with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver.get(url)
                    self.human_like_delay(5, 8)  # Longer wait with VPN
                    
                    # Check if page loaded correctly
                    title = self.driver.title.lower()
                    
                    if "error" in title or "nicht" in title or "existe" in title:
                        print(f"  ⚠️  Error page detected (attempt {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            print(f"  🔄 Retrying...")
                            self.human_like_delay(10, 15)  # Wait before retry
                            continue
                        else:
                            print(f"  ❌ Failed after {max_retries} attempts")
                            return None
                    else:
                        break  # Success
                        
                except Exception as e:
                    print(f"  ⚠️  Load error: {e}")
                    if attempt < max_retries - 1:
                        continue
                    return None
            
            # Start extraction
            data = {
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "source": "autoscout24_vpn"
            }
            
            # Title
            try:
                h1 = self.driver.find_element(By.TAG_NAME, "h1")
                data["title"] = h1.text.strip()
                print(f"  ✓ {data['title'][:45]}")
            except:
                data["title"] = None
            
            # Price
            try:
                price_selectors = ["[class*='Price']", "h2", "[data-testid*='price']"]
                for selector in price_selectors:
                    try:
                        price_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_elem.text
                        if price_text and any(c.isdigit() for c in price_text):
                            data["price_text"] = price_text
                            numbers = re.findall(r'\d+', price_text.replace('.', '').replace(',', ''))
                            if numbers:
                                data["price_numeric"] = int(numbers[0])
                                print(f"  ✓ €{data['price_numeric']:,}")
                            break
                    except:
                        continue
            except:
                data["price_numeric"] = None
            
            # Specifications
            print(f"  📋 Extracting specs...")
            
            try:
                specs = self.driver.find_elements(By.CSS_SELECTOR, "dl dt")
                
                for dt in specs:
                    try:
                        key = dt.text.lower()
                        value = dt.find_element(By.XPATH, "following-sibling::dd[1]").text.strip()
                        
                        # Gearbox
                        if any(w in key for w in ["getriebe", "transmission", "versnellingsbak"]):
                            if "auto" in value.lower():
                                data["gearbox"] = "Automatic"
                            else:
                                data["gearbox"] = "Manual"
                        
                        # Fuel
                        elif any(w in key for w in ["kraftstoff", "fuel", "brandstof"]):
                            val = value.lower()
                            if "diesel" in val:
                                data["fuel_type"] = "diesel"
                            elif any(w in val for w in ["benzin", "petrol"]):
                                data["fuel_type"] = "petrol"
                            elif "elek" in val:
                                data["fuel_type"] = "electric"
                            elif "hybrid" in val:
                                data["fuel_type"] = "hybrid"
                        
                        # Power
                        elif any(w in key for w in ["leistung", "power", "vermogen"]):
                            data["power"] = value
                        
                        # Seats
                        elif any(w in key for w in ["sitze", "seats", "zitplaatsen"]):
                            match = re.search(r'(\d+)', value)
                            if match:
                                data["seats"] = int(match.group(1))
                        
                        # Registration
                        elif any(w in key for w in ["erstzulassung", "registration", "inschrijving"]):
                            data["first_registration"] = value
                        
                        # Mileage
                        elif any(w in key for w in ["kilometerstand", "mileage", "laufleistung"]):
                            match = re.search(r'([\d\.]+)', value.replace(',', ''))
                            if match:
                                km = int(match.group(1).replace('.', ''))
                                if km < 1000:
                                    km *= 1000
                                data["mileage_numeric"] = km
                        
                        # Year
                        elif any(w in key for w in ["baujahr", "year", "bouwjaar"]):
                            match = re.search(r'(20\d{2}|19\d{2})', value)
                            if match:
                                data["year_numeric"] = int(match.group(1))
                    
                    except:
                        continue
                
                # Print what we found
                for field in ["gearbox", "fuel_type", "power", "seats", "mileage_numeric", "year_numeric"]:
                    if data.get(field):
                        print(f"    ✓ {field}: {data[field]}")
            
            except Exception as e:
                print(f"  ⚠️  Spec error: {e}")
            
            # Images
            try:
                images = []
                for img in self.driver.find_elements(By.TAG_NAME, "img"):
                    src = img.get_attribute("src")
                    if src and "http" in src and any(w in src for w in ["autoscout", "as24", "vehicle"]):
                        if src not in images and "logo" not in src.lower():
                            images.append(src)
                
                data["images"] = images[:15]
                data["image_count"] = len(data["images"])
                print(f"  ✓ Images: {data['image_count']}")
            except:
                data["images"] = []
                data["image_count"] = 0
            
            # Features
            try:
                features = []
                for li in self.driver.find_elements(By.CSS_SELECTOR, "li"):
                    text = li.text.strip()
                    if text and 3 < len(text) < 100:
                        if text not in features:
                            features.append(text)
                
                data["features"] = features[:25]
                data["feature_count"] = len(data["features"])
                print(f"  ✓ Features: {data['feature_count']}")
            except:
                data["features"] = []
                data["feature_count"] = 0
            
            # Seller
            try:
                seller = {}
                for selector in ["[class*='seller']", "[class*='dealer']"]:
                    try:
                        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        name = elem.text.strip()
                        if name and len(name) > 2:
                            seller["name"] = name
                            break
                    except:
                        continue
                
                data["seller_info"] = seller
            except:
                data["seller_info"] = {}
            
            # Brand from title
            if data.get("title"):
                brands = ['audi', 'bmw', 'mercedes', 'vw', 'volkswagen', 'ford', 'opel', 'peugeot', 'renault']
                for brand in brands:
                    if brand in data["title"].lower():
                        data["brand"] = brand.upper() if brand == 'vw' else brand.capitalize()
                        break
            
            # Defaults
            for field in ["gearbox", "first_registration", "power", "seats", "fuel_type", "brand", "year_numeric", "mileage_numeric"]:
                data.setdefault(field, None)
            
            print(f"  ✅ {data.get('brand', '?')} {data.get('year_numeric', '')}\n")
            return data
            
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
            return None
    
    def save_data(self):
        """Save to project"""
        print("💾 Saving...")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_file = os.path.join(project_root, 'data', 'raw', 'cars_data.json')
        
        existing = []
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        
        existing_urls = {c.get('url') for c in existing if c.get('url')}
        new_cars = [c for c in self.cars if c.get('url') not in existing_urls]
        
        all_cars = existing + new_cars
        
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(all_cars, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Saved: {len(all_cars)} total ({len(new_cars)} new)\n")
        return len(new_cars)
    
    def run(self):
        """Main"""
        print("="*60)
        print("🚗 AutoScout24 VPN-Optimized Scraper")
        print("="*60)
        print(f"\n⚠️  IMPORTANT: Connect VPN before running!")
        print(f"  Recommended: Belgium or Germany server\n")
        print("="*60)
        
        if not CAR_URLS:
            print("\n❌ No URLs in CAR_URLS list!")
            print("\n📋 Steps:")
            print("  1. Connect VPN (Belgium/Germany)")
            print("  2. Open: https://www.autoscout24.de/lst")
            print("  3. Copy 10-20 car URLs")
            print("  4. Add to CAR_URLS in this file")
            print("  5. Run again\n")
            return
        
        print(f"\nURLs to scrape: {len(CAR_URLS)}\n")
        print("="*60 + "\n")
        
        try:
            self.setup_driver()
            
            for i, url in enumerate(CAR_URLS, 1):
                print(f"[{i}/{len(CAR_URLS)}]")
                
                car = self.scrape_car(url)
                if car:
                    self.cars.append(car)
                
                if i < len(CAR_URLS):
                    delay = self.human_like_delay(4, 8)
                    print(f"  ⏱️  Waiting {delay:.1f}s...\n")
            
            if self.cars:
                new_count = self.save_data()
                
                print("="*60)
                print("✅ COMPLETE!")
                print("="*60)
                print(f"  Scraped: {len(self.cars)}")
                print(f"  New: {new_count}")
                print(f"  Success: {len(self.cars)*100//len(CAR_URLS)}%")
                print("\n🎯 Next:")
                print(r"  cd ..\scripts")
                print("  python clean_real_data_only.py")
                print("="*60 + "\n")
            
        finally:
            if self.driver:
                print("🔒 Closing...")
                self.driver.quit()
                print("✅ Done!\n")


if __name__ == "__main__":
    scraper = VPNOptimizedScraper()
    scraper.run()