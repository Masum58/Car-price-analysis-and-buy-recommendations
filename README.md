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

---

## How to Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

API will be available at:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

