from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

from model import predict_food_demand

from graphs import (
    generate_waste_report,
    generate_restaurant_comparison,
    get_top_3_wasted_foods,
    calculate_food_wise_cost,
    generate_weekly_food_trend
)

app = Flask(__name__)
app.secret_key = "dinesmart_secret_key"


# ---------------- DEMO RESTAURANT LOGINS ----------------
USERS = {
    "campus": {
        "password": "campus123",
        "restaurant": "CampusCafeteria"
    },
    "fastfood": {
        "password": "fast123",
        "restaurant": "FastFoodOutlet"
    },
    "finedine": {
        "password": "dine123",
        "restaurant": "FineDineBistro"
    }
}


# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USERS and USERS[username]['password'] == password:
            session['restaurant'] = USERS[username]['restaurant']
            return redirect(url_for('dashboard'))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'restaurant' not in session:
        return redirect(url_for('login'))

    restaurant = session['restaurant']

    # Load history data
    history = pd.read_csv("data/history.csv")
    history = history[history['restaurant'] == restaurant]

    foods = history['food_item'].unique().tolist()

    # Analytics
    worst_food, waste_qty = generate_waste_report(restaurant)
    top_3_waste = get_top_3_wasted_foods(restaurant).to_dict(orient="records")
    food_costs, total_cost = calculate_food_wise_cost(restaurant)
    generate_restaurant_comparison()

    # Prediction result
    food_prediction = None

    if request.method == 'POST':
        try:
            temperature = int(request.form.get('temperature'))
            food = request.form.get('food')

            if food and temperature:
                food_prediction = predict_food_demand(
                    restaurant, food, temperature
                )
                generate_weekly_food_trend(restaurant, food)

        except Exception as e:
            # Safe fallback (no crash)
            food_prediction = None
            print("Prediction error:", e)

    return render_template(
        "dashboard.html",
        restaurant=restaurant,
        foods=foods,
        worst_food=worst_food,
        waste_qty=waste_qty,
        top_3_waste=top_3_waste,
        food_costs=food_costs.to_dict(orient="records"),
        total_cost=total_cost,
        food_prediction=food_prediction
    )


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)