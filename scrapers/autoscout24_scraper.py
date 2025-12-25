"""
AutoScout24 Selenium Scraper
Human-like browser scraping (VPN friendly)
"""

import json
import time
import random
import logging
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoScout24SeleniumScraper:

    def __init__(self):
        self.base_url = "https://www.autoscout24.be"

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    # --------------------------------------------------
    # UTILS
    # --------------------------------------------------
    def human_sleep(self, a=2, b=4):
        time.sleep(random.uniform(a, b))

    # --------------------------------------------------
    # SEARCH PAGE
    # --------------------------------------------------
    def collect_listing_urls(self, pages=2):
        urls = set()

        for page in range(1, pages + 1):
            url = f"{self.base_url}/lst?atype=C&page={page}"
            logger.info(f"Opening search page: {url}")

            self.driver.get(url)
            self.human_sleep(5, 8)

            # Scroll
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            self.human_sleep(3, 5)

            cards = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/offer/']")
            for c in cards:
                link = c.get_attribute("href")
                if link:
                    urls.add(link)

            logger.info(f"Page {page}: total URLs so far = {len(urls)}")

        return list(urls)

    # --------------------------------------------------
    # DETAIL PAGE
    # --------------------------------------------------
    def scrape_detail_page(self, url):
        logger.info(f"Scraping detail: {url}")
        self.driver.get(url)
        self.human_sleep(4, 6)

        data = {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "source": "autoscout24_selenium"
        }

        # Title
        try:
            data["title"] = self.driver.find_element(By.TAG_NAME, "h1").text
        except:
            data["title"] = None

        # Price
        try:
            price = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='price']")
            data["price_text"] = price.text
            data["price_numeric"] = int(
                price.text.replace("€", "").replace(".", "").replace(",", "").strip()
            )
        except:
            data["price_numeric"] = None

        # Key-value specs
        specs = {}
        rows = self.driver.find_elements(By.CSS_SELECTOR, "dl")
        for r in rows:
            try:
                k = r.find_element(By.TAG_NAME, "dt").text.strip().lower()
                v = r.find_element(By.TAG_NAME, "dd").text.strip()
                specs[k] = v
            except:
                continue

        data["gearbox"] = specs.get("gearbox type")
        data["fuel_type"] = specs.get("fuel")
        data["power"] = specs.get("power")
        data["first_registration"] = specs.get("first registration")
        data["seats"] = specs.get("number of seats")

        # Images
        images = []
        imgs = self.driver.find_elements(By.CSS_SELECTOR, "img")
        for img in imgs:
            src = img.get_attribute("src")
            if src and "images" in src:
                images.append(src)

        data["images"] = list(set(images))

        # Equipment / features
        features = []
        try:
            feature_blocks = self.driver.find_elements(By.CSS_SELECTOR, "li")
            for f in feature_blocks:
                t = f.text.strip()
                if 3 < len(t) < 60:
                    features.append(t)
        except:
            pass

        data["features"] = list(set(features))

        # Seller info
        try:
            data["seller_name"] = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='seller-name']"
            ).text
        except:
            data["seller_name"] = None

        try:
            data["seller_location"] = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='seller-address']"
            ).text
        except:
            data["seller_location"] = None

        # Phone (best effort)
        try:
            phone_btn = self.driver.find_element(By.CSS_SELECTOR, "button")
            phone_btn.click()
            self.human_sleep(2, 3)
            data["seller_phone"] = self.driver.find_element(By.TAG_NAME, "a").text
        except:
            data["seller_phone"] = None

        return data

    # --------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------
    def run(self, pages=2):
        all_data = []

        urls = self.collect_listing_urls(pages)
        logger.info(f"Total listing URLs collected: {len(urls)}")

        for i, url in enumerate(urls, 1):
            try:
                car = self.scrape_detail_page(url)
                all_data.append(car)
                logger.info(f"[{i}/{len(urls)}] ✓ {car.get('title')}")
            except Exception as e:
                logger.error(f"Error scraping detail: {e}")

        return all_data

    def close(self):
        self.driver.quit()


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
if __name__ == "__main__":
    scraper = AutoScout24SeleniumScraper()
    cars = scraper.run(pages=2)

    if cars:
        with open("autoscout24_selenium_data.json", "w", encoding="utf-8") as f:
            json.dump(cars, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Saved {len(cars)} cars to autoscout24_selenium_data.json")
    else:
        logger.warning("❌ No data scraped")

    scraper.close()
