import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# ---------------- CONFIG ----------------
MODEL_TYPE = "random_forest"
# Options: "linear", "random_forest"


# ---------------- FOOD-WISE DEMAND PREDICTION ----------------


def predict_food_demand(restaurant, food, temperature):
    data = pd.read_csv("data/food_sales.csv")

    # Try food-specific data
    food_data = data[
        (data['restaurant'] == restaurant) &
        (data['menu_item'] == food)
    ]

    # ❗ If food not found in Kaggle data → fallback
    if food_data.empty:
        restaurant_data = data[data['restaurant'] == restaurant]

        if restaurant_data.empty:
            return 0

        X = restaurant_data[['temperature']]
        y = restaurant_data['quantity_sold']

    else:
        X = food_data[['temperature']]
        y = food_data['quantity_sold']

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )
    model.fit(X, y)

    input_df = pd.DataFrame([[temperature]], columns=['temperature'])
    prediction = model.predict(input_df)

    return int(prediction[0])

# ---------------- WEEKLY FORECAST (FOOD-WISE) ----------------
def weekly_forecast_food(restaurant, food):
    data = pd.read_csv("data/food_sales.csv")

    data = data[
        (data['restaurant'] == restaurant) &
        (data['menu_item'] == food)
    ]

    avg = int(data['quantity_sold'].mean())
    return [avg + i * 5 for i in range(7)]


# ---------------- INTERNAL MODEL SELECTOR ----------------
def _get_model():
    if MODEL_TYPE == "linear":
        return LinearRegression()

    elif MODEL_TYPE == "random_forest":
        return RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

    else:
        raise ValueError("Invalid MODEL_TYPE")