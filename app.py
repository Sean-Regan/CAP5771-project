from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import sqlite3
import os
import re
import model_interface
from dotenv import load_dotenv

load_dotenv()
MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY')
ENDPOINT = "http://localhost:8000"

# Connect to the database
conn = sqlite3.connect("./data/nutrition.db")
cur = conn.cursor()

app = Flask(__name__)
CORS(app)

def normalize_text(str):
    if pd.isna(str):
        return ""
    str = str.lower()
    str = re.sub(r'[^a-z0-9\s]', ' ', str)
    str = re.sub(r'\s+', ' ', str).strip()
    return str

@app.route('/')
def home():
    return render_template('index.html', MAPBOX_API_KEY=MAPBOX_API_KEY, ENDPOINT=ENDPOINT)

@app.route('/api/get-clusters.geojson')
def api_get_clusters():
    return model_interface.get_clusters(5000)

@app.route('/api/nutrition')
def api_get_nutrition_info():
    conn.create_function('normalize_text', 1, normalize_text)

    search_name = request.args.get('name')
    search_brand = request.args.get('brand')
    search_nutrient = request.args.get('nutrient')

    wal_df = pd.read_sql_query("""
                       SELECT clean_desc, name, MIN(amount) as amount, MIN(price_retail) as price
                       FROM wal_nutrient
                       WHERE product_name LIKE ? AND clean_brand LIKE ? AND normalize_text(name) LIKE ?
                       GROUP BY clean_desc, name
                       """, conn, params=(f"%{search_name.value}%", f"%{normalize_text(search_brand.value)}%", f"%{normalize_text(search_nutrient.value)}%"))
    
    wf_df = pd.read_sql_query("""
                       SELECT clean_desc, name, MIN(amount) as amount, MIN(price) as price
                       FROM wf_nutrient
                       WHERE product_name LIKE ? AND clean_brand LIKE ? AND normalize_text(name) LIKE ?
                       GROUP BY clean_desc, name
                       """, conn, params=(f"%{search_name.value}%", f"%{normalize_text(search_brand.value)}%", f"%{normalize_text(search_nutrient.value)}%"))

if __name__ == '__main__':
    model_interface.init_clusters(conn, cur)
    app.run(host='0.0.0.0', port=8000)