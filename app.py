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
# DATABASE HELPER
# =====================================================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vennela",
        database="dinesmart_db"
    )


# =====================================================
# SIGNUP
# =====================================================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO restaurants (name, email, password, role)
                VALUES (%s, %s, %s, 'restaurant')
            """, (name, email, password))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            return render_template("signup.html", error="Email already exists")

    return render_template("signup.html")


# =====================================================
# LOGIN
# =====================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, role
            FROM restaurants
            WHERE email=%s AND password=%s
        """, (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["restaurant_id"] = user[0]
            session["restaurant"] = user[1]
            session["role"] = user[2]

            if user[2] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid login credentials")

    return render_template("login.html")


# =====================================================
# ADD FOOD
# =====================================================
@app.route("/add-food", methods=["GET", "POST"])
def add_food():
    if session.get("role") != "restaurant":
        return redirect(url_for("login"))

    if request.method == "POST":
        food_item = request.form["food_item"]
        prepared = int(request.form["prepared"])
        sold = int(request.form["sold"])
        cost_per_unit = int(request.form["cost_per_unit"])

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
# RESTAURANT DASHBOARD
# =====================================================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if session.get("role") != "restaurant":
        return redirect(url_for("login"))

    restaurant_id = session["restaurant_id"]
    restaurant = session["restaurant"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT food_item
        FROM food_history
        WHERE restaurant_id=%s
    """, (restaurant_id,))
    foods = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    worst_food, waste_qty = generate_waste_report(restaurant_id)
    top_3_waste = get_top_3_wasted_foods(restaurant_id)
    food_costs, total_cost = calculate_food_wise_cost(restaurant_id)
    generate_restaurant_comparison()
    ai_message = generate_ai_recommendation(restaurant_id)

    food_prediction = None
    if request.method == "POST":
        temperature = int(request.form["temperature"])
        food = request.form["food"]
        food_prediction = predict_food_demand(restaurant_id, food, temperature)
        generate_weekly_food_trend(restaurant_id, food)

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
# ✅ ADMIN DASHBOARD — FINAL FIX
# =====================================================
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    selected_restaurant = request.args.get("restaurant_id", type=int)
    analytics = None

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Restaurant list
    cursor.execute("""
        SELECT id, name
        FROM restaurants
        WHERE role='restaurant'
    """)
    restaurants = cursor.fetchall()

    # If a restaurant is selected → load analytics
    if selected_restaurant:
        worst_food, waste_qty = generate_waste_report(selected_restaurant)
        top_3 = get_top_3_wasted_foods(selected_restaurant)
        food_costs, total_cost = calculate_food_wise_cost(selected_restaurant)
        ai_message = generate_ai_recommendation(selected_restaurant)

        analytics = {
            "worst_food": worst_food,
            "waste_qty": waste_qty,
            "top_3": top_3,
            "total_cost": total_cost,
            "ai_message": ai_message
        }

    cursor.close()
    conn.close()

    generate_restaurant_comparison()

    return render_template(
        "admin_dashboard.html",
        restaurants=restaurants,
        selected_restaurant=selected_restaurant,
        analytics=analytics
    )


# =====================================================
# LOGOUT
# =====================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)