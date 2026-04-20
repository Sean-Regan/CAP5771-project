from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import sqlite3
import os
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

@app.route('/')
def home():
    return render_template('index.html', MAPBOX_API_KEY=MAPBOX_API_KEY, ENDPOINT=ENDPOINT)

@app.route('/api/get-clusters.geojson')
def api_get_clusters():
    return model_interface.get_clusters(5000)

@app.route('/api/nutrition')
def api_get_nutrition_info():
    search_name = request.args.get('name')
    search_brand = request.args.get('brand')

    wal_df = pd.read_sql_query("""
                       SELECT price_retail
                       FROM walmart_price
                       WHERE product_name LIKE ? AND brand LIKE ?
                       """, conn, params=(f"%{search_name.value}%", f"%{search_brand.value}%"))
    
    wf_df = pd.read_sql_query("""
                       SELECT price
                       FROM wholefoods_price
                       WHERE product_name LIKE ? AND brand LIKE ?
                       """, conn, params=(f"%{search_name.value}%", f"%{search_brand.value}%"))

if __name__ == '__main__':
    model_interface.init_clusters(conn, cur)
    app.run(host='0.0.0.0', port=8000)