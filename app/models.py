from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# =========================================================
# CLEAN CAR INPUT MODEL
# =========================================================
# =========================================================
# CLEAN CAR INPUT MODEL
# =========================================================
class CarInput(BaseModel):
    """
    Car input data in clean numeric format.
    Used when frontend sends already cleaned data.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "title": "Tesla Model 3 2020",
                "brand": "Tesla",
                "year_numeric": 2020,
                "mileage_numeric": 50000,
                "price_numeric": 35000,
                "fuel_type": "Electric",
                "transmission": "Automatic",
                "seats": 5
            }
        }
    )

    title: str = Field(..., description="Car title or model name")

    brand: Optional[str] = Field(
        None,
        description="Car manufacturer brand"
    )

    year_numeric: Optional[int] = Field(
        None,
        ge=1900,
        le=2035,
        description="Manufacturing year"
    )

    mileage_numeric: Optional[float] = Field(
        None,
        ge=0,
        description="Mileage in kilometers"
    )

    price_numeric: Optional[float] = Field(
        None,
        ge=0,
        description="Listed price in Euro"
    )

    fuel_type: Optional[str] = Field(
        None,
        description="Fuel type (Gasoline, Diesel, Electric, Hybrid)"
    )

    transmission: Optional[str] = Field(
        None,
        description="Transmission type (Manual, Automatic)"
    )

    seats: Optional[int] = Field(
        None,
        ge=1,
        le=9,
        description="Number of seats"
    )

    url: Optional[str] = Field(
        None,
        description="Source listing URL"
    )



# =========================================================
# ANALYSIS RESULT MODEL
# =========================================================
class CarAnalysis(BaseModel):
    """
    Final production-safe car analysis output.
    Matches actual response structure from analysis pipeline.
    """

    title: str
    brand: Optional[str] = None
    year_numeric: Optional[int] = None
    mileage_numeric: Optional[float] = None
    price_numeric: Optional[float] = None

    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    url: Optional[str] = None

    estimated_market_value: Optional[float] = None
    transaction_cost: Optional[float] = None
    profit: Optional[float] = None
    profit_label: Optional[str] = None
    risk_score: Optional[float] = None
    recommendation: Optional[str] = None

    age: Optional[int] = None
    is_premium: Optional[bool] = None
    investment_score: Optional[float] = None

    model_config = ConfigDict(extra="forbid")



# =========================================================
# COMPARE MULTIPLE CARS REQUEST
# =========================================================
class CompareRequest(BaseModel):
    """
    Request to compare multiple cars.
    """

    model_config = ConfigDict(extra="forbid")

    cars: List[CarInput]


# =========================================================
# COMPARE BY NAME REQUEST
# =========================================================
class CompareByNameRequest(BaseModel):
    """
    Compare cars using only titles.
    """

    model_config = ConfigDict(extra="forbid")

    car_names: List[str]


# =========================================================
# AI SUGGESTION REQUEST
# =========================================================
class AISuggestionRequest(BaseModel):
    """
    User request for AI-powered suggestion.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "prompt": "I need a reliable family car under 30000 euros",
                "budget": 30000
            }
        }
    )

    prompt: str = Field(
        ...,
        description="User requirements such as budget and needs"
    )

    budget: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum budget in Euro"
    )


# =========================================================
# AI SUGGESTION RESPONSE
# =========================================================
class AISuggestionResponse(BaseModel):
    """
    AI-generated suggestion output.
    """

    suggestion: str
    timestamp: datetime = Field(default_factory=datetime.now)


# =========================================================
# LIST RESPONSE MODEL
# =========================================================
class CarsListResponse(BaseModel):
    """
    Response for listing cleaned dataset.
    """

    model_config = ConfigDict(extra="forbid")

    total_cars: int
    cars_preview: List[Dict[str, Any]]
    statistics: Dict[str, Dict[str, int]]


# =========================================================
# BRAND COUNT MODEL
# =========================================================
class BrandCount(BaseModel):

    model_config = ConfigDict(extra="forbid")

    brand: str
    count: int


# =========================================================
# DATASET STATISTICS RESPONSE
# =========================================================
class CarsStatsResponse(BaseModel):
    """
    Dataset statistical overview.
    """

    model_config = ConfigDict(extra="forbid")

    total_cars: int
    price_range: Dict[str, float]
    year_range: Dict[str, int]
    top_5_brands: List[BrandCount]
    data_quality: str
