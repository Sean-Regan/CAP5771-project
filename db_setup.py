import pandas as pd
import sqlite3

data_root = "./data/"
nutrients_root = data_root + "nutrients/"

# Connect to the database
conn = sqlite3.connect(data_root + "test.db")
cur = conn.cursor()

# Nutrition datasets
food = pd.read_csv(nutrients_root + "food.csv")
branded_food = pd.read_csv(nutrients_root + "branded_food.csv")
food_nutrient = pd.read_csv(nutrients_root + "food_nutrient.csv")
nutrient = pd.read_csv(nutrients_root + "nutrient.csv")

# Merge the food (name) and branded_food (brand info) datasets
food = food.drop(columns=["market_country","trade_channel","microbe_data"])
branded_food = branded_food.drop(columns=["not_a_significant_source_of", "household_serving_fulltext", "branded_food_category", "data_source", "package_weight", "preparation_state_code", "trade_channel", "short_description"])
food = pd.merge(food, branded_food, on='fdc_id')

food_nutrient = food_nutrient.drop(columns=["data_points","derivation_id","min","max","median","footnote","min_year_acquired"])

food.to_sql("food", conn, if_exists="replace", index=False)
food_nutrient.to_sql("food_nutrient", conn, if_exists="replace", index=False)
nutrient.to_sql("nutrient", conn, if_exists="replace", index=False)
conn.commit()

# Price datasets
walmart_price = pd.read_csv(data_root + "WMT_Grocery_202209.csv")
walmart_price.columns = walmart_price.columns.str.lower()

# walmart_price = walmart_price.drop(columns=['product_url'])

walmart_price.to_sql("walmart_price", conn, if_exists="replace", index=False)
conn.commit()

# Delete duplicates
cur.execute("""
            DELETE FROM food
            WHERE rowid NOT IN (
                SELECT rowid
                FROM food
                GROUP BY gtin_upc
                HAVING (COUNT(*) = 1 OR MAX(publication_date))
            )
            """)
conn.commit()

# Close the connection
conn.close()