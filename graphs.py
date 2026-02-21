import matplotlib
matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt
import os


# =====================================================
# Waste Report
# =====================================================
def generate_waste_report(restaurant):
    os.makedirs("static/graphs", exist_ok=True)

    data = pd.read_csv("data/history.csv")
    data = data[data['restaurant'] == restaurant]

    if data.empty:
        plt.figure()
        plt.text(0.5, 0.5, "No data available",
                 ha='center', va='center', fontsize=12)
        plt.axis("off")
        plt.savefig("static/graphs/waste_report.png")
        plt.close()
        return "No Data", 0

    waste_summary = data.groupby("food_item")["wasted"].sum()

    plt.figure(figsize=(6, 4))
    waste_summary.plot(kind="bar")
    plt.title(f"Food Waste Report – {restaurant}")
    plt.ylabel("Units Wasted")
    plt.tight_layout()

    plt.savefig("static/graphs/waste_report.png")
    plt.close()

    return waste_summary.idxmax(), int(waste_summary.max())


# =====================================================
# Top 3 Wasted Foods
# =====================================================
def get_top_3_wasted_foods(restaurant):
    data = pd.read_csv("data/history.csv")
    data = data[data['restaurant'] == restaurant]

    return (
        data.groupby("food_item")["wasted"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
    )


# =====================================================
# Food-wise Cost (₹)
# =====================================================
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


# =====================================================
# Restaurant Comparison
# =====================================================
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


# =====================================================
# Weekly Trend Per Food
# =====================================================
def generate_weekly_food_trend(restaurant, food):
    os.makedirs("static/graphs", exist_ok=True)

    data = pd.read_csv("data/history.csv")
    data = data[
        (data["restaurant"] == restaurant) &
        (data["food_item"] == food)
    ]

    if data.empty:
        return

    base = int(data["sold"].mean())

    weekly_values = [
        int(base * factor)
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


# =====================================================
# 🤖 AI Recommendation (NEW & IMPORTANT)
# =====================================================
def generate_ai_recommendation(restaurant):
    data = pd.read_csv("data/history.csv")
    data = data[data['restaurant'] == restaurant]

    if data.empty:
        return "Not enough data to generate AI recommendation."

    waste_summary = data.groupby("food_item")["wasted"].sum()
    worst_food = waste_summary.idxmax()
    waste_amount = waste_summary.max()

    if waste_amount > 80:
        return (
            f"High waste detected for {worst_food}. "
            f"Reduce preparation by 30% and monitor demand closely."
        )
    elif waste_amount > 40:
        return (
            f"Moderate waste detected for {worst_food}. "
            f"Reduce preparation by 20% to optimize cost."
        )
    else:
        return (
            "Waste levels are under control. "
            "Maintain current preparation strategy."
        )