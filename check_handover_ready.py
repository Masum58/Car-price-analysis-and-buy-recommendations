"""
✅ CLIENT HANDOVER CHECKLIST
============================
Run this before delivering to client
"""

import json
import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {filepath}")
    return exists

def check_env_file():
    """Check .env file for API keys"""
    print("\n" + "="*70)
    print("🔑 CHECKING API KEYS")
    print("="*70)
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    has_openai = 'OPENAI_API_KEY' in content
    has_thordata = 'THORDATA_API_KEY' in content
    
    print(f"{'✅' if has_openai else '❌'} OPENAI_API_KEY")
    print(f"{'✅' if has_thordata else '⚠️'} THORDATA_API_KEY (optional)")
    
    return has_openai

def check_data_files():
    """Check data files"""
    print("\n" + "="*70)
    print("📊 CHECKING DATA FILES")
    print("="*70)
    
    # Check real data
    has_real = check_file_exists('cars_data_real_api_ready.json', required=True)
    
    if has_real:
        with open('cars_data_real_api_ready.json', 'r', encoding='utf-8') as f:
            cars = json.load(f)
        print(f"   → {len(cars)} cars in API-ready dataset")
        
        if len(cars) < 10:
            print(f"   ⚠️ WARNING: Only {len(cars)} cars. Recommend 50+ for production.")
        else:
            print(f"   ✅ Good: {len(cars)} cars available")
    
    # Check if sample data is still being used
    has_sample = os.path.exists('cars_data_sample.json')
    if has_sample:
        print(f"⚠️ cars_data_sample.json (should not be used in production)")
    
    return has_real

def check_api_configuration():
    """Check API configuration"""
    print("\n" + "="*70)
    print("⚙️ CHECKING API CONFIGURATION")
    print("="*70)
    
    check_file_exists('app/main.py', required=True)
    check_file_exists('app/routes.py', required=True)
    check_file_exists('app/models.py', required=True)
    check_file_exists('app/ai_calculations.py', required=True)
    
    # Check if ai_calculations.py uses correct data file
    try:
        with open('app/ai_calculations.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'cars_data_real_api_ready.json' in content:
            print("✅ Using real data (cars_data_real_api_ready.json)")
        elif 'cars_data_api_ready.json' in content:
            print("⚠️ Using mixed data (cars_data_api_ready.json)")
            print("   → Recommend changing to cars_data_real_api_ready.json")
        else:
            print("❌ No data loading found in ai_calculations.py!")
            return False
        
        return True
    except:
        print("❌ Could not check ai_calculations.py")
        return False

def check_requirements():
    """Check requirements.txt"""
    print("\n" + "="*70)
    print("📦 CHECKING DEPENDENCIES")
    print("="*70)
    
    has_req = check_file_exists('requirements.txt', required=True)
    
    if has_req:
        with open('requirements.txt', 'r') as f:
            packages = f.readlines()
        print(f"   → {len(packages)} packages listed")
    
    return has_req

def check_scraper():
    """Check scraper"""
    print("\n" + "="*70)
    print("🕷️ CHECKING SCRAPER")
    print("="*70)
    
    has_scraper = check_file_exists('scrape_cars.py', required=True)
    
    if has_scraper:
        # Check if scraped data exists
        scraped = check_file_exists('cars_data.json', required=False)
        if scraped:
            with open('cars_data.json', 'r', encoding='utf-8') as f:
                cars = json.load(f)
            print(f"   → {len(cars)} cars in raw scraped data")
    
    return has_scraper

def test_data_quality():
    """Test data quality"""
    print("\n" + "="*70)
    print("🔍 TESTING DATA QUALITY")
    print("="*70)
    
    try:
        with open('cars_data_real_api_ready.json', 'r', encoding='utf-8') as f:
            cars = json.load(f)
        
        # Check completeness
        complete = 0
        for car in cars:
            if (car.get('brand') and 
                car.get('year_numeric') and 
                car.get('mileage_numeric') and 
                car.get('price_numeric')):
                complete += 1
        
        completeness = (complete / len(cars)) * 100 if cars else 0
        
        print(f"Data Completeness: {completeness:.1f}%")
        
        if completeness >= 90:
            print("✅ Excellent data quality")
        elif completeness >= 70:
            print("⚠️ Acceptable data quality")
        else:
            print("❌ Poor data quality - needs improvement")
        
        # Check for real sources
        real_sources = sum(1 for car in cars if 'scraped' in str(car.get('data_source', '')).lower())
        sample_sources = sum(1 for car in cars if 'sample' in str(car.get('data_source', '')).lower())
        
        print(f"\nData Sources:")
        print(f"  Real scraped: {real_sources} cars")
        print(f"  Sample data: {sample_sources} cars")
        
        if sample_sources > 0:
            print("⚠️ WARNING: Sample data detected! Not production ready.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking data: {e}")
        return False

def test_api_import():
    """Test if API can be imported"""
    print("\n" + "="*70)
    print("🧪 TESTING API IMPORT")
    print("="*70)
    
    try:
        from app.main import app
        print("✅ API imports successfully")
        return True
    except Exception as e:
        print(f"❌ API import failed: {e}")
        return False

def generate_summary():
    """Generate final summary"""
    print("\n" + "="*70)
    print("📋 PRE-HANDOVER SUMMARY")
    print("="*70)
    
    checks = {
        'env': check_env_file(),
        'data': check_data_files(),
        'api': check_api_configuration(),
        'requirements': check_requirements(),
        'scraper': check_scraper(),
        'quality': test_data_quality(),
        'import': test_api_import()
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    print(f"\nChecks Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED - READY FOR CLIENT HANDOVER!")
        print("\n📋 Final Steps:")
        print("1. ✅ Test API: uvicorn app.main:app --reload")
        print("2. ✅ Test endpoints in browser: http://127.0.0.1:8000/docs")
        print("3. ✅ Generate final report: python generate_full_report.py")
        print("4. ✅ Create deployment package")
        return True
    else:
        print("\n⚠️ SOME CHECKS FAILED - FIX BEFORE HANDOVER")
        print("\n🔧 Failed Checks:")
        for check, status in checks.items():
            if not status:
                print(f"   ❌ {check}")
        return False

def main():
    print("\n" + "="*70)
    print("🚀 CLIENT HANDOVER VERIFICATION")
    print("="*70)
    print("Checking if project is ready for client delivery...\n")
    
    ready = generate_summary()
    
    print("\n" + "="*70)
    
    if ready:
        print("✅ PROJECT READY FOR CLIENT")
    else:
        print("❌ PROJECT NOT READY - FIX ISSUES ABOVE")
    
    print("="*70 + "\n")
    
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()