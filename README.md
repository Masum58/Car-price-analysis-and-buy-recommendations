# Car Price Analysis & Buy Recommendations (Backend)

This project is a backend system designed to analyze used car listings, estimate fair market value, calculate profit & risk, and provide intelligent buy recommendations.

The system is built for backend/API usage so that mobile apps, web apps, or dashboards can consume the analysis results easily.

---

## 🚀 Tech Stack

- Python
- FastAPI
- Uvicorn
- Web scraping (Autoscout24)
- Rule-based + AI-assisted price analysis

---

## 📁 Project Structure (Important)


---

## 🧠 Core Logic Explanation (For Backend Engineers)

### 1️⃣ Scraping Layer (`scrapers/`)
This layer is responsible for collecting used car listings.

- `autoscout24_working_scraper.py`
  - Scrapes car listings from Autoscout24
  - Extracts price, mileage, year, location, fuel type, etc.

- `autoscout24_working_scraper_fixed.py`
  - Alternative or fixed version for scraping stability

👉 Output: raw or semi-clean JSON data

---

### 2️⃣ Data Processing (`scripts/`)
- `convert_scraped_data.py`
  - Cleans raw scraped data
  - Normalizes price, mileage, year
  - Prepares data for analysis & API consumption

---

### 3️⃣ Analysis Engine (`app/ai_calculations.py`)
Handles:
- Market price estimation
- Profit calculation
- Risk scoring

Example logic:
- Compare listing price vs market average
- Penalize high mileage / accident history
- Boost newer models with good resale value

---

### 4️⃣ Recommendation Engine (`app/car_recommendation_engine.py`)
Produces human-readable recommendations:

- ✅ Good Buy
- ⚠️ Needs Review
- ❌ Avoid

Based on:
- Price gap
- Risk score
- Market demand

---

## 🔌 API Layer (FastAPI)

### Entry Point
```bash
uvicorn app.main:app --reload
📡 API Endpoints (Example)
🔹 POST /analyze-car

Analyzes a car listing and returns price, profit & recommendation.

Request (JSON)
{
  "brand": "BMW",
  "model": "320d",
  "year": 2019,
  "mileage": 65000,
  "listed_price": 18500
}

Response (JSON)
{
  "estimated_market_price": 20500,
  "expected_profit": 2000,
  "risk_score": 0.25,
  "recommendation": "GOOD_BUY"
}


👉 Backend engineers can directly use this endpoint inside:

Mobile apps

Web dashboards

Admin panels

(Exact endpoints may vary depending on implementation.)

🔐 Environment Variables

Create a .env file in the project root (do NOT commit this file).

Example:

OPENAI_API_KEY=your_openai_api_key
ENV=development

▶️ How to Run (Local Development)
pip install -r requirements.txt
uvicorn app.main:app --reload
