from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

from model import predict_food_demand
from graphs import (
    generate_waste_report,
    generate_restaurant_comparison,
    get_top_3_wasted_foods,
    calculate_food_wise_cost,
    generate_weekly_food_trend,
    generate_ai_recommendation
)

app = Flask(__name__)
app.secret_key = "dinesmart_secret_key"


# =====================================================
# DATABASE HELPER (MySQL)
# =====================================================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vennela",   # change if needed
        database="dinesmart_db"
    )


# =====================================================
# SIGN UP
# =====================================================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO restaurants (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:
            return render_template(
                "signup.html",
                error="Restaurant or email already exists"
            )

    return render_template("signup.html")


# =====================================================
# LOGIN
# =====================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name FROM restaurants WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["restaurant_id"] = user[0]
            session["restaurant"] = user[1]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid login credentials")

    return render_template("login.html")


# =====================================================
# ADD FOOD DATA
# =====================================================
@app.route("/add-food", methods=["GET", "POST"])
def add_food():
    if "restaurant_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        food_item = request.form.get("food_item")
        prepared = int(request.form.get("prepared"))
        sold = int(request.form.get("sold"))
        cost_per_unit = int(request.form.get("cost_per_unit"))

        wasted = max(prepared - sold, 0)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO food_history
            (restaurant_id, food_item, prepared, sold, wasted, cost_per_unit)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session["restaurant_id"],
            food_item,
            prepared,
            sold,
            wasted,
            cost_per_unit
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_food.html")


# =====================================================
# DASHBOARD
# =====================================================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "restaurant_id" not in session:
        return redirect(url_for("login"))

    restaurant_id = session["restaurant_id"]
    restaurant = session["restaurant"]

    # ---------------- FOOD LIST ----------------
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT food_item
        FROM food_history
        WHERE restaurant_id = %s
    """, (restaurant_id,))

    foods = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # ---------------- ANALYTICS ----------------
    worst_food, waste_qty = generate_waste_report(restaurant_id)
    if waste_qty == 0:
        worst_food = "No data yet"

    top_3_waste = get_top_3_wasted_foods(restaurant_id)
    food_costs, total_cost = calculate_food_wise_cost(restaurant_id)

    generate_restaurant_comparison()

    ai_message = generate_ai_recommendation(restaurant_id)

    # ---------------- PREDICTION ----------------
    food_prediction = None

    if request.method == "POST":
        try:
            temperature = int(request.form.get("temperature"))
            food = request.form.get("food")

            if food:
                food_prediction = predict_food_demand(
                    restaurant_id, food, temperature   # ✅ FIXED
                )
                generate_weekly_food_trend(restaurant_id, food)

        except Exception as e:
            print("Prediction error:", e)

    return render_template(
        "dashboard.html",
        restaurant=restaurant,
        foods=foods,
        worst_food=worst_food,
        waste_qty=waste_qty,
        top_3_waste=top_3_waste,
        food_costs=food_costs,
        total_cost=total_cost,
        food_prediction=food_prediction,
        ai_message=ai_message
    )


# =====================================================
# LOGOUT
# =====================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================================================
# RUN APP
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)