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
from dotenv import load_dotenv
import numpy as np

# =========================
# ENVIRONMENT & CONFIGURATION
# =========================
load_dotenv()

# =========================
# PROJECT PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "cars_data.json")
ML_MODEL_PATH = os.path.join(BASE_DIR, "data", "ml_models", "ml_model.joblib")

# =========================
# BRAND GROUPS
# =========================
PREMIUM_BRANDS = ["BMW", "MERCEDES", "AUDI", "TESLA", "PORSCHE", "LEXUS"]
MID_TIER_BRANDS = ["VOLKSWAGEN", "TOYOTA", "HONDA", "MAZDA", "SUBARU"]
BUDGET_BRANDS = ["DACIA", "SKODA", "SEAT", "KIA", "HYUNDAI"]

# =========================
# BASIC HELPERS
# =========================
def calculate_age(year: Optional[int]) -> int:
    """
    Returns how old the car is.
    If year is missing or invalid, age is 0.
    """
    if not isinstance(year, int):
        return 0
    return max(0, datetime.now().year - year)


def is_premium_brand(brand: Optional[str]) -> bool:
    """
    Checks if brand belongs to premium category.
    """
    if not brand:
        return False
    return brand.upper() in PREMIUM_BRANDS


def safe_float(value, default=0.0):
    """
    Converts value to float safely.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    """
    Converts value to int safely.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

# =========================
# LOAD CLEAN CAR DATA
# =========================
def load_car_data() -> List[dict]:
    """
    Loads cleaned car dataset from disk.
    """
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Car data file not found")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# MARKET VALUE ESTIMATION
# =========================
def estimate_market_value(car_data: dict) -> float:
    """
    Estimates realistic resale market value.

    This does NOT depend on listed price.
    It represents expected market resale value.
    """

    brand = car_data.get("brand", "")
    year = car_data.get("year_numeric")
    mileage = safe_float(car_data.get("mileage_numeric"), 0)

    # Base market value by brand category
    if is_premium_brand(brand):
        base_value = 12000
    elif brand and brand.upper() in MID_TIER_BRANDS:
        base_value = 9000
    elif brand and brand.upper() in BUDGET_BRANDS:
        base_value = 7000
    else:
        base_value = 8000

    # Depreciation by age
    age = calculate_age(year)
    base_value -= age * 600

    # Depreciation by mileage
    base_value -= (mileage / 10000) * 120

    # Prevent unrealistic low value
    return round(max(1500, base_value), 2)

# =========================
# TRANSACTION COST MODEL
# =========================
def calculate_transaction_cost(price: float) -> float:
    """
    Estimates transaction related cost.
    """
    if price <= 4000:
        return round(price * 0.15, 2)
    elif price <= 15000:
        return round(price * 0.10, 2)
    else:
        return round(price * 0.08, 2)

# =========================
# RISK SCORE
# =========================
def calculate_risk_score(car_data: dict) -> float:
    """
    Risk score from 0 (low risk) to 10 (high risk).
    """
    age = calculate_age(car_data.get("year_numeric"))
    mileage = safe_float(car_data.get("mileage_numeric"), 0)
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
    elif brand and brand.upper() in BUDGET_BRANDS:
        risk += 1

    return max(0, min(10, round(risk, 2)))

# =========================
# PROFIT CALCULATION (PRODUCTION SAFE)
# =========================
def calculate_profit_and_recommendation(car_data: dict) -> dict:
    """
    FINAL production-safe profit logic.

    Rules:
    - Profit can NEVER be negative
    - Exact profit value is always shown
    - Label explains profit category only
    """

    price = safe_float(car_data.get("price_numeric"), 0)

    market_value = estimate_market_value(car_data)
    transaction_cost = calculate_transaction_cost(price)
    risk_score = calculate_risk_score(car_data)

    raw_profit = market_value - (price + transaction_cost)

    # Enforce safety: no negative profit
    if raw_profit <= 0:
        profit = 0
        profit_label = "NO_PROFIT"
    else:
        profit = round(raw_profit, 2)

        if profit < 800:
            profit_label = "LOW"
        elif profit < 2000:
            profit_label = "MEDIUM"
        else:
            profit_label = "HIGH"

    # Recommendation logic
    if profit_label == "HIGH" and risk_score < 4:
        recommendation = "STRONG BUY"
    elif profit_label in ["MEDIUM", "HIGH"] and risk_score < 6:
        recommendation = "BUY"
    elif profit_label == "LOW":
        recommendation = "CONSIDER"
    else:
        recommendation = "DON'T BUY"

    return {
        "estimated_market_value": market_value,
        "transaction_cost": transaction_cost,
        "profit": profit,
        "profit_label": profit_label,
        "risk_score": risk_score,
        "recommendation": recommendation,
    }

# =========================
# ML PRICE PREDICTION
# =========================
def predict_car_price_ml(car_data: dict) -> float:
    """
    Predicts price using ML model.
    Supportive signal only.
    """
    if not os.path.exists(ML_MODEL_PATH):
        raise FileNotFoundError("ML model not found")

    model = joblib.load(ML_MODEL_PATH)

    current_year = datetime.now().year
    year = safe_int(car_data.get("year_numeric"), current_year)
    age = max(1, current_year - year)

    mileage = safe_float(car_data.get("mileage_numeric"), 0)
    mileage_per_year = mileage / age

    brand_encoded = hash(car_data.get("brand", "unknown")) % 100
    fuel_encoded = hash(car_data.get("fuel_type", "unknown")) % 10

    X = np.array([[brand_encoded, age, mileage, fuel_encoded, mileage_per_year]])

    predicted = model.predict(X)[0]
    return round(max(0, predicted), 2)

# =========================
# ANALYSIS HELPERS
# =========================
def analyze_car(car_data: dict) -> dict:
    """
    Full analysis for a single car.
    """
    analysis = calculate_profit_and_recommendation(car_data)

    return {
        **car_data,
        "age": calculate_age(car_data.get("year_numeric")),
        "is_premium": is_premium_brand(car_data.get("brand")),
        **analysis,
    }


def analyze_multiple_cars(cars: List[dict]) -> List[dict]:
    """
    Runs analysis on multiple cars.
    """
    return [analyze_car(car) for car in cars]


def compare_cars(cars: List[dict]) -> dict:
    """
    Compares cars by profit and risk.
    """
    analyzed = analyze_multiple_cars(cars)

    by_profit = sorted(analyzed, key=lambda x: safe_float(x.get("profit"), 0), reverse=True)
    by_risk = sorted(analyzed, key=lambda x: safe_float(x.get("risk_score"), 0))

    best_overall = max(
        analyzed,
        key=lambda x: safe_float(x.get("profit"), 0)
        - safe_float(x.get("risk_score"), 0) * 500,
        default=None,
    )

    return {
        "all_cars": analyzed,
        "best_by_profit": by_profit[0] if by_profit else None,
        "best_by_risk": by_risk[0] if by_risk else None,
        "best_overall_deal": best_overall,
    }

# =========================
# AI SUGGESTION (REQUIRED PLACEHOLDER)
# =========================
async def get_ai_suggestion(prompt: str, budget: Optional[float] = None) -> str:
    """
    Placeholder to keep API stable.
    """
    return "AI suggestion is disabled. Profit analysis is active."

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
