"""
AutoScout24.be Scraper with Cookie Consent Handling
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


class AutoScout24WithCookies:
    def __init__(self):
        self.driver_path = r"C:\Users\masum\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        self.driver = None
        self.cars = []
    
    def setup_driver(self):
        """Setup Chrome"""
        print("🔧 Setting up Chrome...")
        
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Add user data to remember cookies
        options.add_argument(r"user-data-dir=C:\selenium_profile")
        
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        print("✅ Ready\n")
    
    def handle_cookies(self):
        """Accept cookie consent"""
        print("🍪 Handling cookies...")
        
        try:
            # Wait for cookie banner
            wait = WebDriverWait(self.driver, 10)
            
            # Common cookie button selectors
            cookie_buttons = [
                "button[id*='accept']",
                "button[class*='accept']",
                "button[id*='consent']",
                "button[class*='consent']",
                "#onetrust-accept-btn-handler",
                ".cookie-accept",
                "[data-testid*='cookie-accept']"
            ]
            
            for selector in cookie_buttons:
                try:
                    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    button.click()
                    print("  ✓ Cookies accepted")
                    time.sleep(2)
                    return True
                except:
                    continue
            
            print("  ⚠️  No cookie button found (maybe already accepted)")
            return True
            
        except Exception as e:
            print(f"  ⚠️  Cookie handling: {e}")
            return False
    
    def get_car_urls_from_page(self, page_url):
        """Get URLs from one listing page"""
        print(f"\n📄 Loading: {page_url}")
        
        self.driver.get(page_url)
        
        # Handle cookies on first page
        if "page=1" in page_url or page_url.endswith("sort=age"):
            self.handle_cookies()
        
        time.sleep(random.uniform(3, 5))
        
        # Check page title
        title = self.driver.title
        print(f"  Page: {title}")
        
        if "error" in title.lower():
            print("  ❌ Error page detected!")
            return []
        
        urls = []
        
        # Try multiple selector strategies
        selectors = [
            "article a[href*='/angebote/']",
            "a[href*='/angebote/']",
            "[class*='ListItem'] a",
            "a[data-qa-listing-link]"
        ]
        
        for selector in selectors:
            try:
                links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  Trying {selector}: {len(links)} found")
                
                if links:
                    for link in links:
                        href = link.get_attribute('href')
                        if href and '/angebote/' in href:
                            clean_url = href.split('?')[0]
                            if clean_url not in urls:
                                urls.append(clean_url)
                    
                    if urls:
                        print(f"  ✓ Got {len(urls)} URLs")
                        return urls
            except:
                continue
        
        print("  ⚠️  No URLs found")
        return []
    
    def scrape_car_detail(self, url):
        """Scrape one car"""
        print(f"\n🚗 {url[:60]}...")
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            data = {
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "source": "autoscout24_belgium"
            }
            
            # Title
            try:
                data["title"] = self.driver.find_element(By.TAG_NAME, "h1").text.strip()
                print(f"  ✓ {data['title'][:40]}")
            except:
                data["title"] = None
            
            # Price
            try:
                price = self.driver.find_element(By.CSS_SELECTOR, "[class*='Price']").text
                data["price_text"] = price
                nums = re.findall(r'\d+', price.replace('.', '').replace(',', ''))
                if nums:
                    data["price_numeric"] = int(nums[0])
            except:
                data["price_text"] = None
                data["price_numeric"] = None
            
            # Specs from dl/dt/dd
            specs = self.driver.find_elements(By.CSS_SELECTOR, "dl dt")
            
            for dt in specs:
                try:
                    key = dt.text.lower()
                    value = dt.find_element(By.XPATH, "following-sibling::dd[1]").text.strip()
                    
                    if "transmission" in key or "gearbox" in key:
                        data["gearbox"] = "Automatic" if "automatic" in value.lower() else "Manual"
                    elif "fuel" in key or "brandstof" in key:
                        if "diesel" in value.lower():
                            data["fuel_type"] = "diesel"
                        elif "petrol" in value.lower() or "benzin" in value.lower():
                            data["fuel_type"] = "petrol"
                    elif "power" in key:
                        data["power"] = value
                    elif "seats" in key or "zitplaatsen" in key:
                        match = re.search(r'(\d+)', value)
                        if match:
                            data["seats"] = int(match.group(1))
                    elif "registration" in key:
                        data["first_registration"] = value
                    elif "mileage" in key or "kilometerstand" in key:
                        match = re.search(r'([\d\.]+)', value.replace(',', ''))
                        if match:
                            data["mileage_numeric"] = int(match.group(1).replace('.', ''))
                    elif "year" in key or "bouwjaar" in key:
                        match = re.search(r'(20\d{2})', value)
                        if match:
                            data["year_numeric"] = int(match.group(1))
                except:
                    continue
            
            # Images
            images = []
            for img in self.driver.find_elements(By.TAG_NAME, "img"):
                src = img.get_attribute("src")
                if src and "http" in src and "autoscout" in src:
                    if src not in images:
                        images.append(src)
            data["images"] = images[:15]
            data["image_count"] = len(data["images"])
            
            # Features
            features = []
            for li in self.driver.find_elements(By.CSS_SELECTOR, "li"):
                text = li.text.strip()
                if text and 3 < len(text) < 100:
                    if text not in features:
                        features.append(text)
            data["features"] = features[:25]
            data["feature_count"] = len(data["features"])
            
            # Seller
            seller = {}
            try:
                seller["name"] = self.driver.find_element(By.CSS_SELECTOR, "[class*='seller']").text
            except:
                seller["name"] = None
            data["seller_info"] = seller
            
            # Brand from title
            if data.get("title"):
                brands = ['audi', 'bmw', 'mercedes', 'vw', 'ford', 'opel', 'peugeot', 'renault']
                for brand in brands:
                    if brand in data["title"].lower():
                        data["brand"] = brand.upper() if brand == 'vw' else brand.capitalize()
                        break
            
            # Defaults
            for field in ["gearbox", "first_registration", "power", "seats", "fuel_type", "brand"]:
                data.setdefault(field, None)
            
            print(f"  ✅ {data.get('brand', '?')} {data.get('year_numeric', '')}")
            return data
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def save_data(self):
        """Save to project"""
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
        
        print(f"\n💾 Saved: {len(all_cars)} total ({len(new_cars)} new)")
    
    def run(self, pages=2):
        """Main"""
        print("="*60)
        print("🚗 AutoScout24.be - Cookie Handling Version")
        print("="*60 + "\n")
        
        try:
            self.setup_driver()
            
            # Collect URLs
            all_urls = []
            for page in range(1, pages + 1):
                url = f"https://www.autoscout24.be/lst?atype=C&cy=B&sort=age&page={page}"
                urls = self.get_car_urls_from_page(url)
                all_urls.extend(urls)
                time.sleep(2)
            
            if not all_urls:
                print("\n⚠️  No URLs collected!")
                print("\n💡 Manual method recommended:")
                print("   Use: autoscout_manual_urls.py")
                return
            
            all_urls = list(set(all_urls))[:20]  # Max 20
            print(f"\n✅ Total URLs: {len(all_urls)}")
            
            # Scrape details
            for i, url in enumerate(all_urls, 1):
                print(f"\n[{i}/{len(all_urls)}]")
                car = self.scrape_car_detail(url)
                if car:
                    self.cars.append(car)
                time.sleep(random.uniform(2, 4))
            
            if self.cars:
                self.save_data()
                print(f"\n✅ Success! {len(self.cars)} cars")
            
        finally:
            if self.driver:
                input("\nPress Enter to close browser...")
                self.driver.quit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int, default=2)
    args = parser.parse_args()
    
    scraper = AutoScout24WithCookies()
    scraper.run(pages=args.pages)
