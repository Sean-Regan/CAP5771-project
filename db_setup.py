import pandas as pd
import sqlite3

data_root = "./data/"
nutrients_root = data_root + "nutrients/"

# Connect to the database
conn = sqlite3.connect(data_root + "test.db")

# Nutrition datasets
food = pd.read_csv(nutrients_root + "food.csv")
food_nutrient = pd.read_csv(nutrients_root + "food_nutrient.csv")
nutrient = pd.read_csv(nutrients_root + "nutrient.csv")

food = food.drop(columns=["market_country","trade_channel","microbe_data"])
food_nutrient = food_nutrient.drop(columns=["data_points","derivation_id","min","max","median","footnote","min_year_acquired"])

food.to_sql("food", conn, if_exists="replace", index=False)
food_nutrient.to_sql("food_nutrient", conn, if_exists="replace", index=False)
nutrient.to_sql("nutrient", conn, if_exists="replace", index=False)

# Price datasets
walmart_price = pd.read_csv(data_root + "WMT_Grocery_202209.csv")
walmart_price.columns = walmart_price.columns.str.lower()

walmart_price.to_sql("walmart_price", conn, if_exists="replace", index=False)

# Commit and close the sqlite connection
conn.commit()
conn.close()