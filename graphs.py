import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os
import mysql.connector


# =====================================================
# DATABASE CONNECTION (MUST MATCH app.py)
# =====================================================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vennela",          # 🔴 change if needed
        database="dinesmart_db"      # ✅ MUST match app.py
    )


# =====================================================
# Waste Report
# =====================================================
def generate_waste_report(restaurant_id):
    os.makedirs("static/graphs", exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT food_item, SUM(wasted) AS total_waste
        FROM food_history
        WHERE restaurant_id = %s
        GROUP BY food_item
    """, (restaurant_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        plt.figure()
        plt.text(0.5, 0.5, "No data available",
                 ha="center", va="center", fontsize=12)
        plt.axis("off")
        plt.savefig("static/graphs/waste_report.png")
        plt.close()
        return "No Data", 0

    foods = [r[0] for r in rows]
    wasted = [r[1] for r in rows]

    plt.figure(figsize=(6, 4))
    plt.bar(foods, wasted)
    plt.title("Food Waste Report")
    plt.ylabel("Units Wasted")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("static/graphs/waste_report.png")
    plt.close()

    max_index = wasted.index(max(wasted))
    return foods[max_index], int(wasted[max_index])


# =====================================================
# Top 3 Wasted Foods
# =====================================================
def get_top_3_wasted_foods(restaurant_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT food_item, SUM(wasted) AS wasted
        FROM food_history
        WHERE restaurant_id = %s
        GROUP BY food_item
        ORDER BY wasted DESC
        LIMIT 3
    """, (restaurant_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# =====================================================
# Food-wise Cost (₹)
# =====================================================
def calculate_food_wise_cost(restaurant_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT food_item,
               SUM(wasted * cost_per_unit) AS waste_cost
        FROM food_history
        WHERE restaurant_id = %s
        GROUP BY food_item
    """, (restaurant_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    total_cost = int(sum(r["waste_cost"] for r in rows)) if rows else 0
    return rows, total_cost


# =====================================================
# Restaurant Comparison (Admin View)
# =====================================================
def generate_restaurant_comparison():
    os.makedirs("static/graphs", exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.name, SUM(f.wasted) AS total_waste
        FROM food_history f
        JOIN restaurants r ON r.id = f.restaurant_id
        GROUP BY r.name
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        return

    names = [r[0] for r in rows]
    wasted = [r[1] for r in rows]

    plt.figure(figsize=(5, 3))
    plt.bar(names, wasted)
    plt.title("Food Waste Comparison", fontsize=11)
    plt.ylabel("Wasted Units", fontsize=9)
    plt.xticks(rotation=20, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.savefig("static/graphs/restaurant_comparison.png")
    plt.close()


# =====================================================
# Weekly Trend Per Food
# =====================================================
def generate_weekly_food_trend(restaurant_id, food):
    os.makedirs("static/graphs", exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sold
        FROM food_history
        WHERE restaurant_id = %s AND food_item = %s
    """, (restaurant_id, food))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        return

    base = int(sum(r[0] for r in rows) / len(rows))

    weekly_values = [
        int(base * f)
        for f in [0.85, 0.95, 1.0, 1.1, 1.05, 0.98, 0.9]
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
# 🤖 AI Recommendation (Dynamic & Correct)
# =====================================================
def generate_ai_recommendation(restaurant_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT food_item, SUM(wasted) AS total_waste
        FROM food_history
        WHERE restaurant_id = %s
        GROUP BY food_item
    """, (restaurant_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        return "Add food data to receive AI recommendations."

    worst_food, waste_amount = max(rows, key=lambda x: x[1])

    if waste_amount > 100:
        return f"🚨 {worst_food} has very high waste. Reduce preparation by 30% immediately."
    elif waste_amount > 50:
        return f"⚠️ {worst_food} shows moderate waste. Reduce preparation by 20%."
    else:
        return "✅ Waste levels are healthy. Maintain current preparation strategy."