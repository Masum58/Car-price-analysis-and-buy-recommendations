import json
from app.ai_calculations import normalize_scraped_car

with open("scrapers/output.json", "r") as f:
    cars = json.load(f)

clean_car = normalize_scraped_car(cars[0])
print(clean_car)
