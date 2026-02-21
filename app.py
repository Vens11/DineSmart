from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import sqlite3

from model import predict_food_demand
from graphs import (
    generate_waste_report,
    generate_restaurant_comparison,
    get_top_3_wasted_foods,
    calculate_food_wise_cost,
    generate_weekly_food_trend,
    generate_ai_recommendation   # ✅ IMPORTANT
)

app = Flask(__name__)
app.secret_key = "dinesmart_secret_key"


# =====================================================
# DATABASE HELPER
# =====================================================
def get_db():
    return sqlite3.connect("database.db")


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
                "INSERT INTO restaurants (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
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
            "SELECT id, name FROM restaurants WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["restaurant_id"] = user[0]
            session["restaurant"] = user[1]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid login credentials")

    return render_template("login.html")


# =====================================================
# DASHBOARD
# =====================================================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "restaurant" not in session:
        return redirect(url_for("login"))

    restaurant = session["restaurant"]

    # Load history
    history = pd.read_csv("data/history.csv")
    history = history[history["restaurant"] == restaurant]

    foods = history["food_item"].unique().tolist()

    # ---------------- ANALYTICS ----------------
    worst_food, waste_qty = generate_waste_report(restaurant)

    if waste_qty == 0:
        worst_food = "No data yet"

    top_3_waste = get_top_3_wasted_foods(restaurant).to_dict("records")
    food_costs, total_cost = calculate_food_wise_cost(restaurant)

    generate_restaurant_comparison()

    # ✅ AI RECOMMENDATION (THIS WAS MISSING)
    ai_message = generate_ai_recommendation(restaurant)

    # ---------------- PREDICTION ----------------
    food_prediction = None

    if request.method == "POST":
        try:
            temperature = int(request.form.get("temperature"))
            food = request.form.get("food")

            if food:
                food_prediction = predict_food_demand(
                    restaurant, food, temperature
                )
                generate_weekly_food_trend(restaurant, food)

        except Exception as e:
            print("Prediction error:", e)

    return render_template(
        "dashboard.html",
        restaurant=restaurant,
        foods=foods,
        worst_food=worst_food,
        waste_qty=waste_qty,
        top_3_waste=top_3_waste,
        food_costs=food_costs.to_dict("records"),
        total_cost=total_cost,
        food_prediction=food_prediction,
        ai_message=ai_message   # ✅ PASSED TO TEMPLATE
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