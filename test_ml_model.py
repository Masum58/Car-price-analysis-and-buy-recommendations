"""
Train ML model and save it as ml_model.joblib
"""

import json
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

print("=" * 70)
print("🚗 TRAINING CAR PRICE ML MODEL")
print("=" * 70)

# -----------------------------
# Load dataset
# -----------------------------
with open("cars_data_sample.json", "r", encoding="utf-8") as f:
    cars = json.load(f)

df = pd.DataFrame(cars)

print(f"Loaded {len(df)} cars")

# -----------------------------
# Feature engineering
# -----------------------------
CURRENT_YEAR = 2025

df["age"] = CURRENT_YEAR - df["year_numeric"]

brand_map = {b: i for i, b in enumerate(df["brand"].unique())}
df["brand_encoded"] = df["brand"].map(brand_map)

fuel_map = {f: i for i, f in enumerate(df["fuel_type"].unique())}
df["fuel_encoded"] = df["fuel_type"].map(fuel_map)

df["mileage_per_year"] = df["mileage_numeric"] / df["age"].replace(0, 1)

features = [
    "brand_encoded",
    "age",
    "mileage_numeric",
    "fuel_encoded",
    "mileage_per_year"
]

X = df[features]
y = df["price_numeric"]

# -----------------------------
# Train / test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------
# Train model
# -----------------------------
model = RandomForestRegressor(
    n_estimators=120,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# -----------------------------
# Save model  ✅ VERY IMPORTANT
# -----------------------------
joblib.dump(model, "ml_model.joblib")
print("✅ Model saved as ml_model.joblib")

# -----------------------------
# Evaluate
# -----------------------------
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\nModel Performance:")
print(f"MAE : €{mae:,.0f}")
print(f"RMSE: €{rmse:,.0f}")
print(f"R²  : {r2*100:.1f}%")

print("=" * 70)
print("✅ TRAINING COMPLETE")
print("=" * 70)
