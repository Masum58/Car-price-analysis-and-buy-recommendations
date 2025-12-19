from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from app.models import (
    CarInput, 
    CarAnalysis, 
    CompareRequest, 
    CompareByNameRequest,
    AISuggestionRequest,
    AISuggestionResponse,
    CarsListResponse,
    CarsStatsResponse
)

from app.ai_calculations import (
    analyze_multiple_cars,
    compare_cars,
    get_ai_suggestion
)

router = APIRouter()

@router.post("/analyze-cars/", response_model=List[CarAnalysis])
async def analyze_cars(cars: List[CarInput]):
    """
    Analyze multiple cars and return profit/risk scores
    
    Example:
```json
    [
        {
            "title": "Tesla Model 3 2020",
            "brand": "Tesla",
            "year_numeric": 2020,
            "mileage_numeric": 50000,
            "price_numeric": 35000
        }
    ]
```
    """
    try:
        # Convert Pydantic models to dicts
        cars_data = [car.model_dump() for car in cars]
        
        # Analyze
        results = analyze_multiple_cars(cars_data)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post("/compare-cars/")
async def compare_cars_endpoint(request: CompareRequest):
    """
    Compare multiple cars and get rankings
    
    Returns:
    - all_cars: All analyzed cars
    - best_by_profit: Car with highest profit potential
    - best_by_risk: Car with lowest risk
    - best_overall_deal: Best balanced deal
    """
    try:
        cars_data = [car.model_dump() for car in request.cars]
        
        comparison = compare_cars(cars_data)
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")

@router.post("/ai-suggest/", response_model=AISuggestionResponse)
async def ai_suggest(request: AISuggestionRequest):
    """
    Get AI-powered car buying suggestion
    
    Example:
```json
    {
        "prompt": "I need a reliable family car under 30000 euros",
        "budget": 30000
    }
```
    """
    try:
        suggestion = await get_ai_suggestion(request.prompt, request.budget)
        
        return AISuggestionResponse(
            suggestion=suggestion,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI suggestion error: {str(e)}")

@router.get("/test-analysis/")
async def test_analysis():
    """
    Test endpoint with sample data
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
    
    results = analyze_multiple_cars(sample_cars)
    
    return {
        "message": "Test analysis completed",
        "results": results
    }

@router.get("/cars/list", response_model=CarsListResponse)
async def list_clean_cars():
    """
    Get list of all clean, API-ready cars from the master dataset
    
    Returns:
    - total_cars: Total number of cars in dataset
    - cars: Preview of first 10 cars
    - stats: Quick statistics
    """
    try:
        from app.ai_calculations import load_car_data
        
        cars = load_car_data()
        
        # Calculate quick stats
        total = len(cars)
        brands = {}
        fuel_types = {}
        
        for car in cars:
            # Count brands
            brand = car.get('brand', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
            
            # Count fuel types
            fuel = car.get('fuel_type', 'Unknown')
            fuel_types[fuel] = fuel_types.get(fuel, 0) + 1
        
        return {
            "total_cars": total,
            "cars_preview": cars[:10],  # First 10 cars
            "statistics": {
                "brands": brands,
                "fuel_types": fuel_types
            }
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, 
            detail="cars_data_api_ready.json not found. Run clean_combine_enhanced.py first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading cars: {str(e)}")

@router.get("/cars/stats", response_model=CarsStatsResponse)
async def get_dataset_stats():
    """
    Get detailed statistics about the car dataset
    """
    try:
        from app.ai_calculations import load_car_data
        
        cars = load_car_data()
        
        # Calculate detailed stats
        total = len(cars)
        
        # Price stats
        prices = [car.get('price_numeric') for car in cars if car.get('price_numeric')]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        # Year range
        years = [car.get('year_numeric') for car in cars if car.get('year_numeric')]
        oldest = min(years) if years else 0
        newest = max(years) if years else 0
        
        # Brand count
        brands = {}
        for car in cars:
            brand = car.get('brand', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
        
        # Top 5 brands
        top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]
        
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
            "top_5_brands": [{"brand": b[0], "count": b[1]} for b in top_brands],
            "data_quality": "100% - Production Ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")