import json

from app.ai_calculations import (
    normalize_scraped_car,
    calculate_profit_and_recommendation,
    rank_cars_by_investment_quality
)

with open("scrapers/output.json", "r", encoding="utf-8") as f:
    raw_cars = json.load(f)

analyzed = []

for raw in raw_cars:
    clean = normalize_scraped_car(raw)
    analysis = calculate_profit_and_recommendation(clean)
    analyzed.append({**clean, **analysis})

ranked = rank_cars_by_investment_quality(analyzed)

print("TOP 5 INVESTMENT CARS:\n")

for car in ranked[:5]:
    print(
        f"{car['title']} | "
        f"profit={car['profit']} | "
        f"risk={car['risk_score']} | "
        f"score={car['investment_score']}"
    )
