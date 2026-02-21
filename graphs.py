import matplotlib
matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt
import os


# ---------------- Waste Report ----------------
def generate_waste_report(restaurant):
    os.makedirs("static/graphs", exist_ok=True)

    data = pd.read_csv("data/history.csv")
    data = data[data['restaurant'] == restaurant]

    waste_summary = data.groupby("food_item")["wasted"].sum()

    plt.figure(figsize=(7, 4))
    waste_summary.plot(kind="bar")
    plt.title(f"Food Waste Report – {restaurant}")
    plt.ylabel("Units Wasted")
    plt.xlabel("Food Item")
    plt.tight_layout()

    plt.savefig("static/graphs/waste_report.png")
    plt.close()

    return waste_summary.idxmax(), int(waste_summary.max())


# ---------------- Top 3 Wasted Foods ----------------
def get_top_3_wasted_foods(restaurant):
    data = pd.read_csv("data/history.csv")
    data = data[data['restaurant'] == restaurant]

    top_3 = (
        data.groupby("food_item")["wasted"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
    )

    return top_3


# ---------------- Food-wise Cost (₹) ----------------
def calculate_food_wise_cost(restaurant):
    data = pd.read_csv("data/history.csv")
    data = data[data['restaurant'] == restaurant]

    data["waste_cost"] = data["wasted"] * data["cost_per_unit"]

    food_cost = (
        data.groupby("food_item")["waste_cost"]
        .sum()
        .reset_index()
    )

    total_cost = int(food_cost["waste_cost"].sum())

    return food_cost, total_cost


# ---------------- Restaurant Comparison ----------------
def generate_restaurant_comparison():
    os.makedirs("static/graphs", exist_ok=True)

    data = pd.read_csv("data/history.csv")
    summary = data.groupby("restaurant")["wasted"].sum()

    plt.figure(figsize=(7, 4))
    summary.plot(kind="bar")
    plt.title("Food Waste Comparison Across Restaurants")
    plt.ylabel("Total Wasted Units")
    plt.tight_layout()

    plt.savefig("static/graphs/restaurant_comparison.png")
    plt.close()


# ---------------- Weekly Forecast Chart (Overall) ----------------
def generate_weekly_forecast_chart(restaurant, forecast):
    os.makedirs("static/graphs", exist_ok=True)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    plt.figure(figsize=(6, 4))
    plt.plot(days, forecast, marker='o')
    plt.title(f"Weekly Demand Forecast – {restaurant}")
    plt.ylabel("Predicted Demand")
    plt.xlabel("Day")
    plt.tight_layout()

    plt.savefig("static/graphs/weekly_forecast.png")
    plt.close()


# ---------------- Weekly Trend Per Food ----------------
def generate_weekly_food_trend(restaurant, food):
    os.makedirs("static/graphs", exist_ok=True)

    # Create dummy weekly trend from waste data (demo purpose)
    data = pd.read_csv("data/history.csv")
    data = data[
        (data["restaurant"] == restaurant) &
        (data["food_item"] == food)
    ]

    # Simulated weekly trend
    weekly_values = [
        int(data["sold"].values[0] * factor)
        for factor in [0.8, 0.9, 1.0, 1.1, 1.0, 0.95, 0.9]
    ]

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    plt.figure(figsize=(6, 4))
    plt.plot(days, weekly_values, marker="o")
    plt.title(f"Weekly Trend – {food}")
    plt.ylabel("Units Sold")
    plt.xlabel("Day")
    plt.tight_layout()

    plt.savefig("static/graphs/weekly_food_trend.png")
    plt.close()