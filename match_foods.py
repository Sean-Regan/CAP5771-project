import pandas as pd
import sqlite3
import re

def normalize_text(str):
    if pd.isna(str):
        return ""
    str = str.lower()
    str = re.sub(r'[^a-z0-9\s]', ' ', str)
    str = re.sub(r'\s+', ' ', str).strip()
    return str

# Connect to the database
conn = sqlite3.connect("./data/nutrition.db")
cur = conn.cursor()

conn.create_function('normalize_text', 1, normalize_text)

wf_nutrients_query = """
SELECT wp.zip_code, wp.brand, wp.product_name, wp.price, wm.fdc_id, fn.nutrient_id, n.name, n.unit_name, fn.amount, f.clean_desc, f.clean_brand_owner, f.clean_brand, f.clean_subbrand, f.gtin_upc, f.serving_size, f.serving_size_unit
FROM wholefoods_price wp
JOIN wf_match wm
    ON normalize_text(wp.product_name) = wm.wf_name
JOIN food_nutrient fn
    ON wm.fdc_id = fn.fdc_id
JOIN food f
    ON wm.fdc_id = f.fdc_id
JOIN nutrient n
    ON fn.nutrient_id = n.id;
"""

wal_nutrients_query = """
SELECT wp.shipping_location, wp.brand, wp.product_name, wp.price_retail, wm.fdc_id, fn.nutrient_id, n.name, n.unit_name, fn.amount, f.clean_desc, f.clean_brand_owner, f.clean_brand, f.clean_subbrand, f.gtin_upc, f.serving_size, f.serving_size_unit
FROM walmart_price wp
JOIN wal_match wm
    ON normalize_text(wp.product_name) = wm.wal_name
JOIN food_nutrient fn
    ON wm.fdc_id = fn.fdc_id
JOIN food f
    ON wm.fdc_id = f.fdc_id
JOIN nutrient n
    ON fn.nutrient_id = n.id;
"""

wf_nutrients = pd.read_sql_query(wf_nutrients_query, conn)
wal_nutrients = pd.read_sql_query(wal_nutrients_query, conn)

wf_nutrients.to_sql("wf_nutrient", conn, if_exists="replace", index=False)
wal_nutrients.to_sql("wal_nutrient", conn, if_exists="replace", index=False)
