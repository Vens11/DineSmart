import pandas as pd
import numpy as np

# Load Kaggle dataset
df = pd.read_csv("data/train.csv")

# Keep required columns
df = df[['week', 'meal_id', 'num_orders']]

# Rename columns
df.rename(columns={
    'week': 'date',
    'meal_id': 'menu_item',
    'num_orders': 'quantity_sold'
}, inplace=True)

# Assign restaurants randomly (demo logic)
df['restaurant'] = np.random.choice(
    ['CampusCafeteria', 'FastFoodOutlet', 'FineDineBistro'],
    size=len(df)
)

# Add temperature variation
df['temperature'] = np.random.randint(18, 38, size=len(df))

# Save cleaned dataset
df.to_csv("data/food_sales.csv", index=False)

print("✅ Kaggle dataset cleaned and food_sales.csv created")