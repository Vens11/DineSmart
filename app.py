from flask import Flask, render_template, request, redirect, url_for, session

from model import train_and_predict, weekly_forecast
from graphs import (
    generate_waste_report,
    generate_restaurant_comparison,
    generate_weekly_forecast_chart,
    calculate_cost_savings
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
        else:
            return render_template(
                "login.html",
                error="Invalid restaurant or password"
            )

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'restaurant' not in session:
        return redirect(url_for('login'))

    restaurant = session['restaurant']

    # 1️⃣ Generate waste report
    worst_food, waste_qty = generate_waste_report(restaurant)

    # 2️⃣ Generate restaurant comparison chart
    generate_restaurant_comparison()

    # 3️⃣ Weekly forecast
    forecast = weekly_forecast(restaurant)
    generate_weekly_forecast_chart(restaurant, forecast)

    # 4️⃣ Cost savings
    total_cost, savings = calculate_cost_savings(restaurant)

    # 5️⃣ Demand prediction (form submission)
    prediction = None
    if request.method == 'POST':
        try:
            temperature = int(request.form['temperature'])
            event = int(request.form['event'])
            prediction = train_and_predict(restaurant, temperature, event)
        except:
            prediction = None

    return render_template(
        "dashboard.html",
        restaurant=restaurant,
        worst_food=worst_food,
        waste_qty=waste_qty,
        total_cost=total_cost,
        savings=savings,
        prediction=prediction
    )


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
