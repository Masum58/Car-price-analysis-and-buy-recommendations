import json

from app.ai_calculations import (
    normalize_scraped_car,
    calculate_profit_and_recommendation
)

# Load raw scraped data
with open("scrapers/output.json", "r", encoding="utf-8") as f:
    raw_cars = json.load(f)

print(f"Total raw cars: {len(raw_cars)}\n")

analyzed_cars = []

for idx, raw_car in enumerate(raw_cars, start=1):
    # STEP 1: normalize
    clean_car = normalize_scraped_car(raw_car)

    # STEP 2: profit + risk
    analysis = calculate_profit_and_recommendation(clean_car)

    final_car = {
        **clean_car,
        **analysis
    }

    analyzed_cars.append(final_car)

    # Print first 3 cars only (readable output)
    if idx <= 3:
        print(f"--- Car #{idx} ---")
        for k, v in final_car.items():
            print(f"{k}: {v}")
        print()

print(f"Analysis completed for {len(analyzed_cars)} cars.")
