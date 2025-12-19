from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

print("Testing Selenium setup...")

try:
    print("1. Installing Chrome driver...")
    service = Service(ChromeDriverManager().install())
    
    print("2. Setting up options...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    print("3. Starting Chrome...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("4. Loading test page...")
    driver.get("https://www.google.com")
    
    print(f"✓ SUCCESS! Page title: {driver.title}")
    
    driver.quit()
    print("✓ Test complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
