import pandas as pd
import sqlite3

data_root = "./data/"
nutrients_root = data_root + "nutrients/"

# Connect to the database
conn = sqlite3.connect(data_root + "nutrition.db")
cur = conn.cursor()

# Nutrition datasets
food = pd.read_csv(nutrients_root + "food.csv", usecols=['fdc_id', 'description', 'publication_date'])
branded_food = pd.read_csv(nutrients_root + "branded_food.csv", usecols=['fdc_id', 'brand_owner', 'brand_name', 'subbrand_name', 'gtin_upc', 'serving_size', 'serving_size_unit', 'market_country'])
food_nutrient = pd.read_csv(nutrients_root + "food_nutrient.csv", usecols=['id', 'fdc_id', 'nutrient_id', 'amount'])
nutrient = pd.read_csv(nutrients_root + "nutrient.csv")

# Merge the food (name) and branded_food (brand info) datasets
food = pd.merge(food, branded_food, on='fdc_id')

food.to_sql("food", conn, if_exists="replace", index=False)
food_nutrient.to_sql("food_nutrient", conn, if_exists="replace", index=False)
nutrient.to_sql("nutrient", conn, if_exists="replace", index=False)
conn.commit()

# Price datasets
walmart_price = pd.read_csv(data_root + "WMT_Grocery_202209.csv")
walmart_price.columns = walmart_price.columns.str.lower()

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