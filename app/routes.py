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
    normalize_scraped_car,              # Converts raw scraped data to clean format
    calculate_profit_and_recommendation, # Calculates profit, risk, recommendation
    rank_cars_by_investment_quality,     # Ranks cars by investment score
)

# =========================================================
# Schemas (API response shape)
# =========================================================
from app.models import (
    CarAnalysis,
)

router = APIRouter()

# =========================================================
# MAIN ANALYSIS ENDPOINT (PRODUCTION)
# =========================================================
@router.post(
    "/analyze-cars/",
    response_model=List[CarAnalysis],
    summary="Analyze cars from RAW scraped data",
    description="""
Analyze multiple cars using RAW scraped format.

This endpoint is designed for:
Scraper → Backend → AI → UI

Guaranteed rules:
- Negative profit is NEVER returned
- If a car is a loss:
  - profit = 0
  - profit_label = NO_PROFIT

Processing steps:
1. Take raw scraped car data
2. Clean & normalize the data
3. Calculate market value, profit, risk
4. Return production-safe result
""",
)
async def analyze_cars(
    cars: List[dict] = Body(
        ...,
        examples=[
            [
                {
                    "car_title": "Peugeot 208",
                    "price": "€ 2,990",
                    "details_url": "https://www.autoscout24.com/offers/peugeot-208",
                    "Vehicle_History": {
                        "Mileage": "169,000 km",
                        "First_registration": "05/2014"
                    },
                    "Energy_Consumption": {
                        "Fuel_type": "Gasoline"
                    },
                    "Technical_Data": {
                        "Gearbox": "Manual"
                    }
                }
            ]
        ],
    )
):
    try:
        results = []

        for raw_car in cars:
            # Step 1: Convert raw scraped data to clean numeric format
            clean_car = normalize_scraped_car(raw_car)

            # Step 2: Calculate profit, risk and recommendation
            analysis = calculate_profit_and_recommendation(clean_car)

            # Extra safety guard (should never trigger, but kept for production)
            if analysis["profit"] < 0:
                analysis["profit"] = 0
                analysis["profit_label"] = "NO_PROFIT"

            # Step 3: Merge clean input with analysis output
            results.append({
                **clean_car,
                **analysis
            })

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis error: {str(e)}"
        )


# =========================================================
# BACKWARD COMPATIBILITY ENDPOINT (DEPRECATED)
# =========================================================
@router.post(
    "/ai/analyze",
    response_model=List[CarAnalysis],
    summary="(Deprecated) Analyze cars",
    description="""
Deprecated endpoint.

This endpoint exists ONLY for old clients.
Internally it forwards the request to /analyze-cars/
and guarantees the same production-safe profit logic.
""",
)
async def ai_analyze_legacy(cars: List[dict]):
    # Strict proxy, no separate logic
    return await analyze_cars(cars)


# =========================================================
# TOP DEALS (INVESTMENT DISCOVERY ENDPOINT)
# =========================================================
@router.get(
    "/cars/top-deals",
    summary="Get top car investment opportunities",
    description="""
Returns the best car investment opportunities.

Modes:
- strict:
  Shows only strong, risk-adjusted positive deals

- relaxed:
  Shows strong deals + near-miss deals
  Near-miss cars are clearly labeled
""",
)
async def get_top_deals(
    mode: str = Query("strict", enum=["strict", "relaxed"]),
    limit: int = Query(10, ge=1, le=50),
    min_profit: float = Query(1, ge=0),
    max_risk: float = Query(6, ge=0, le=10),
):
    try:
        # Source of truth: scraper output
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

        # Rank cars by investment score
        ranked = rank_cars_by_investment_quality(analyzed)

        # Strong opportunities
        strong = [
            car for car in ranked
            if car["investment_score"] > 0
        ][:limit]

        # Relaxed mode: near-miss deals
        near_miss = []
        if mode == "relaxed":
            near_miss = [
                {
                    **car,
                    "note": "Positive profit but weak risk-adjusted score"
                }
                for car in ranked
                if car["investment_score"] <= 0
                and car["profit"] >= min_profit
                and car["risk_score"] <= max_risk
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
        raise HTTPException(
            status_code=500,
            detail=f"Top deals error: {str(e)}"
        )
