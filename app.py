from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import sqlite3
from model_interface import get_clusters

# Connect to the database
conn = sqlite3.connect("./data/nutrition.db")
cur = conn.cursor()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-clusters')
def api_get_clusters():
    # Temporary
    get_clusters()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)