"""
Car Price Analysis - Complete Web Scraper with Selenium
Scrapes car listings from 2dehands.be
"""

import os
import re
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Keys
THORDATA_API_KEY = os.getenv("THORDATA_API_KEY")

# Target websites
WEBSITES = {
    "2dehands": "https://www.2dehands.be/l/auto-s/",
}


class SeleniumCarScraper:
    """Selenium-based scraper for 2dehands.be"""
    
    def __init__(self, headless=True):
        """Initialize Selenium driver"""
        self.headless = headless
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        logger.info("Setting up Selenium Chrome driver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✓ Chrome driver ready")
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def scrape_2dehands_page(self, url: str) -> List[Dict]:
        """Scrape a single page from 2dehands.be"""
        logger.info(f"Scraping with Selenium: {url}")
        
        results = []
        
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)
            
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article, li, div")))
                time.sleep(3)  # Wait for dynamic content
            except TimeoutException:
                logger.warning("Timeout waiting for page load")
                return results
            
            # Get all text content
            page_text = self.driver.page_source
            soup = BeautifulSoup(page_text, 'html.parser')
            
            # Find all links that look like car listings
            all_links = soup.find_all('a', href=True)
            
            car_listings = []
            for link in all_links:
                href = link.get('href', '')
                if '/a/' in href or '/aanbod/' in href:
                    text = link.get_text(strip=True)
                    if text and len(text) > 10:
                        car_listings.append({
                            'url': href if href.startswith('http') else f"https://www.2dehands.be{href}",
                            'text': text
                        })
            
            logger.info(f"Found {len(car_listings)} potential car listings")
            
            # Process listings
            for idx, listing in enumerate(car_listings[:30], 1):
                try:
                    title = listing['text']
                    car_url = listing['url']
                    
                    # Extract data
                    price = self.extract_price_advanced(title)
                    year = self.extract_year(title)
                    mileage = self.extract_mileage(title)
                    brand = self.extract_brand(title)
                    
                    if title and price and price >= 1000:
                        car_data = {
                            "title": title[:100],
                            "brand": brand,
                            "year_numeric": year,
                            "mileage_numeric": mileage,
                            "price_numeric": price,
                            "url": car_url,
                            "source": "2dehands.be",
                            "scraped_at": datetime.now().isoformat()
                        }
                        
                        results.append(car_data)
                        logger.info(f"  {idx}. ✓ {title[:40]}... - €{price:,.0f}")
                
                except Exception as e:
                    continue
            
            logger.info(f"✓ Scraped {len(results)} cars from page")
            
        except Exception as e:
            logger.error(f"Error scraping page: {e}")
        
        return results
    
    def extract_price_advanced(self, text: str) -> Optional[float]:
        """Advanced price extraction"""
        patterns = [
            r'€\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*€',
            r'(\d{1,3}(?:[.,]\d{3})*)\s*euro',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    cleaned = match.replace('.', '').replace(',', '')
                    price = float(cleaned)
                    if 1000 <= price <= 300000:
                        return price
                except:
                    continue
        
        return None
    
    def extract_year(self, text: str) -> Optional[int]:
        """Extract year"""
        years = re.findall(r'\b(19\d{2}|20[0-2]\d)\b', text)
        if years:
            year = int(years[0])
            if 1990 <= year <= 2025:
                return year
        return None
    
    def extract_mileage(self, text: str) -> Optional[int]:
        """Extract mileage"""
        patterns = [
            r'(\d{1,3}(?:[.,]\d{3})*)\s*(?:km|KM)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    cleaned = match.replace('.', '').replace(',', '')
                    mileage = int(cleaned)
                    if 0 <= mileage <= 500000:
                        return mileage
                except:
                    continue
        return None
    
    def extract_brand(self, title: str) -> Optional[str]:
        """Extract brand from title"""
        brands = [
            "BMW", "Mercedes", "Audi", "Volkswagen", "Tesla", "Toyota",
            "Honda", "Ford", "Opel", "Peugeot", "Renault", "Citroen",
            "Nissan", "Mazda", "Hyundai", "Kia", "Volvo", "Seat",
            "Skoda", "Dacia", "Fiat", "Alfa Romeo", "Porsche", "Lexus",
            "VW", "Dodge", "Jeep", "Chevrolet"
        ]
        
        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand
        return None
    
    def scrape_multiple_pages(self, base_url: str, max_pages: int = 3) -> List[Dict]:
        """Scrape multiple pages"""
        all_results = []
        
        for page in range(1, max_pages + 1):
            url = f"{base_url}p/{page}/"
            results = self.scrape_2dehands_page(url)
            all_results.extend(results)
            
            logger.info(f"Page {page}/{max_pages}: {len(results)} cars | Total: {len(all_results)}")
            
            time.sleep(3)
        
        return all_results
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("✓ Browser closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def remove_duplicates(data: List[Dict]) -> List[Dict]:
    """Remove duplicate listings"""
    seen = set()
    unique = []
    
    for item in data:
        key = f"{item.get('title', '')}_{item.get('price_numeric', 0)}"
        if key not in seen:
            seen.add(key)
            unique.append(item)
    
    logger.info(f"Removed {len(data) - len(unique)} duplicates")
    return unique


def validate_data(data: List[Dict]) -> List[Dict]:
    """Validate and clean scraped data"""
    valid = []
    
    for item in data:
        if not item.get('title'):
            continue
        if not item.get('price_numeric'):
            continue
        
        if item.get('year_numeric'):
            if not (1990 <= item['year_numeric'] <= 2025):
                item['year_numeric'] = None
        
        if item.get('mileage_numeric'):
            if not (0 <= item['mileage_numeric'] <= 500000):
                item['mileage_numeric'] = None
        
        if item.get('price_numeric'):
            if not (1000 <= item['price_numeric'] <= 300000):
                continue
        
        valid.append(item)
    
    logger.info(f"Validated {len(valid)}/{len(data)} listings")
    return valid


def save_to_json(data: List[Dict], filename: str = "cars_data.json"):
    """Save data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved {len(data)} listings to {filename}")
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")


def save_to_csv(data: List[Dict], filename: str = "cars_data.csv"):
    """Save data to CSV file"""
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"✓ Saved {len(data)} listings to {filename}")
    except Exception as e:
        logger.error(f"Failed to save CSV: {e}")


def main():
    """Main entry point with Selenium"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Car Price Scraper with Selenium')
    parser.add_argument('--pages', type=int, default=2, help='Max pages to scrape')
    parser.add_argument('--use-selenium', action='store_true', default=True,
                       help='Use Selenium (default: True)')
    parser.add_argument('--show-browser', action='store_true',
                       help='Show browser window')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Car Price Scraper - Selenium Mode")
    logger.info("=" * 60)
    
    try:
        with SeleniumCarScraper(headless=not args.show_browser) as scraper:
            base_url = "https://www.2dehands.be/l/auto-s/"
            all_data = scraper.scrape_multiple_pages(base_url, max_pages=args.pages)
            
            if all_data:
                all_data = remove_duplicates(all_data)
                all_data = validate_data(all_data)
                
                save_to_json(all_data)
                save_to_csv(all_data)
                
                logger.info("=" * 60)
                logger.info(f"✓ Scraping completed: {len(all_data)} cars")
                logger.info("=" * 60)
            else:
                logger.warning("No data scraped")
    
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()