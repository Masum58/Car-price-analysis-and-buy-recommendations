"""
Enhanced AutoScout24 Scraper - Belgian Site
All Client Requirements: Gearbox, Registration, Images, Features, Seller, Power, Seats
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random
import json
import os
import re
from datetime import datetime


class AutoScout24Scraper:
    def __init__(self, chromedriver_path=None):
        """Initialize scraper with Chrome driver path"""
        self.chromedriver_path = chromedriver_path or r"C:\Users\masum\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        self.driver = None
        self.base_url = "https://www.autoscout24.be/lst"
        self.cars = []
        
    def setup_driver(self):
        """Setup Chrome with anti-detection"""
        print("🔧 Setting up Chrome driver...")
        
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # User agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(self.chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Chrome ready")
        
    def get_listing_urls(self, pages=3):
        """Get car detail page URLs from listing pages"""
        print(f"\n📋 Collecting car URLs from {pages} listing pages...")
        
        all_urls = []
        
        for page in range(1, pages + 1):
            url = f"{self.base_url}?atype=C&cy=B&damaged_listing=exclude&page={page}&search_id=example&sort=age"
            
            print(f"\n  Page {page}/{pages}: {url}")
            self.driver.get(url)
            
            # Human-like wait
            time.sleep(random.uniform(3, 5))
            
            try:
                # Find all car listing links
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/angebote/']")
                
                for link in links:
                    href = link.get_attribute('href')
                    if href and '/angebote/' in href and href not in all_urls:
                        # Clean URL (remove tracking params)
                        clean_url = href.split('?')[0]
                        all_urls.append(clean_url)
                
                print(f"    Found {len(all_urls)} unique URLs so far")
                
            except Exception as e:
                print(f"    ⚠️ Error on page {page}: {e}")
            
            time.sleep(random.uniform(2, 4))
        
        print(f"\n✅ Total URLs collected: {len(all_urls)}")
        return all_urls
    
    def scrape_car_details(self, url):
        """Scrape detailed information from car page"""
        print(f"\n🚗 Scraping: {url[:60]}...")
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(4, 6))  # Human-like delay
            
            data = {
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "source": "autoscout24_belgium"
            }
            
            # ============================================
            # BASIC INFO
            # ============================================
            
            # Title
            try:
                title = self.driver.find_element(By.TAG_NAME, "h1").text.strip()
                data["title"] = title
                print(f"  ✓ Title: {title[:50]}")
            except:
                data["title"] = None
            
            # Price
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, "[class*='Price'], [data-testid*='price']")
                price_text = price_elem.text.strip()
                data["price_text"] = price_text
                
                # Extract numeric
                numbers = re.findall(r'\d+', price_text.replace('.', '').replace(',', ''))
                if numbers:
                    data["price_numeric"] = int(numbers[0])
                    print(f"  ✓ Price: €{data['price_numeric']}")
            except:
                data["price_text"] = None
                data["price_numeric"] = None
            
            # Description
            try:
                desc = self.driver.find_element(By.CSS_SELECTOR, "[class*='description'], [data-testid*='description']").text
                data["description"] = desc[:500]
            except:
                data["description"] = None
            
            # ============================================
            # SPECIFICATIONS (Client Requirements)
            # ============================================
            
            try:
                # Method 1: Find dl/dt/dd elements
                specs = self.driver.find_elements(By.CSS_SELECTOR, "dl dt, dl dd")
                
                for i, elem in enumerate(specs):
                    text = elem.text.lower()
                    
                    # Gearbox ⭐
                    if "transmission" in text or "gearbox" in text or "versnellingsbak" in text:
                        try:
                            value = specs[i+1].text if i+1 < len(specs) else elem.text
                            if "manual" in value.lower() or "handgeschakeld" in value.lower():
                                data["gearbox"] = "Manual"
                            elif "automatic" in value.lower() or "automaat" in value.lower():
                                data["gearbox"] = "Automatic"
                            print(f"  ✓ Gearbox: {data.get('gearbox')}")
                        except:
                            pass
                    
                    # Fuel Type ⭐
                    elif "fuel" in text or "brandstof" in text:
                        try:
                            value = specs[i+1].text.lower() if i+1 < len(specs) else elem.text.lower()
                            if "diesel" in value:
                                data["fuel_type"] = "diesel"
                            elif "petrol" in value or "benzine" in value:
                                data["fuel_type"] = "petrol"
                            elif "electric" in value or "elektrisch" in value:
                                data["fuel_type"] = "electric"
                            elif "hybrid" in value:
                                data["fuel_type"] = "hybrid"
                            print(f"  ✓ Fuel: {data.get('fuel_type')}")
                        except:
                            pass
                    
                    # Power ⭐
                    elif "power" in text or "vermogen" in text or "pk" in text:
                        try:
                            value = specs[i+1].text if i+1 < len(specs) else elem.text
                            data["power"] = value
                            print(f"  ✓ Power: {value}")
                        except:
                            pass
                    
                    # Seats ⭐
                    elif "seats" in text or "zitplaatsen" in text:
                        try:
                            value = specs[i+1].text if i+1 < len(specs) else elem.text
                            seats_match = re.search(r'(\d+)', value)
                            if seats_match:
                                data["seats"] = int(seats_match.group(1))
                                print(f"  ✓ Seats: {data['seats']}")
                        except:
                            pass
                    
                    # First Registration ⭐
                    elif "registration" in text or "inschrijving" in text or "erstzulassung" in text:
                        try:
                            value = specs[i+1].text if i+1 < len(specs) else elem.text
                            data["first_registration"] = value
                            print(f"  ✓ Registration: {value}")
                        except:
                            pass
                    
                    # Mileage
                    elif "mileage" in text or "kilometerstand" in text:
                        try:
                            value = specs[i+1].text if i+1 < len(specs) else elem.text
                            km_match = re.search(r'([\d\.]+)', value.replace(',', ''))
                            if km_match:
                                data["mileage_numeric"] = int(km_match.group(1).replace('.', ''))
                                print(f"  ✓ Mileage: {data['mileage_numeric']} km")
                        except:
                            pass
                    
                    # Year
                    elif "year" in text or "bouwjaar" in text:
                        try:
                            value = specs[i+1].text if i+1 < len(specs) else elem.text
                            year_match = re.search(r'(20\d{2}|19\d{2})', value)
                            if year_match:
                                data["year_numeric"] = int(year_match.group(1))
                                print(f"  ✓ Year: {data['year_numeric']}")
                        except:
                            pass
            
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
                    if src and ("http" in src) and ("autoscout24" in src or "as24" in src):
                        if src not in images:
                            images.append(src)
                
                data["images"] = images[:15]  # Max 15 images
                data["image_count"] = len(data["images"])
                print(f"  ✓ Images: {data['image_count']}")
                
            except:
                data["images"] = []
                data["image_count"] = 0
            
            # ============================================
            # FEATURES ⭐
            # ============================================
            
            try:
                features = []
                feature_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='Equipment'], [class*='feature'], li")
                
                for feat in feature_elements:
                    text = feat.text.strip()
                    if text and len(text) > 3 and len(text) < 100:
                        if text not in features:
                            features.append(text)
                
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
                try:
                    seller_name = self.driver.find_element(By.CSS_SELECTOR, "[class*='seller'], [class*='dealer']").text
                    seller_info["name"] = seller_name
                    print(f"  ✓ Seller: {seller_name[:30]}")
                except:
                    seller_info["name"] = None
                
                # Location
                try:
                    location = self.driver.find_element(By.CSS_SELECTOR, "[class*='location'], [class*='address']").text
                    seller_info["location"] = location
                except:
                    seller_info["location"] = None
                
                # Phone (often requires click/reveal)
                try:
                    phone_elem = self.driver.find_element(By.CSS_SELECTOR, "[href^='tel:'], [class*='phone']")
                    phone = phone_elem.text or phone_elem.get_attribute('href')
                    if phone:
                        phone = phone.replace('tel:', '')
                        seller_info["phone"] = phone
                except:
                    seller_info["phone"] = None
                
                data["seller_info"] = seller_info
                
            except:
                data["seller_info"] = {}
            
            # ============================================
            # EXTRACT FROM TITLE/DESCRIPTION
            # ============================================
            
            # Brand from title
            if "brand" not in data or not data.get("brand"):
                title_lower = (data.get("title") or "").lower()
                brands = ['audi', 'bmw', 'mercedes', 'volkswagen', 'vw', 'ford', 'opel', 
                         'peugeot', 'renault', 'citroen', 'toyota', 'honda', 'nissan']
                for brand in brands:
                    if brand in title_lower:
                        data["brand"] = brand.upper() if brand == 'vw' else brand.capitalize()
                        break
            
            # Set defaults for missing fields
            data.setdefault("gearbox", None)
            data.setdefault("first_registration", None)
            data.setdefault("power", None)
            data.setdefault("seats", None)
            data.setdefault("fuel_type", None)
            data.setdefault("brand", None)
            data.setdefault("year_numeric", None)
            data.setdefault("mileage_numeric", None)
            
            print(f"  ✅ Car scraped successfully")
            return data
            
        except Exception as e:
            print(f"  ❌ Error scraping car: {e}")
            return None
    
    def save_data(self):
        """Save to project data folder"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_file = os.path.join(project_root, 'data', 'raw', 'cars_data.json')
        
        # Load existing
        existing = []
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except:
                pass
        
        # Remove duplicates
        existing_urls = {c.get('url') for c in existing if c.get('url')}
        new_cars = [c for c in self.cars if c.get('url') not in existing_urls]
        
        # Combine
        all_cars = existing + new_cars
        
        # Save
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(all_cars, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(all_cars)} total cars ({len(new_cars)} new)")
        return len(new_cars)
    
    def run(self, pages=3, max_cars=20):
        """Main scraping function"""
        print("="*60)
        print("🚗 AutoScout24 Belgium Scraper - Enhanced")
        print("="*60)
        
        try:
            self.setup_driver()
            
            # Get listing URLs
            urls = self.get_listing_urls(pages=pages)
            
            if not urls:
                print("⚠️ No URLs found!")
                return
            
            # Limit to max_cars
            urls = urls[:max_cars]
            
            print(f"\n📊 Will scrape {len(urls)} cars")
            
            # Scrape each car
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}]")
                car_data = self.scrape_car_details(url)
                
                if car_data:
                    self.cars.append(car_data)
                
                # Delay between cars
                time.sleep(random.uniform(2, 4))
            
            # Save
            if self.cars:
                new_count = self.save_data()
                print(f"\n✅ Success! Scraped {len(self.cars)} cars, added {new_count} new")
            else:
                print("\n⚠️ No cars scraped")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🔒 Browser closed")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AutoScout24 Belgium Scraper')
    parser.add_argument('--pages', type=int, default=3, help='Number of listing pages')
    parser.add_argument('--max', type=int, default=20, help='Max cars to scrape')
    parser.add_argument('--driver', type=str, default=None, help='ChromeDriver path')
    
    args = parser.parse_args()
    
    scraper = AutoScout24Scraper(chromedriver_path=args.driver)
    scraper.run(pages=args.pages, max_cars=args.max)

if __name__ == "__main__":
    main()