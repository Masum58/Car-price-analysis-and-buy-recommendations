# =========================
# STANDARD LIBRARIES
# =========================
import os
import json
from datetime import datetime
from typing import List, Optional

# =========================
# THIRD-PARTY LIBRARIES
# =========================
import joblib
import openai
from dotenv import load_dotenv
import numpy as np


# =========================
# ENVIRONMENT & CONFIGURATION
# =========================
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

# =========================
# PROJECT PATHS (CRITICAL)
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR, "data", "raw", "cars_data.json"
)

ML_MODEL_PATH = os.path.join(
    BASE_DIR, "data", "ml_models", "ml_model.joblib"
)


# =========================
# BRAND CATEGORIZATION
# =========================
PREMIUM_BRANDS = ["BMW", "MERCEDES", "AUDI", "TESLA", "PORSCHE", "LEXUS"]
MID_TIER_BRANDS = ["VOLKSWAGEN", "TOYOTA", "HONDA", "MAZDA", "SUBARU"]
BUDGET_BRANDS = ["DACIA", "SKODA", "SEAT", "KIA", "HYUNDAI"]


# =========================
# HELPER FUNCTIONS
# =========================
def calculate_age(year: Optional[int]) -> int:
    if not isinstance(year, int):
        return 0
    return max(0, datetime.now().year - year)


def is_premium_brand(brand: Optional[str]) -> bool:
    if not brand:
        return False
    return brand.upper() in PREMIUM_BRANDS


# =========================
# DATA LOADER
# =========================
def load_car_data() -> List[dict]:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Car data not found: {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# MARKET VALUE ESTIMATION
# =========================
def estimate_market_value(car_data: dict) -> float:
    price = car_data.get("price_numeric") or 20000
    brand = car_data.get("brand", "")
    year = car_data.get("year_numeric")
    mileage = car_data.get("mileage_numeric") or 0
    fuel_type = (car_data.get("fuel_type") or "").lower()

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

    return round(
        max(base_value * 0.85, min(base_value * 1.2, estimated_value)),
        2
    )


# =========================
# RISK SCORE
# =========================
def calculate_risk_score(car_data: dict) -> float:
    age = calculate_age(car_data.get("year_numeric"))
    mileage = car_data.get("mileage_numeric") or 0
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
    price = car_data.get("price_numeric") or 0
    estimated_value = estimate_market_value(car_data)
    risk_score = calculate_risk_score(car_data)

    age = calculate_age(car_data.get("year_numeric"))
    mileage = car_data.get("mileage_numeric") or 0

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
# ML PRICE PREDICTION (SAFE)
# =========================
def predict_car_price_ml(car_data: dict) -> float:
    if not os.path.exists(ML_MODEL_PATH):
        raise FileNotFoundError("ML model not found")

    model = joblib.load(ML_MODEL_PATH)

    current_year = datetime.now().year

    year = car_data.get("year_numeric")
    if not isinstance(year, int):
        year = current_year

    age = max(1, current_year - year)

    mileage = car_data.get("mileage_numeric")
    if not isinstance(mileage, (int, float)):
        mileage = 0

    mileage_per_year = mileage / age

    brand_encoded = hash(car_data.get("brand", "unknown")) % 100
    fuel_encoded = hash(car_data.get("fuel_type", "unknown")) % 10

    X = np.array([[
        brand_encoded,
        age,
        mileage,
        fuel_encoded,
        mileage_per_year
    ]])

    raw_price = model.predict(X)[0]
    safe_price = max(0, raw_price)

    base_price = car_data.get("price_numeric") or 20000
    final_price = max(
        base_price * 0.5,
        min(base_price * 1.5, safe_price)
    )

    return round(float(final_price), 2)


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
# ANALYSIS HELPERS (REQUIRED FOR API)
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
# EXPORTS
# =========================
__all__ = [
    "load_car_data",
    "predict_car_price_ml",
    "estimate_market_value",
    "calculate_profit_and_recommendation",
    "calculate_risk_score",
    "analyze_multiple_cars",
    "compare_cars",
    "get_ai_suggestion",
]
