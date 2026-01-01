"""
AutoScout24 Working Scraper - Fixed Version
Handles session errors, better stability
"""

import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

BASE_URL = "https://www.autoscout24.com"
LISTING_URL = "https://www.autoscout24.com/lst?sort=standard"
OUTPUT_FILE = "output.json"
MAX_NEW_CARS = 5
BREAK_TIME = 30
MAX_PAGES = 30


# -------------------------
# Cookie handler
# -------------------------
def handle_cookie_consent(driver, timeout=10):
    """Handle cookie consent popup"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[class^='_consent-accept']")
            )
        ).click()
        time.sleep(1)
    except:
        pass


# -------------------------
# Check if session valid
# -------------------------
def is_session_valid(driver):
    """Check if driver session is still valid"""
    try:
        driver.current_url
        return True
    except:
        return False


# -------------------------
# Force listing render with checks
# -------------------------
def force_listing_render(driver):
    """Scroll page to trigger JS hydration - with safety checks"""
    try:
        if not is_session_valid(driver):
            print("  ⚠️  Session invalid, skipping scroll")
            return
        
        # Small scroll
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)
        
        # Full scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    except Exception as e:
        print(f"  ⚠️  Scroll error (non-critical): {e}")


# -------------------------
# Listing page scraper
# -------------------------
def scrape_listing(driver):
    """Scrape car listings from current page"""
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "article.cldt-summary-full-item")
            )
        )
    except Exception as e:
        print(f"  ⚠️  No listings found: {e}")
        return []

    cars = []
    cards = driver.find_elements(By.CSS_SELECTOR, "article.cldt-summary-full-item")
    
    print(f"  ✓ Found {len(cards)} car cards")

    for i, card in enumerate(cards, 1):
        try:
            link = card.find_element(By.CSS_SELECTOR, 'a[href^="/offers/"]')
            details_url = urljoin(BASE_URL, link.get_attribute("href"))

            title_spans = card.find_elements(By.CSS_SELECTOR, "h2 span")
            car_title = title_spans[0].text.strip() if len(title_spans) > 0 else "N/A"
            car_subtitle = title_spans[1].text.strip() if len(title_spans) > 1 else "N/A"

            try:
                price = card.find_element(
                    By.CSS_SELECTOR, 'span[class^="CurrentPrice_price"]'
                ).text.strip()
            except:
                price = "N/A"

            cars.append({
                "car_title": car_title,
                "car_subtitle": car_subtitle,
                "price": price,
                "details_url": details_url,
            })

        except Exception as e:
            print(f"    ⚠️  Card {i} error: {e}")
            continue

    return cars


# -------------------------
# Generic DL section scraper
# -------------------------
def scrape_dl_section(driver, section_id, field_map):
    """Scrape specification section"""
    data = {v: "N/A" for v in field_map.values()}

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"#{section_id} dl"))
        )
    except:
        return data

    dts = driver.find_elements(By.CSS_SELECTOR, f"#{section_id} dl dt")

    for dt in dts:
        key = dt.text.strip()
        try:
            dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
            value = dd.text.strip()
        except:
            continue

        if key in field_map:
            data[field_map[key]] = value

    return data


# -------------------------
# Seller info
# -------------------------
def scrape_seller(driver):
    """Scrape seller information"""
    seller = {
        "company_name": "N/A",
        "contact_name": "N/A",
        "location": "N/A",
        "phone": [],
    }

    try:
        seller["company_name"] = driver.find_element(
            By.CSS_SELECTOR,
            'div.RatingsAndCompanyName_dealer__EaECM [data-cs-mask="true"]',
        ).text.strip()
    except:
        pass

    try:
        seller["contact_name"] = driver.find_element(
            By.CSS_SELECTOR, 'span[class^="Contact_contactName"]'
        ).text.strip()
    except:
        pass

    try:
        seller["location"] = driver.find_element(
            By.CSS_SELECTOR, "button.Department_link__xMUEe"
        ).text.strip()
    except:
        pass

    try:
        driver.find_element(By.ID, "vendor-section-call-button").click()
        time.sleep(1)
        phones = driver.find_elements(By.CSS_SELECTOR, 'a[href^="tel:"]')
        seller["phone"] = [p.text for p in phones if p.text]
    except:
        pass

    return seller


# -------------------------
# Images (max quality, unique)
# -------------------------
def extract_image_id(url):
    """Extract unique image ID from URL"""
    return url.split("/")[-2]


def resolution_score(url):
    """Calculate image resolution score"""
    try:
        w, h = url.split("/")[-1].split(".")[0].split("x")
        return int(w) * int(h)
    except:
        return 0


def scrape_images(driver, wait, max_images=15):
    """Scrape high-quality images"""
    images = {}

    try:
        next_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.image-gallery-right-nav")
            )
        )
    except:
        return []

    for _ in range(max_images):
        time.sleep(0.2)

        sources = driver.find_elements(
            By.CSS_SELECTOR, "div.image-gallery-slide picture source"
        )

        for src in sources:
            srcset = src.get_attribute("srcset")
            if not srcset:
                continue

            for item in srcset.split(","):
                url = item.strip().split(" ")[0]
                img_id = extract_image_id(url)
                score = resolution_score(url)

                if img_id not in images or score > images[img_id]["score"]:
                    images[img_id] = {"url": url, "score": score}

        if len(images) >= max_images:
            break
        
        try:
            next_btn.click()
        except:
            break

    return [v["url"] for v in images.values()][:max_images]


# -------------------------
# Load existing JSON
# -------------------------
def load_existing():
    """Load existing scraped data"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            print("  ⚠️  Could not load existing JSON")
            return []
    return []


# -------------------------
# Pagination URL helper
# -------------------------
def build_page_url(base_url, page):
    """Build paginated URL"""
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs["page"] = [str(page)]
    return parsed._replace(query=urlencode(qs, doseq=True)).geturl()


# -------------------------
# Visual sleep function
# -------------------------
def visual_sleep(seconds):
    """Sleep with countdown display"""
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        print(f"⏸️  Break time: {mins:02d}:{secs:02d} remaining", end="\r")
        time.sleep(1)
    print("\n▶️  Break finished. Resuming scraping...\n")


# -------------------------
# Save data safely
# -------------------------
def save_data(results):
    """Save data to JSON file"""
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"  ❌ Save error: {e}")
        return False


# -------------------------
# MAIN function
# -------------------------
def main():
    """Main scraping function"""
    print("\n" + "="*60)
    print("🚗 AutoScout24 Scraper - Starting")
    print("="*60 + "\n")
    
    # Setup Chrome options
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Initialize driver
    driver = None
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        wait = WebDriverWait(driver, 20)
        
        print("✅ Chrome driver initialized\n")
        
        existing_data = load_existing()
        existing_urls = {
            item["details_url"] for item in existing_data if "details_url" in item
        }
        
        print(f"📂 Loaded {len(existing_data)} existing cars\n")

        results = existing_data
        total_new_scraped = 0

        for page in range(1, MAX_PAGES + 1):
            page_url = build_page_url(LISTING_URL, page)
            print(f"📄 Opening page {page}: {page_url[:80]}...")

            try:
                driver.get(page_url)
                handle_cookie_consent(driver)
                force_listing_render(driver)
                
                cars = scrape_listing(driver)
                print(f"➡  Found {len(cars)} cars on page {page}\n")
                
                if not cars:
                    print("  ⚠️  No cars found, stopping")
                    break

            except Exception as e:
                print(f"  ❌ Page {page} error: {e}\n")
                continue

            for idx, car in enumerate(cars, 1):
                if car["details_url"] in existing_urls:
                    print(f"  [{idx}/{len(cars)}] ⏭️  Skipped (already exists)")
                    continue

                print(f"  [{idx}/{len(cars)}] 🔍 Scraping: {car['details_url'][:60]}...")
                
                try:
                    driver.get(car["details_url"])
                    handle_cookie_consent(driver)
                    time.sleep(2)

                    data = {
                        "car_title": car["car_title"],
                        "car_subtitle": car["car_subtitle"],
                        "details_url": car["details_url"],
                        "price": car["price"],
                        "all_images": scrape_images(driver, wait),
                        "Basic_Data": scrape_dl_section(
                            driver,
                            "basic-details-section",
                            {
                                "Body type": "Body_type",
                                "Vehicle type": "Vehicle_type",
                                "Drivetrain": "Drivetrain",
                                "Seats": "Seats",
                                "Doors": "Doors",
                                "Country version": "Country_version",
                                "Offer Number": "Offer_Number",
                                "Model code": "Model_Code",
                            },
                        ),
                        "Vehicle_History": scrape_dl_section(
                            driver,
                            "listing-history-section",
                            {
                                "Mileage": "Mileage",
                                "First registration": "First_registration",
                                "Previous owner": "Previous_owner",
                                "Full service history": "Full_service_history",
                                "General inspection": "General_inspection",
                            },
                        ),
                        "Technical_Data": scrape_dl_section(
                            driver,
                            "technical-details-section",
                            {
                                "Power": "Power",
                                "Gearbox": "Gearbox",
                                "Engine size": "Engine_size",
                                "Cylinders": "Cylinders",
                                "Gears": "Gears",
                                "Empty weight": "Empty_weight",
                            },
                        ),
                        "Energy_Consumption": scrape_dl_section(
                            driver,
                            "environment-details-section",
                            {
                                "Emission class": "Emission_class",
                                "Fuel type": "Fuel_type",
                                "Fuel consumption": "Fuel_consumption",
                                "CO₂-emissions": "CO₂_emissions",
                            },
                        ),
                        "Colour_and_Upholstery": scrape_dl_section(
                            driver,
                            "color-section",
                            {
                                "Colour": "Colour",
                                "Paint": "Paint",
                                "Manufacturer colour": "Manufacturer_colour",
                                "Upholstery colour": "Upholstery_colour",
                                "Upholstery": "Upholstery",
                            },
                        ),
                        "seller_info": scrape_seller(driver),
                    }

                    results.append(data)
                    existing_urls.add(car["details_url"])
                    total_new_scraped += 1

                    # Save after each car
                    if save_data(results):
                        print(f"    ✅ Saved! New total: {total_new_scraped}")
                    else:
                        print(f"    ⚠️  Save failed but continuing")

                    # Break after every N cars
                    if total_new_scraped > 0 and total_new_scraped % MAX_NEW_CARS == 0:
                        print(f"\n⏸️  {MAX_NEW_CARS} new cars scraped. Taking a break...\n")
                        visual_sleep(BREAK_TIME)
                
                except Exception as e:
                    print(f"    ❌ Scraping error: {e}")
                    continue
            
            # Check if we should stop
            if total_new_scraped >= MAX_NEW_CARS * 2:  # Stop after 10 cars
                print(f"\n🎯 Reached {total_new_scraped} cars, stopping")
                break

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    
    finally:
        if driver:
            try:
                driver.quit()
                print("\n🔒 Browser closed")
            except:
                pass
    
    print("\n" + "="*60)
    print("🎉 Scraping finished")
    print("="*60)
    print(f"  Total new cars: {total_new_scraped}")
    print(f"  Output file: {OUTPUT_FILE}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()