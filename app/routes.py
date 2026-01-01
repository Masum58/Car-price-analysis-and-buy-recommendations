# FastAPI router & error handling
from fastapi import APIRouter, HTTPException

# Basic Python utilities
from typing import List
from datetime import datetime

# ========== NEW: AI Recommendation Engine ==========
from app.car_recommendation_engine import (
    CarRecommendationEngine,
    get_user_context_from_request,
    format_comparison_for_ui
)

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

# ========== NEW: Initialize AI Recommendation Engine ==========
recommendation_engine = CarRecommendationEngine()


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


# =========================================================
# ========== NEW ENDPOINTS: AI RECOMMENDATION ==========
# =========================================================


# =========================================================
# COMPARE TWO CARS WITH AI
# =========================================================
@router.post("/compare-two-cars/")
async def compare_two_cars_with_ai(request: dict):
    """
    Compare two cars with AI recommendation engine
    
    This endpoint uses user context to intelligently compare cars
    and highlight the better option with detailed reasoning.
    
    Request body:
    {
        "car_a": {
            "car_title": "BMW 320d Touring",
            "price": "€28,500",
            "Basic_Data": {"Seats": "5"},
            "Technical_Data": {"Gearbox": "Automatic"},
            "Vehicle_History": {"First_registration": "03/2019", "Mileage": "65,000 km"},
            "Energy_Consumption": {"Fuel_type": "Diesel"}
        },
        "car_b": {
            "car_title": "Audi A4 Avant",
            "price": "€32,900",
            "Basic_Data": {"Seats": "5"},
            "Technical_Data": {"Gearbox": "Automatic"},
            "Vehicle_History": {"First_registration": "05/2020", "Mileage": "45,000 km"},
            "Energy_Consumption": {"Fuel_type": "Diesel"}
        },
        "user_context": {
            "max_budget": 30000,
            "min_seats": 5,
            "preferred_gearbox": "automatic",
            "preferred_fuel": "diesel",
            "wanted_features": ["navigation", "parking sensors"],
            "usage_type": "family",
            "priority": "balanced"
        }
    }
    
    Response:
    {
        "recommended_car": "car_a",  // or "car_b" or "tie"
        "confidence": "high",  // low, medium, high
        "car_a": {
            "highlight": true,  // Use this to highlight in UI!
            "score": 87.5,
            "insights": [
                "✅ Well within your budget",
                "💰 Excellent deal - below market price",
                "🔧 Highly reliable brand and age"
            ],
            "warnings": []
        },
        "car_b": {
            "highlight": false,
            "score": 72.3,
            "insights": [
                "⭐ Great feature match for your needs"
            ],
            "warnings": [
                "⚠️ Above your preferred budget"
            ]
        },
        "reasoning": "Car A is the better choice with a score of 87.5/100 vs 72.3/100. It excels in: Price, Value. ✅ Well within your budget",
        "detailed_scores": {
            "price": {
                "car_a_score": 0.92,
                "car_b_score": 0.65,
                "winner": "car_a",
                "difference": 0.27
            },
            "value": {...},
            "reliability": {...},
            "features": {...},
            "fuel_efficiency": {...},
            "safety": {...}
        }
    }
    """
    try:
        # Extract data from request
        car_a = request.get("car_a")
        car_b = request.get("car_b")
        user_ctx = get_user_context_from_request(
            request.get("user_context", {})
        )
        
        # Validate input
        if not car_a or not car_b:
            raise HTTPException(
                status_code=400,
                detail="Both car_a and car_b are required"
            )
        
        # Compare with AI engine
        comparison = recommendation_engine.compare_two_cars(
            car_a, car_b, user_ctx
        )
        
        # Format for UI
        result = format_comparison_for_ui(comparison)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI comparison error: {str(e)}"
        )


# =========================================================
# ANALYZE SINGLE CAR WITH AI
# =========================================================
@router.post("/analyze-single-car/")
async def analyze_single_car_with_ai(request: dict):
    """
    Analyze single car with user context
    
    Provides intelligent analysis based on user preferences,
    budget, and needs.
    
    Request body:
    {
        "car": {
            "car_title": "BMW 320d Touring",
            "price": "€28,500",
            "Basic_Data": {"Seats": "5"},
            "Technical_Data": {"Gearbox": "Automatic"},
            "Vehicle_History": {"First_registration": "03/2019", "Mileage": "65,000 km"},
            "Energy_Consumption": {"Fuel_type": "Diesel"}
        },
        "user_context": {
            "max_budget": 30000,
            "min_seats": 5,
            "preferred_gearbox": "automatic",
            "preferred_fuel": "diesel"
        }
    }
    
    Response:
    {
        "score": 87.5,
        "user_fit": 87.5,
        "insights": [
            "✅ Well within your budget",
            "💰 Excellent deal - below market price",
            "🔧 Highly reliable brand and age",
            "⭐ Great feature match for your needs",
            "⛽ Good fuel economy for your usage"
        ],
        "warnings": [],
        "scores_breakdown": {
            "price": 0.92,
            "value": 0.85,
            "reliability": 0.88,
            "features": 0.82,
            "fuel_efficiency": 0.78,
            "safety": 0.75
        }
    }
    """
    try:
        # Extract data
        car = request.get("car")
        user_ctx = get_user_context_from_request(
            request.get("user_context", {})
        )
        
        # Validate input
        if not car:
            raise HTTPException(
                status_code=400,
                detail="car data is required"
            )
        
        # Analyze with AI engine
        analysis = recommendation_engine.analyze_car_for_user(
            car, user_ctx
        )
        
        return {
            "score": round(analysis["user_fit"], 1),
            "user_fit": round(analysis["user_fit"], 1),
            "insights": analysis["insights"],
            "warnings": analysis["warnings"],
            "scores_breakdown": {
                k: round(v, 2) for k, v in analysis["scores"].items()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis error: {str(e)}"
        )


# =========================================================
# HEALTH CHECK FOR NEW ENDPOINTS
# =========================================================
@router.get("/ai-engine/health")
async def ai_engine_health():
    """
    Check if AI recommendation engine is working
    """
    try:
        # Test with dummy data
        test_car = {
            "car_title": "Test Car",
            "price": "€20,000",
            "Basic_Data": {"Seats": "5"},
            "Technical_Data": {"Gearbox": "Manual"},
            "Energy_Consumption": {"Fuel_type": "Diesel"}
        }
        
        test_context = {
            "max_budget": 25000,
            "min_seats": 5
        }
        
        # Try analysis
        analysis = recommendation_engine.analyze_car_for_user(
            test_car, test_context
        )
        
        return {
            "status": "healthy",
            "engine": "CarRecommendationEngine",
            "version": "1.0",
            "test_score": round(analysis["user_fit"], 1),
            "message": "AI engine is working correctly"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }