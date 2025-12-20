"""
AutoScout24.be Scraper - Alternative data source
This site is often easier to scrape than 2dehands
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoScout24Scraper:
    """Scraper for AutoScout24.be"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'nl-BE,nl;q=0.9,en;q=0.8'
        })
        self.base_url = "https://www.autoscout24.be"
    
    def scrape_search_page(self, page: int = 1) -> List[Dict]:
        """Scrape AutoScout24 search results"""
        
        # AutoScout24 search URL
        url = f"{self.base_url}/lst?sort=standard&desc=0&ustate=N%2CU&size=20&page={page}&atype=C"
        
        logger.info(f"Scraping AutoScout24 page {page}: {url}")
        
        results = []
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page: {response.status_code}")
                return results
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find listing cards
            listings = soup.find_all('article', class_=lambda x: x and 'listing' in x.lower())
            
            if not listings:
                # Try alternative selectors
                listings = soup.find_all('div', {'data-item-name': True})
            
            logger.info(f"Found {len(listings)} listings")
            
            for listing in listings:
                try:
                    # Extract title
                    title_elem = listing.find(['h2', 'h3'])
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # Extract price
                    price_elem = listing.find(class_=lambda x: x and 'price' in str(x).lower())
                    price_text = price_elem.get_text(strip=True) if price_elem else ""
                    price = self.extract_price(price_text)
                    
                    # Extract details
                    details_text = listing.get_text()
                    
                    year = self.extract_year(details_text)
                    mileage = self.extract_mileage(details_text)
                    brand = self.extract_brand(title)
                    
                    # Extract URL
                    link_elem = listing.find('a', href=True)
                    car_url = link_elem['href'] if link_elem else ""
                    if car_url and not car_url.startswith('http'):
                        car_url = self.base_url + car_url
                    
                    if title and price:
                        car_data = {
                            "title": title,
                            "brand": brand,
                            "year_numeric": year,
                            "mileage_numeric": mileage,
                            "price_numeric": price,
                            "url": car_url,
                            "source": "autoscout24.be",
                            "scraped_at": datetime.now().isoformat()
                        }
                        results.append(car_data)
                        logger.info(f"  ✓ {title[:40]}... - €{price:,.0f}")
                
                except Exception as e:
                    logger.error(f"Error parsing listing: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping page: {e}")
        
        return results
    
    def extract_price(self, text: str) -> float:
        """Extract price"""
        import re
        patterns = [
            r'€\s*(\d{1,3}(?:[.,\s]\d{3})*)',
            r'(\d{1,3}(?:[.,\s]\d{3})*)\s*€',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    cleaned = match.replace('.', '').replace(',', '').replace(' ', '')
                    price = float(cleaned)
                    if 1000 <= price <= 300000:
                        return price
                except:
                    continue
        return None
    
    def extract_year(self, text: str) -> int:
        """Extract year"""
        import re
        years = re.findall(r'\b(19\d{2}|20[0-2]\d)\b', text)
        if years:
            year = int(years[0])
            if 1990 <= year <= 2025:
                return year
        return None
    
    def extract_mileage(self, text: str) -> int:
        """Extract mileage"""
        import re
        patterns = [
            r'(\d{1,3}(?:[.,\s]\d{3})*)\s*km',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    cleaned = match.replace('.', '').replace(',', '').replace(' ', '')
                    mileage = int(cleaned)
                    if 0 <= mileage <= 500000:
                        return mileage
                except:
                    continue
        return None
    
    def extract_brand(self, title: str) -> str:
        """Extract brand"""
        brands = [
            "BMW", "Mercedes", "Audi", "Volkswagen", "Tesla", "Toyota",
            "Honda", "Ford", "Opel", "Peugeot", "Renault", "Citroen",
            "Nissan", "Mazda", "Hyundai", "Kia", "Volvo", "Seat",
            "Skoda", "Dacia", "Fiat", "Alfa Romeo", "Porsche", "Lexus"
        ]
        
        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand
        return None
    
    def scrape_multiple_pages(self, max_pages: int = 10) -> List[Dict]:
        """Scrape multiple pages"""
        all_results = []
        
        for page in range(1, max_pages + 1):
            results = self.scrape_search_page(page)
            all_results.extend(results)
            
            logger.info(f"Page {page}/{max_pages}: {len(results)} cars | Total: {len(all_results)}")
            
            if len(results) == 0:
                logger.warning("No more results, stopping")
                break
            
            time.sleep(2)  # Be polite
        
        return all_results


def main():
    """Test AutoScout24 scraper"""
    logger.info("=" * 60)
    logger.info("AutoScout24.be Scraper Test")
    logger.info("=" * 60)
    
    scraper = AutoScout24Scraper()
    cars = scraper.scrape_multiple_pages(max_pages=5)
    
    if cars:
        # Save to file
        with open('autoscout24_data.json', 'w', encoding='utf-8') as f:
            json.dump(cars, f, indent=2, ensure_ascii=False)
        
        logger.info("=" * 60)
        logger.info(f"✓ Scraped {len(cars)} cars from AutoScout24")
        logger.info(f"✓ Saved to autoscout24_data.json")
        logger.info("=" * 60)
    else:
        logger.warning("No cars scraped")


if __name__ == "__main__":
    main()