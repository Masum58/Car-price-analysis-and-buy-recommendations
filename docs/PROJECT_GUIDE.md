# Car Price Analysis & Buy Recommendation System
------------------------------------------------

## 1. Project Overview

This project is an automated backend system that:
- Scrapes used car listings from online marketplaces (e.g. AutoScout24)
- Cleans and normalizes the data
- Analyzes market price and demand
- Estimates profit margin and risk
- Provides AI-powered buy / avoid recommendations via APIs

This system is designed for **data analysis, research, and backend API usage**.

---

## 2. Folder Structure Explained

### app/
Core application logic.

- `routes.py`
  - Main API routes
  - Entry point for analysis and recommendation APIs

- `ai_calculations.py`
  - Market price calculation
  - Profit & risk estimation logic
  - Buy / Avoid decision rules

---

### scrapers/
All car data scraping logic.

- `autoscout24_scraper.py`
  - Main scraper logic (requests-based)

- `autoscout24_selenium.py`
  - Selenium-based scraper (used when site blocks normal requests)

- `autoscout24_final.py`
  - Cleaned & final production scraper

- `autoscout24_vpn.py`
  - Experimental scraper using VPN / proxy logic

- `autoscout_with_cookies.py`
  - Scraper using browser cookies

- `debug_autoscout.py`
  - Debug & testing scraper logic

⚠️ Not all scrapers are meant for production use.
Some are experimental or for testing only.

---

### scripts/
Manual or helper scripts.

- `manual_entry_autoscout.py`
  - Manually add or test scraped car data

- `manual_entry_full.py`
  - Full manual data entry for testing pipeline


- `PROJECT_GUIDE.md`
  - This file
  - Explains how the system works and how to run it
## 3. Which File Should I Run?

### 🔹 To scrape car data (recommended):

```bash
python scrapers/autoscout24_final.py

---


### docs/
Project documentation and guides.

