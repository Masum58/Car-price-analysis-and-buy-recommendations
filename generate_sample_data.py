"""
Generate realistic sample car data for testing
Based on Belgian market prices
"""

import json
import random
from datetime import datetime, timedelta

# Realistic Belgian market data
CAR_DATABASE = [
    # BMW
    {"brand": "BMW", "model": "316d", "base_price": 15000, "year_range": (2015, 2018)},
    {"brand": "BMW", "model": "320d", "base_price": 22000, "year_range": (2017, 2020)},
    {"brand": "BMW", "model": "X1", "base_price": 28000, "year_range": (2018, 2021)},
    {"brand": "BMW", "model": "X3", "base_price": 35000, "year_range": (2019, 2022)},
    
    # Mercedes
    {"brand": "Mercedes", "model": "A180", "base_price": 18000, "year_range": (2016, 2019)},
    {"brand": "Mercedes", "model": "C200", "base_price": 25000, "year_range": (2017, 2020)},
    {"brand": "Mercedes", "model": "GLA", "base_price": 27000, "year_range": (2018, 2021)},
    
    # Audi
    {"brand": "Audi", "model": "A3", "base_price": 19000, "year_range": (2016, 2019)},
    {"brand": "Audi", "model": "A4", "base_price": 26000, "year_range": (2017, 2020)},
    {"brand": "Audi", "model": "Q3", "base_price": 29000, "year_range": (2018, 2021)},
    
    # Volkswagen
    {"brand": "Volkswagen", "model": "Golf", "base_price": 14000, "year_range": (2016, 2019)},
    {"brand": "Volkswagen", "model": "Passat", "base_price": 17000, "year_range": (2016, 2019)},
    {"brand": "Volkswagen", "model": "Tiguan", "base_price": 24000, "year_range": (2017, 2020)},
    
    # Toyota
    {"brand": "Toyota", "model": "Corolla", "base_price": 16000, "year_range": (2017, 2020)},
    {"brand": "Toyota", "model": "RAV4", "base_price": 25000, "year_range": (2018, 2021)},
    {"brand": "Toyota", "model": "Yaris", "base_price": 11000, "year_range": (2016, 2019)},
    
    # Tesla
    {"brand": "Tesla", "model": "Model 3", "base_price": 38000, "year_range": (2019, 2022)},
    
    # Renault
    {"brand": "Renault", "model": "Clio", "base_price": 9000, "year_range": (2016, 2019)},
    {"brand": "Renault", "model": "Megane", "base_price": 12000, "year_range": (2016, 2019)},
    
    # Peugeot
    {"brand": "Peugeot", "model": "208", "base_price": 10000, "year_range": (2016, 2019)},
    {"brand": "Peugeot", "model": "3008", "base_price": 18000, "year_range": (2017, 2020)},
]

def generate_car_listing(car_template):
    """Generate a realistic car listing"""
    
    # Random year within range
    year = random.randint(car_template["year_range"][0], car_template["year_range"][1])
    
    # Calculate age
    age = 2025 - year
    
    # Price depreciation based on age
    depreciation_rate = 0.12  # 12% per year
    price = car_template["base_price"] * ((1 - depreciation_rate) ** age)
    
    # Add some random variation (±15%)
    price = price * random.uniform(0.85, 1.15)
    price = round(price / 100) * 100  # Round to nearest 100
    
    # Mileage (average 15,000 km/year with variation)
    avg_km_per_year = random.randint(12000, 20000)
    mileage = age * avg_km_per_year
    mileage = round(mileage / 1000) * 1000  # Round to nearest 1000
    
    # Random fuel type
    fuel_types = ["diesel", "petrol", "hybrid", "electric"]
    if car_template["brand"] == "Tesla":
        fuel_type = "electric"
    else:
        fuel_type = random.choice(fuel_types[:3])  # No electric for others
    
    # Build title
    title = f"{car_template['brand']} {car_template['model']} {year}"
    
    # Random scraped date (within last 30 days)
    days_ago = random.randint(0, 30)
    scraped_date = datetime.now() - timedelta(days=days_ago)
    
    return {
        "title": title,
        "brand": car_template["brand"],
        "year_numeric": year,
        "mileage_numeric": mileage,
        "price_numeric": price,
        "fuel_type": fuel_type,
        "url": f"https://www.2dehands.be/car/{car_template['brand'].lower()}-{car_template['model'].lower()}-{year}",
        "source": "sample_data",
        "scraped_at": scraped_date.isoformat()
    }


def generate_dataset(num_cars: int = 100) -> list:
    """Generate a full dataset"""
    dataset = []
    
    for i in range(num_cars):
        # Pick random car template
        template = random.choice(CAR_DATABASE)
        car = generate_car_listing(template)
        dataset.append(car)
    
    return dataset


def main():
    """Generate and save sample data"""
    print("=" * 60)
    print("Generating Realistic Sample Car Data")
    print("=" * 60)
    
    # Generate 100 cars
    cars = generate_dataset(100)
    
    # Save to JSON
    with open('cars_data_sample.json', 'w', encoding='utf-8') as f:
        json.dump(cars, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Generated {len(cars)} realistic car listings")
    print(f"✓ Saved to 'cars_data_sample.json'")
    
    # Show stats
    brands = {}
    for car in cars:
        brand = car['brand']
        brands[brand] = brands.get(brand, 0) + 1
    
    print(f"\nBrand Distribution:")
    for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
        print(f"  {brand}: {count} cars")
    
    print("\nPrice Range:")
    prices = [car['price_numeric'] for car in cars]
    print(f"  Min: €{min(prices):,.0f}")
    print(f"  Max: €{max(prices):,.0f}")
    print(f"  Avg: €{sum(prices)/len(prices):,.0f}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()