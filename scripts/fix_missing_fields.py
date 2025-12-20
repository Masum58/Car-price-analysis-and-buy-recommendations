# scripts/fix_missing_fields.py

import json
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "cars_data.json")

BRANDS = [
    "Renault",
    "BMW",
    "Volkswagen",
    "VW",
    "Peugeot",
    "Citroen",
    "Fiat",
    "Ford"
]

with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)

fixed_brand = 0
fixed_price = 0

for car in data:
    title = car.get("title", "").lower()

    # Fix brand
    if not car.get("brand"):
        for b in BRANDS:
            if b.lower() in title:
                car["brand"] = b
                fixed_brand += 1
                break

    # Fix price (only if missing)
    if not car.get("price_numeric"):
        m = re.search(r"€\s?(\d+)", title)
        if m:
            car["price_numeric"] = float(m.group(1))
            fixed_price += 1

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Auto-fix completed")
print(f"   • Brand fixed : {fixed_brand}")
print(f"   • Price fixed : {fixed_price}")
print(f"📄 File updated : {DATA_PATH}")
