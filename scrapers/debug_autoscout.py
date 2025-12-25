"""
Debug AutoScout24.be - Find Working Selectors
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def debug_autoscout24():
    print("\n" + "="*60)
    print("🔍 DEBUGGING AUTOSCOUT24.BE")
    print("="*60 + "\n")
    
    # Setup
    options = Options()
    # NOT headless - we want to see
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    service = Service(r"C:\Users\masum\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://www.autoscout24.be/lst?atype=C&cy=B&sort=age"
        print(f"Loading: {url}\n")
        driver.get(url)
        
        print("Waiting 8 seconds...")
        time.sleep(8)
        
        print("\n" + "-"*60)
        print("PAGE ANALYSIS")
        print("-"*60 + "\n")
        
        # Page title
        print(f"Title: {driver.title}\n")
        
        # Save HTML
        with open('autoscout_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("✅ Saved: autoscout_page.html\n")
        
        # Test selectors
        print("Testing selectors:")
        print("-"*60)
        
        selectors = [
            "article",
            "a[href*='/angebote/']",
            "a[href*='/offer/']",
            "div[class*='ListItem']",
            "div[class*='list-item']",
            "[data-testid*='listing']",
            "[data-testid*='result']",
            "a[data-testid]",
            ".ListItem_article",
            ".cldt-summary-full-item"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"{selector:40s} → {len(elements):3d} found")
                
                if elements and len(elements) > 0:
                    # Show sample
                    sample = elements[0]
                    if sample.tag_name == 'a':
                        href = sample.get_attribute('href')
                        print(f"{'':40s}   Sample: {href[:60] if href else 'No href'}")
                    else:
                        text = sample.text[:50] if sample.text else "No text"
                        print(f"{'':40s}   Sample: {text}")
            except Exception as e:
                print(f"{selector:40s} → Error: {str(e)[:30]}")
        
        # Screenshot
        print("\n" + "-"*60)
        driver.save_screenshot("autoscout_screenshot.png")
        print("✅ Saved: autoscout_screenshot.png")
        
        # Check for blocking
        print("\n" + "-"*60)
        print("Checking for blocks:")
        print("-"*60)
        
        page_text = driver.page_source.lower()
        checks = ["captcha", "blocked", "access denied", "cookie", "consent"]
        
        for check in checks:
            if check in page_text:
                print(f"  ⚠️  Found: '{check}'")
        
        print("\n" + "="*60)
        print("FILES CREATED:")
        print("  • autoscout_page.html")
        print("  • autoscout_screenshot.png")
        print("\nCheck these to see what's on the page!")
        print("="*60 + "\n")
        
    finally:
        input("Press Enter to close...")
        driver.quit()

if __name__ == "__main__":
    debug_autoscout24()