# =========================
# STANDARD LIBRARIES
# =========================
import os
from datetime import datetime
from typing import List, Optional
import json

# =========================
# THIRD-PARTY LIBRARIES
# =========================
import joblib
import openai
from dotenv import load_dotenv


# =========================
# ENVIRONMENT & CONFIGURATION
# =========================
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

ML_MODEL_PATH = "ml_model.joblib"


# =========================
# BRAND CATEGORIZATION
# =========================
PREMIUM_BRANDS = ["BMW", "Mercedes", "Audi", "Tesla", "Porsche", "Lexus"]
MID_TIER_BRANDS = ["Volkswagen", "Toyota", "Honda", "Mazda", "Subaru"]
BUDGET_BRANDS = ["Dacia", "Skoda", "Seat", "Kia", "Hyundai"]


# =========================
# HELPER FUNCTIONS
# =========================
def calculate_age(year: Optional[int]) -> int:
    if not year:
        return 0
    return max(0, datetime.now().year - year)


def is_premium_brand(brand: Optional[str]) -> bool:
    if not brand:
        return False
    return brand.upper() in [b.upper() for b in PREMIUM_BRANDS]


# =========================
# DATA LOADER
# =========================
def load_car_data():
    """Load REAL scraped car data only (no sample data)"""
    import json
    with open('cars_data_real_api_ready.json', 'r', encoding='utf-8') as f:
        return json.load(f)


# =========================
# MARKET VALUE ESTIMATION
# =========================
def estimate_market_value(car_data: dict) -> float:
    price = car_data.get("price_numeric", 20000)
    brand = car_data.get("brand", "")
    year = car_data.get("year_numeric")
    mileage = car_data.get("mileage_numeric", 0)
    fuel_type = car_data.get("fuel_type", "").lower()

    base_value = price if price > 0 else 20000

    if is_premium_brand(brand):
        brand_adjustment = base_value * 0.10
    elif brand.upper() in MID_TIER_BRANDS:
        brand_adjustment = base_value * 0.05
    elif brand.upper() in BUDGET_BRANDS:
        brand_adjustment = -base_value * 0.05
    else:
        brand_adjustment = 0

    age = calculate_age(year)
    expected_mileage = age * 15000
    mileage_diff = mileage - expected_mileage

    mileage_adjustment = (
        -(mileage_diff / 10000) * 500
        if mileage_diff > 0
        else (abs(mileage_diff) / 10000) * 300
    )

    if age <= 2:
        age_adjustment = base_value * 0.05
    elif age <= 5:
        age_adjustment = 0
    elif age <= 10:
        age_adjustment = -base_value * 0.05
    else:
        age_adjustment = -base_value * 0.10

    if "electric" in fuel_type or "hybrid" in fuel_type:
        fuel_adjustment = base_value * 0.08
    elif "diesel" in fuel_type:
        fuel_adjustment = -base_value * 0.03
    else:
        fuel_adjustment = 0

    estimated_value = (
        base_value
        + brand_adjustment
        + mileage_adjustment
        + age_adjustment
        + fuel_adjustment
    )

    return round(max(base_value * 0.85, min(base_value * 1.2, estimated_value)), 2)


# =========================
# RISK SCORE
# =========================
def calculate_risk_score(car_data: dict) -> float:
    age = calculate_age(car_data.get("year_numeric"))
    mileage = car_data.get("mileage_numeric", 0)
    brand = car_data.get("brand", "")

    risk = 0.0

    if age > 15:
        risk += 4
    elif age > 10:
        risk += 2.5
    elif age > 5:
        risk += 1

    if mileage > 200000:
        risk += 4
    elif mileage > 150000:
        risk += 2.5
    elif mileage > 100000:
        risk += 1

    if is_premium_brand(brand):
        risk -= 1
    elif brand.upper() in BUDGET_BRANDS:
        risk += 1

    return max(0, min(10, round(risk, 2)))


# =========================
# PROFIT & RECOMMENDATION
# =========================
def calculate_profit_and_recommendation(car_data: dict) -> dict:
    price = car_data.get("price_numeric", 0)
    estimated_value = estimate_market_value(car_data)
    risk_score = calculate_risk_score(car_data)

    age = calculate_age(car_data.get("year_numeric"))
    mileage = car_data.get("mileage_numeric", 0)

    total_costs = 300 + min(age * 50, 500) + (mileage / 100000) * 200
    profit = estimated_value - (price + total_costs)

    if profit > 3000 and risk_score < 3:
        rec = "STRONG BUY"
    elif profit > 1500 and risk_score < 5:
        rec = "BUY"
    elif profit > 500:
        rec = "CONSIDER"
    elif profit > -500:
        rec = "FAIR DEAL"
    else:
        rec = "DON'T BUY"

    return {
        "estimated_market_value": estimated_value,
        "profit": round(profit, 2),
        "risk_score": risk_score,
        "recommendation": rec,
    }


# =========================
# ANALYSIS
# =========================
def analyze_car(car_data: dict) -> dict:
    analysis = calculate_profit_and_recommendation(car_data)
    return {
        **car_data,
        "age": calculate_age(car_data.get("year_numeric")),
        "is_premium": is_premium_brand(car_data.get("brand")),
        **analysis,
    }


def analyze_multiple_cars(cars: List[dict]) -> List[dict]:
    return [analyze_car(car) for car in cars]


# =========================
# CAR COMPARISON
# =========================
def compare_cars(cars: List[dict]) -> dict:
    analyzed = analyze_multiple_cars(cars)

    by_profit = sorted(analyzed, key=lambda x: x["profit"], reverse=True)
    by_risk = sorted(analyzed, key=lambda x: x["risk_score"])

    best_overall = max(
        analyzed,
        key=lambda x: x["profit"] - x["risk_score"] * 500,
        default=None,
    )

    return {
        "all_cars": analyzed,
        "best_by_profit": by_profit[0] if by_profit else None,
        "best_by_risk": by_risk[0] if by_risk else None,
        "best_overall_deal": best_overall,
    }


# =========================
# AI SUGGESTION
# =========================
async def get_ai_suggestion(prompt: str, budget: Optional[float] = None) -> str:
    try:
        if budget:
            prompt += f"\nBudget: €{budget}"

        client = openai.OpenAI(api_key=openai.api_key)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a car buying assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=400,
        )

        return response.choices[0].message.content
    except Exception as e:
        return str(e)


# =========================
# ML PRICE PREDICTION
# =========================
def predict_car_price_ml(car_data: dict) -> float:
    """
    Predict car price using trained ML model.
    Feature order MUST match training exactly.
    """

    if not os.path.exists(ML_MODEL_PATH):
        raise FileNotFoundError("ML model not found")

    model = joblib.load(ML_MODEL_PATH)

    # ----------------------------
    # Feature engineering (SAME AS TRAINING)
    # ----------------------------
    current_year = datetime.now().year
    year = car_data.get("year_numeric", current_year)
    age = max(0, current_year - year)

    mileage = car_data.get("mileage_numeric", 0)
    mileage_per_year = mileage / max(age, 1)

    # Brand encoding (simple fixed map)
    brand_map = {
        "BMW": 0,
        "AUDI": 1,
        "MERCEDES": 2,
        "TOYOTA": 3,
        "HONDA": 4,
        "VOLKSWAGEN": 5,
        "TESLA": 6,
        "OTHER": 7
    }
    brand = car_data.get("brand", "").upper()
    brand_encoded = brand_map.get(brand, brand_map["OTHER"])

    fuel_map = {
        "petrol": 0,
        "diesel": 1,
        "hybrid": 2,
        "electric": 3
    }
    fuel_encoded = fuel_map.get(
        car_data.get("fuel_type", "").lower(),
        0
    )

    # 🔥 EXACT SAME ORDER AS TRAINING
    X = [[
        brand_encoded,
        age,
        mileage,
        fuel_encoded,
        mileage_per_year
    ]]

    # ----------------------------
    # Prediction
    # ----------------------------
    raw_price = model.predict(X)[0]
    print("RAW ML OUTPUT:", raw_price)

    # Safety: no negative prices
    safe_price = max(0, raw_price)

    # Business bounds
    base_price = car_data.get("price_numeric", 20000)
    final_price = max(
        base_price * 0.5,
        min(base_price * 1.5, safe_price)
    )

    print("FINAL PRICE:", final_price)

    return round(float(final_price), 2)



# =========================
# EXPLICIT EXPORTS
# =========================
__all__ = [
    "analyze_multiple_cars",
    "compare_cars",
    "get_ai_suggestion",
    "load_car_data",
    "predict_car_price_ml",
]
