# Car Price Analysis & Buy Recommendations API

This project is a production-ready backend API built with FastAPI to analyze used car listings and provide intelligent buy recommendations.  
It takes RAW scraped car data as input, cleans and normalizes it, estimates fair market value, calculates profit and risk, and returns a safe, decision-ready response that can be directly consumed by web apps, mobile apps, or dashboards.

The system is designed with strict business rules to ensure reliability in real-world usage: negative profit is never returned, loss-making cars are clearly labeled, and deprecated endpoints are safely forwarded to the latest production endpoint.  
This makes the API suitable for scraper → backend → AI → UI pipelines as well as long-term production deployments.

---

## Core API Endpoints

### Health Check
**GET `/health`**  
Checks whether the service is running.

---

### Analyze Cars (MAIN PRODUCTION ENDPOINT)
**POST `/analyze-cars/`**

Analyzes multiple cars from RAW scraped data and returns:
- Normalized numeric fields (price, mileage, year)
- Estimated market value
- Guaranteed non-negative profit
- Risk score
- Clear buy recommendation

**Key Guarantees**
- Negative profit is never returned
- Loss cars return `profit = 0` and recommendation = `DON'T BUY`
- Safe for direct UI and backend usage

This is the primary endpoint used in production.

---

### Deprecated Endpoint (Backward Compatibility)
**POST `/ai/analyze`**

This endpoint exists only for older clients.  
Internally, it forwards requests to `/analyze-cars/` and guarantees identical results.

---

### Top Car Investment Opportunities
**GET `/cars/top-deals`**

Returns the best car investment opportunities based on profit and risk filters.

Query modes:
- `strict` → Only strong, risk-adjusted deals
- `relaxed` → Includes near-miss deals (clearly labeled)

Useful for dashboards and recommendation feeds.

1️⃣ /cars/compare-user-context

This endpoint compares multiple cars based on user preferences instead of pure financial logic.

It evaluates how well each car matches user requirements such as:

- Maximum budget

- Minimum number of seats

- Preferred gearbox type

- Preferred fuel type

Each car receives a user_fit_score based on matching criteria.
The response includes:

all_cars (each with user_fit_score and match reasons)

- best_match

- comparison_reason

How it works:

- User context is received.

- Each car is evaluated against user preferences.

- Matching rules increase score.

- Car with highest score is selected as best match.

Example request:

{
  "user_context": {
    "max_budget": 20000,
    "min_seats": 5,
    "preferred_gearbox": "Automatic",
    "preferred_fuel_type": "Diesel"
  },
  "cars": [
    {
      "title": "Peugeot 208",
      "brand": "Peugeot",
      "year_numeric": 2014,
      "mileage_numeric": 169000,
      "price_numeric": 2990,
      "fuel_type": "Gasoline",
      "transmission": "Manual",
      "seats": 5
    },
    {
      "title": "BMW 320d 2018",
      "brand": "BMW",
      "year_numeric": 2018,
      "mileage_numeric": 80000,
      "price_numeric": 18000,
      "fuel_type": "Diesel",
      "transmission": "Automatic",
      "seats": 5
    }
  ]
}

This endpoint is useful for personalized recommendations.

2️⃣ /cars/compare-investment

This endpoint compares cars using investment logic.

It analyzes each car using:

- Estimated market value

- Transaction cost

- Profit (never negative in production)

- Risk score

- Investment score

Investment score formula:

investment_score = profit - (risk_score * 500)

The response includes:

- all_cars

- best_by_profit

- best_by_risk

- best_overall_deal

How it works:

- Clean car input is received.

- Financial analysis is performed.

- Profit is forced to zero if negative.

- Investment score is calculated.

- Best selections are returned.

Example request:

{
  "cars": [
    {
      "title": "Peugeot 208",
      "brand": "Peugeot",
      "year_numeric": 2014,
      "mileage_numeric": 169000,
      "price_numeric": 2990
    },
    {
      "title": "BMW 320d 2018",
      "brand": "BMW",
      "year_numeric": 2018,
      "mileage_numeric": 80000,
      "price_numeric": 25000
    }
  ]
}

This endpoint is designed for financial decision making and dealer-side investment analysis.


Profit Calculation Logic:

The system calculates profit using a structured financial estimation pipeline.
Step 1: Market Value Estimation:

Each car’s fair market value is estimated using:


Vehicle age


Mileage


Brand category (premium vs non-premium)


Fuel type


Depreciation logic


This produces:
estimated_market_value


Step 2: Transaction Cost Calculation:

Transaction cost is calculated as a percentage of the listed price:
transaction_cost = price_numeric × transaction_rate

This represents:


Dealer margin


Registration cost


Operational cost


Risk buffer



Step 3: Raw Profit Formula:

Raw profit is calculated as:
raw_profit = estimated_market_value - price_numeric - transaction_cost


Step 4: Production Safety Rule:

In production mode, negative profit is never returned.
If raw_profit is negative:
profit = 0
profit_label = "NO_PROFIT"

This ensures:


No misleading negative values


Cleaner UI output


Safe financial interpretation



Profit Labels
Profit is categorized into investment tiers:
Profit ValueLabel0NO_PROFITSmall marginLOWModerateMEDIUMHigh marginHIGH

Investment Score Formula
For investment comparison endpoints:
investment_score = profit - (risk_score × 500)

This means:


Higher profit increases score


Higher risk reduces score


A car with high profit but high risk may not rank first



Risk Score (0–10)
Risk score is derived from:


Age


Mileage


Brand reliability


Market volatility


Lower risk = better investment stability.


---

## How to Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

API will be available at:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

