import mysql.connector

# =====================================================
# DATABASE CONNECTION (same as app.py)
# =====================================================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vennela",      # change if needed
        database="dinesmart_db"
    )


# =====================================================
# FOOD-WISE DEMAND PREDICTION (NO KAGGLE, NO CSV)
# =====================================================
def predict_food_demand(restaurant_id, food, temperature):
    conn = get_db()
    cursor = conn.cursor()

    # 1️⃣ Base demand = average sold quantity
    cursor.execute("""
        SELECT AVG(sold)
        FROM food_history
        WHERE restaurant_id = %s AND food_item = %s
    """, (restaurant_id, food))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    # ❌ No data yet → sensible default
    if result[0] is None:
        base = 5
    else:
        base = float(result[0])

    # 2️⃣ Temperature scaling (realistic logic)
    if temperature >= 35:
        base *= 1.3
    elif temperature >= 30:
        base *= 1.2
    elif temperature <= 20:
        base *= 0.85

    # 3️⃣ Safety → never 0
    return max(1, int(round(base)))


# =====================================================
# WEEKLY FORECAST (FOOD-WISE)
# =====================================================
def weekly_forecast_food(restaurant_id, food):
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
        return [5, 5, 5, 5, 5, 5, 5]

    avg = int(sum(r[0] for r in rows) / len(rows))
    avg = max(1, avg)

    return [
        int(avg * f)
        for f in [0.9, 0.95, 1.0, 1.1, 1.15, 1.05, 0.95]
    ]