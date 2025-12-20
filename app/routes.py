# FastAPI router & error handling
from fastapi import APIRouter, HTTPException

# Basic Python utilities
from typing import List
from datetime import datetime

# Import request/response schemas (Pydantic models)
from app.models import (
    CarInput,              # Input car data
    CarAnalysis,           # Output analysis schema
    CompareRequest,        # Compare cars request
    CompareByNameRequest,  # (reserved / future use)
    AISuggestionRequest,   # AI suggestion input
    AISuggestionResponse,  # AI suggestion output
    CarsListResponse,      # Cars list response
    CarsStatsResponse      # Dataset stats response
)

# Import business logic functions
from app.ai_calculations import (
    analyze_multiple_cars,  # Analyze profit/risk
    compare_cars,           # Compare multiple cars
    get_ai_suggestion,      # OpenAI-based suggestion
    load_car_data           # Load cleaned car dataset
)

# Create API router
router = APIRouter()

# =========================================================
# ANALYZE CARS
# =========================================================
@router.post("/analyze-cars/", response_model=List[CarAnalysis])
async def analyze_cars(cars: List[CarInput]):
    """
    Analyze multiple cars.
    Returns profit, risk score, recommendation, etc.
    """
    try:
        # Convert Pydantic models to normal dictionaries
        cars_data = [car.model_dump() for car in cars]

        # Run analysis logic
        return analyze_multiple_cars(cars_data)

    except Exception as e:
        # Any unexpected error → HTTP 500
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


# =========================================================
# COMPARE CARS
# =========================================================
@router.post("/compare-cars/")
async def compare_cars_endpoint(request: CompareRequest):
    """
    Compare cars and find:
    - Best by profit
    - Best by risk
    - Best overall deal
    """
    try:
        # Convert input cars to dict
        cars_data = [car.model_dump() for car in request.cars]

        # Compare cars
        return compare_cars(cars_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")


# =========================================================
# AI SUGGESTION
# =========================================================
@router.post("/ai-suggest/", response_model=AISuggestionResponse)
async def ai_suggest(request: AISuggestionRequest):
    """
    Ask AI for car buying advice based on user prompt & budget
    """
    try:
        suggestion = await get_ai_suggestion(
            request.prompt,
            request.budget
        )

        return AISuggestionResponse(
            suggestion=suggestion,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI suggestion error: {str(e)}")


# =========================================================
# TEST ANALYSIS (DEV ONLY)
# =========================================================
@router.get("/test-analysis/")
async def test_analysis():
    """
    Developer test endpoint with hardcoded sample cars
    (No request body needed)
    """
    sample_cars = [
        {
            "title": "Tesla Model 3 2020",
            "brand": "Tesla",
            "year_numeric": 2020,
            "mileage_numeric": 50000,
            "price_numeric": 35000,
            "fuel_type": "electric"
        },
        {
            "title": "BMW 320d 2018",
            "brand": "BMW",
            "year_numeric": 2018,
            "mileage_numeric": 80000,
            "price_numeric": 25000,
            "fuel_type": "diesel"
        }
    ]

    # Analyze sample cars
    results = analyze_multiple_cars(sample_cars)

    return {
        "message": "Test analysis completed",
        "results": results
    }


# =========================================================
# LIST CLEAN CARS
# =========================================================
@router.get("/cars/list", response_model=CarsListResponse)
async def list_clean_cars():
    """
    Returns:
    - Total number of cars
    - First 10 cars as preview
    - Brand & fuel statistics
    """
    try:
        cars = load_car_data()
        total = len(cars)

        brands = {}
        fuel_types = {}

        # Count brands and fuel types
        for car in cars:
            brand = car.get("brand") or "Unknown"
            fuel = car.get("fuel_type") or "Unknown"

            brands[brand] = brands.get(brand, 0) + 1
            fuel_types[fuel] = fuel_types.get(fuel, 0) + 1

        return {
            "total_cars": total,
            "cars_preview": cars[:10],
            "statistics": {
                "brands": brands,
                "fuel_types": fuel_types
            }
        }

    except FileNotFoundError:
        # Dataset missing
        raise HTTPException(
            status_code=404,
            detail="cars_data.json not found in data/raw/"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading cars: {str(e)}")


# =========================================================
# DATASET STATS (SAFE VERSION)
# =========================================================
@router.get("/cars/stats", response_model=CarsStatsResponse)
async def get_dataset_stats():
    """
    Returns dataset statistics:
    - Price range
    - Year range
    - Top 5 brands
    """
    try:
        cars = load_car_data()
        total = len(cars)

        # -----------------------------
        # SAFE PRICE CALCULATION
        # -----------------------------
        prices = [
            car.get("price_numeric")
            for car in cars
            if isinstance(car.get("price_numeric"), (int, float))
        ]

        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        avg_price = sum(prices) / len(prices) if prices else 0

        # -----------------------------
        # SAFE YEAR CALCULATION
        # -----------------------------
        years = [
            car.get("year_numeric")
            for car in cars
            if isinstance(car.get("year_numeric"), int)
        ]

        oldest = min(years) if years else 0
        newest = max(years) if years else 0

        # -----------------------------
        # BRAND COUNT
        # -----------------------------
        brands = {}
        for car in cars:
            brand = car.get("brand") or "Unknown"
            brands[brand] = brands.get(brand, 0) + 1

        top_brands = sorted(
            brands.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_cars": total,
            "price_range": {
                "min": round(min_price, 2),
                "max": round(max_price, 2),
                "average": round(avg_price, 2)
            },
            "year_range": {
                "oldest": int(oldest),
                "newest": int(newest)
            },
            "top_5_brands": [
                {"brand": b, "count": c} for b, c in top_brands
            ],
            "data_quality": "Cleaned & API-ready"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating stats: {str(e)}"
        )
