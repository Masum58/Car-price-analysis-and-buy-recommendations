# =========================================================
# FastAPI router & error handling
# =========================================================
from fastapi import APIRouter, HTTPException, Body, Query
from typing import List
import json
import os

# =========================================================
# Core business logic
# =========================================================
from app.ai_calculations import (
    normalize_scraped_car,
    calculate_profit_and_recommendation,
    rank_cars_by_investment_quality,
)

# =========================================================
# Advanced AI Recommendation Layer
# =========================================================
from app.car_recommendation_engine import (
    CarRecommendationEngine,
    get_user_context_from_request,
)

# =========================================================
# Schemas
# =========================================================
from app.models import (
    CarInput,
    CarAnalysis,
)

from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Initialize recommendation engine
recommendation_engine = CarRecommendationEngine()


# =========================================================
# MAIN ANALYSIS ENDPOINT (RAW SCRAPER INPUT)
# =========================================================
@router.post(
    "/analyze-cars/",
    response_model=List[CarAnalysis],
    summary="Analyze cars from RAW scraped data",
)
async def analyze_cars(
    cars: List[dict] = Body(
        ...,
        example=[
            {
                "car_title": "Peugeot 208",
                "price": "€ 2,990",
                "details_url": "https://www.autoscout24.com/offers/peugeot-208",
                "Vehicle_History": {
                    "Mileage": "169,000 km",
                    "First_registration": "05/2014"
                },
                "Energy_Consumption": {"Fuel_type": "Gasoline"},
                "Technical_Data": {"Gearbox": "Manual"}
            }
        ],
    )
):
    try:
        results = []

        for raw_car in cars:
            clean_car = normalize_scraped_car(raw_car)
            analysis = calculate_profit_and_recommendation(clean_car)

            # Production safety guard
            if analysis["profit"] < 0:
                analysis["profit"] = 0
                analysis["profit_label"] = "NO_PROFIT"

            results.append({**clean_car, **analysis})

        return results

    except Exception as e:
        raise HTTPException(500, f"Analysis error: {str(e)}")


# =========================================================
# BACKWARD COMPATIBILITY ENDPOINT
# =========================================================
@router.post(
    "/ai/analyze",
    response_model=List[CarAnalysis],
    summary="Deprecated - Analyze cars",
)
async def ai_analyze_legacy(cars: List[dict]):
    return await analyze_cars(cars)


# =========================================================
# TOP DEALS (INVESTMENT DISCOVERY)
# =========================================================
@router.get(
    "/cars/top-deals",
    summary="Get top car investment opportunities",
)
async def get_top_deals(
    mode: str = Query("strict", enum=["strict", "relaxed"]),
    limit: int = Query(10, ge=1, le=50),
    min_profit: float = Query(1, ge=0),
    max_risk: float = Query(6, ge=0, le=10),
):
    try:
        path = os.path.join("scrapers", "output.json")
        if not os.path.exists(path):
            raise HTTPException(404, "scrapers/output.json not found")

        with open(path, "r", encoding="utf-8") as f:
            raw_cars = json.load(f)

        analyzed = []

        for raw in raw_cars:
            clean = normalize_scraped_car(raw)
            analysis = calculate_profit_and_recommendation(clean)
            analyzed.append({**clean, **analysis})

        ranked = rank_cars_by_investment_quality(analyzed)

        strong = [
            car for car in ranked
            if car["investment_score"] > 0
        ][:limit]

        near_miss = []
        if mode == "relaxed":
            near_miss = [
                {
                    **c,
                    "note": "Positive profit but weak risk-adjusted score"
                }
                for c in ranked
                if c["investment_score"] <= 0
                and c["profit"] >= min_profit
                and c["risk_score"] <= max_risk
            ][:limit]

        return {
            "mode": mode,
            "summary": {
                "strong_opportunities": len(strong),
                "near_miss_opportunities": len(near_miss),
            },
            "strong_opportunities": strong,
            "near_miss_opportunities": near_miss,
        }

    except Exception as e:
        raise HTTPException(500, f"Top deals error: {str(e)}")


# =========================================================
# USER CONTEXT REQUEST MODEL
# =========================================================
class UserContext(BaseModel):
    max_budget: Optional[float] = None
    min_seats: Optional[int] = None
    preferred_gearbox: Optional[str] = None
    preferred_fuel_type: Optional[str] = None


class UserContextCompareRequest(BaseModel):
    user_context: UserContext
    cars: List[CarInput]


# =========================================================
# USER CONTEXT BASED COMPARISON
# =========================================================
@router.post(
    "/cars/compare-user-context",
    summary="Compare cars based on user preferences",
)
async def compare_cars_user_context(payload: UserContextCompareRequest):
    try:
        analyzed = []
        ctx = payload.user_context

        for car in payload.cars:
            car_dict = car.model_dump()

            score = 0
            reasons = []

            if ctx.max_budget is not None:
                if car_dict.get("price_numeric", 0) <= ctx.max_budget:
                    score += 2
                    reasons.append("Within budget")
                else:
                    reasons.append("Over budget")

            if ctx.preferred_gearbox:
                if car_dict.get("transmission") == ctx.preferred_gearbox:
                    score += 1
                    reasons.append("Matches gearbox preference")

            if ctx.preferred_fuel_type:
                if car_dict.get("fuel_type") == ctx.preferred_fuel_type:
                    score += 1
                    reasons.append("Matches fuel preference")

            analyzed.append({
                **car_dict,
                "user_fit_score": score,
                "match_reasons": reasons
            })

        best_match = max(analyzed, key=lambda x: x["user_fit_score"])

        return {
            "all_cars": analyzed,
            "best_match": best_match,
            "comparison_reason":
                "Best match selected based on highest user_fit_score"
        }

    except Exception as e:
        raise HTTPException(500, f"User comparison error: {str(e)}")


# =========================================================
# INVESTMENT BASED COMPARISON
# =========================================================
class InvestmentCompareRequest(BaseModel):
    cars: List[CarInput]


@router.post(
    "/cars/compare-investment",
    summary="Compare cars using investment logic",
)
async def compare_cars_investment(payload: InvestmentCompareRequest):
    try:
        analyzed = []

        for car in payload.cars:
            car_dict = car.model_dump()

            analysis = calculate_profit_and_recommendation(car_dict)

            if analysis["profit"] < 0:
                analysis["profit"] = 0
                analysis["profit_label"] = "NO_PROFIT"

            full_car = {**car_dict, **analysis}

            investment_score = (
                full_car["profit"] - (full_car["risk_score"] * 500)
            )

            full_car["investment_score"] = round(investment_score, 2)

            analyzed.append(full_car)

        best_by_profit = max(analyzed, key=lambda x: x["profit"])
        best_by_risk = min(analyzed, key=lambda x: x["risk_score"])
        best_overall = max(analyzed, key=lambda x: x["investment_score"])

        return {
            "all_cars": analyzed,
            "best_by_profit": best_by_profit,
            "best_by_risk": best_by_risk,
            "best_overall_deal": best_overall
        }

    except Exception as e:
        raise HTTPException(500, f"Comparison error: {str(e)}")
