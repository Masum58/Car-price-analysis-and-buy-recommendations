# This file is ONLY for testing ML price prediction output
# It runs directly from terminal (not FastAPI)

from app.ai_calculations import predict_car_price_ml, load_car_data

print("=" * 60)
print("🚗 ML PRICE PREDICTION TERMINAL TEST (ALL CARS)")
print("=" * 60)

# Load all cars from dataset
cars = load_car_data()

print(f"Total cars loaded: {len(cars)}\n")

# Loop through cars one by one
for idx, car_data in enumerate(cars, start=1):
    print("-" * 60)
    print(f"{idx}. {car_data.get('title', 'Unknown Car')}")

    try:
        predicted_price = predict_car_price_ml(car_data)

        listed_price = car_data.get("price_numeric", 0)

        print("--------------------------------------")
        print(f"Listed Price : €{listed_price}")
        print(f"ML Price     : €{predicted_price}")

        if predicted_price < 0:
            print("❌ RESULT: NEGATIVE PRICE (BUG)")
        elif predicted_price >= listed_price:
            print("✅ RESULT: POSITIVE PRICE (OK / PROFIT POTENTIAL)")
        else:
            print("⚠️ RESULT: POSITIVE BUT BELOW LIST PRICE")

    except Exception as e:
        print("❌ ERROR while predicting:", e)

print("\n✅ Finished ML prediction for all cars")
