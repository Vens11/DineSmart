import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# ---------------- CONFIG ----------------
MODEL_TYPE = "random_forest"

# Change to "random_forest" if needed


# ---------------- TRAIN & PREDICT ----------------
def train_and_predict(restaurant, temperature, event):
    data = pd.read_csv("data/food_sales.csv")
    data = data[data['restaurant'] == restaurant]

    X = data[['temperature', 'event']]
    y = data['quantity_sold']

    if MODEL_TYPE == "linear":
        model = LinearRegression()

    elif MODEL_TYPE == "random_forest":
        model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

    else:
        raise ValueError("Invalid MODEL_TYPE")

    model.fit(X, y)

    prediction = model.predict([[temperature, event]])
    return int(prediction[0])


# ---------------- WEEKLY FORECAST ----------------
def weekly_forecast(restaurant):
    data = pd.read_csv("data/food_sales.csv")
    data = data[data['restaurant'] == restaurant]

    avg = int(data['quantity_sold'].mean())
    return [avg + i * 5 for i in range(7)]
