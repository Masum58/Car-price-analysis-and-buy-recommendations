"""
Track dataset growth over time
"""
import json
from datetime import datetime
import os

print("\n" + "="*60)
print("📈 DATASET GROWTH TRACKER")
print("="*60 + "\n")

# Load current data
try:
    with open('cars_data_real_api_ready.json', 'r') as f:
        clean_cars = json.load(f)
    
    with open('cars_data.json', 'r') as f:
        all_cars = json.load(f)
    
    # Get stats
    total_scraped = len(all_cars)
    total_clean = len(clean_cars)
    quality_rate = (total_clean / total_scraped * 100) if total_scraped > 0 else 0
    
    print(f"📊 Current Status:")
    print(f"   Total Scraped: {total_scraped} cars")
    print(f"   Clean & Ready: {total_clean} cars")
    print(f"   Quality Rate: {quality_rate:.1f}%")
    
    # Save to log
    log_entry = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M'),
        'total_scraped': total_scraped,
        'total_clean': total_clean,
        'quality_rate': quality_rate
    }
    
    # Load or create log
    log_file = 'progress_log.json'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"\n✅ Progress logged!")
    
    # Show growth
    if len(logs) > 1:
        print(f"\n📈 Growth Since Start:")
        first = logs[0]
        current = logs[-1]
        
        growth = current['total_clean'] - first['total_clean']
        days = len(logs) - 1
        
        print(f"   Day 1: {first['total_clean']} cars")
        print(f"   Day {days+1}: {current['total_clean']} cars")
        print(f"   Growth: +{growth} cars (+{growth/first['total_clean']*100:.1f}%)")
        print(f"   Avg/day: +{growth/days:.1f} cars/day")
    
    print("\n" + "="*60 + "\n")
    
except Exception as e:
    print(f"❌ Error: {e}")