from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CarInput(BaseModel):
    """Car input data from scraper or user"""
    title: str = Field(..., description="Car title/name")
    brand: Optional[str] = Field(None, description="Car brand")
    year_numeric: Optional[int] = Field(None, description="Manufacturing year", ge=1900, le=2030)
    mileage_numeric: Optional[float] = Field(None, description="Mileage in km", ge=0)
    price_numeric: Optional[float] = Field(None, description="Listed price", ge=0)
    fuel_type: Optional[str] = Field(None, description="Fuel type (petrol/diesel/electric)")
    transmission: Optional[str] = Field(None, description="Transmission type")
    url: Optional[str] = Field(None, description="Source URL")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Tesla Model 3 2020",
                "brand": "Tesla",
                "year_numeric": 2020,
                "mileage_numeric": 50000,
                "price_numeric": 35000,
                "fuel_type": "electric",
                "transmission": "automatic"
            }
        }

class CarAnalysis(BaseModel):
    """Car analysis result with profit/risk scores"""
    title: str
    brand: Optional[str]
    year_numeric: Optional[int]
    mileage_numeric: Optional[float]
    price_numeric: Optional[float]
    estimated_market_value: Optional[float] = Field(None, description="Estimated fair market value")
    profit: Optional[float] = Field(None, description="Potential profit")
    risk_score: Optional[float] = Field(None, description="Risk score (0-10)")
    recommendation: Optional[str] = Field(None, description="Buy recommendation")
    age: Optional[int] = Field(None, description="Car age in years")
    is_premium: Optional[bool] = Field(None, description="Is premium brand")

class CompareRequest(BaseModel):
    """Request to compare cars"""
    cars: List[CarInput] = Field(..., description="List of cars to compare")

class CompareByNameRequest(BaseModel):
    """Request to compare cars by name"""
    car_names: List[str] = Field(..., description="List of car names/titles")

class AISuggestionRequest(BaseModel):
    """Request for AI-powered car suggestion"""
    prompt: str = Field(..., description="User requirements (budget, type, needs)")
    budget: Optional[float] = Field(None, description="Maximum budget")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "I need a reliable family car under 30000 euros",
                "budget": 30000
            }
        }

class AISuggestionResponse(BaseModel):
    """AI suggestion response"""
    suggestion: str = Field(..., description="AI-generated suggestion")
    timestamp: datetime = Field(default_factory=datetime.now)
from typing import Dict, Any

class CarsListResponse(BaseModel):
    total_cars: int
    cars_preview: List[Dict[str, Any]]
    statistics: Dict[str, Dict[str, int]]


class BrandCount(BaseModel):
    brand: str
    count: int


class CarsStatsResponse(BaseModel):
    total_cars: int
    price_range: Dict[str, float]
    year_range: Dict[str, int]
    top_5_brands: List[BrandCount]
    data_quality: str
