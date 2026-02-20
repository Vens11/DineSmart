import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------- Waste Report ----------------
def generate_waste_report(restaurant):
    os.makedirs("static/graphs", exist_ok=True)

    data = pd.read_csv("data/history.csv")
    data = data[data['restaurant'] == restaurant]

    waste_summary = data.groupby("food_item")["wasted"].sum()

    plt.figure()
    waste_summary.plot(kind="bar")
    plt.title(f"Food Waste Report – {restaurant}")
    plt.ylabel("Units Wasted")

    plt.savefig("static/graphs/waste_report.png")
    plt.close()

    return waste_summary.idxmax(), int(waste_summary.max())


# ---------------- Restaurant Comparison ----------------
def generate_restaurant_comparison():
    os.makedirs("static/graphs", exist_ok=True)

    data = pd.read_csv("data/history.csv")
    summary = data.groupby("restaurant")["wasted"].sum()

    plt.figure()
    summary.plot(kind="bar")
    plt.title("Food Waste Comparison Across Restaurants")
    plt.ylabel("Total Wasted Units")

    plt.savefig("static/graphs/restaurant_comparison.png")
    plt.close()


# ---------------- Weekly Forecast Chart ----------------
def generate_weekly_forecast_chart(restaurant, forecast):
    os.makedirs("static/graphs", exist_ok=True)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    plt.figure()
    plt.plot(days, forecast, marker='o')
    plt.title(f"Weekly Demand Forecast – {restaurant}")
    plt.ylabel("Predicted Demand")

    plt.savefig("static/graphs/weekly_forecast.png")
    plt.close()


# ---------------- Cost Savings ----------------
def calculate_cost_savings(restaurant):
    COST_PER_UNIT = {
        "CampusCafeteria": 20,
        "FastFoodOutlet": 30,
        "FineDineBistro": 50
    }

    data = pd.read_csv("data/history.csv")
    data = data[data['restaurant'] == restaurant]

    total_waste = data['wasted'].sum()
    total_cost = total_waste * COST_PER_UNIT[restaurant]

    # Assume AI reduces waste by 25%
    savings = int(total_cost * 0.25)

    return total_cost, savings
