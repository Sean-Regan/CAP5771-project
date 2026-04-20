from flask import jsonify
import pandas as pd
import pgeocode
import random
import re
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans

nutrients_arr = pd.DataFrame([])
global_nomi = pgeocode.Nominatim('us')

def get_lat_lon(zip_code: int) -> (float, float):
    global global_nomi
    query = global_nomi.query_postal_code([str(zip_code)])
    return (query.latitude.iloc[0], query.longitude.iloc[0])

def normalize_text(str):
    if pd.isna(str):
        return ""
    str = str.lower()
    str = re.sub(r'[^a-z0-9\s]', ' ', str)
    str = re.sub(r'\s+', ' ', str).strip()
    return str

def create_clusters(conn):
    print("Generating clusters...")
    conn.create_function('normalize_text', 1, normalize_text)

    wf_nutrients_query = """
    SELECT fn.nutrient_id, wp.zip_code, wp.price, normalize_text(f.brand_owner)
    FROM wholefoods_price wp
    JOIN wf_match wm
        ON normalize_text(wp.product_name) = wm.wf_name
    JOIN food_nutrient fn
        ON wm.fdc_id = fn.fdc_id
    JOIN food f
        ON wm.fdc_id = f.fdc_id;
    """

    wal_nutrients_query = """
    SELECT fn.nutrient_id, wp.shipping_location, wp.price_retail, normalize_text(f.brand_owner)
    FROM walmart_price wp
    JOIN wf_match wm
        ON normalize_text(wp.product_name) = wm.wf_name
    JOIN food_nutrient fn
        ON wm.fdc_id = fn.fdc_id
    JOIN food f
        ON wm.fdc_id = f.fdc_id;
    """

    wf_nutrients = pd.read_sql_query(wf_nutrients_query, conn)
    wal_nutrients = pd.read_sql_query(wal_nutrients_query, conn)

    wf_nutrients['lat_lon'] = wf_nutrients['zip_code'].apply(get_lat_lon)
    wf_nutrients[['latitude', 'longitude']] = pd.DataFrame(wf_nutrients['lat_lon'].tolist(), index=wf_nutrients.index)
    wf_nutrients.drop(columns=['lat_lon'])

    wal_nutrients['lat_lon'] = wal_nutrients['shipping_location'].apply(get_lat_lon)
    wal_nutrients[['latitude', 'longitude']] = pd.DataFrame(wal_nutrients['lat_lon'].tolist(), index=wal_nutrients.index)
    wal_nutrients = wal_nutrients.drop(columns=['lat_lon'])

    wal_nutrients = wal_nutrients.rename(columns={'normalize_text(f.brand_owner)': 'brand_owner', 'price_retail': 'price', 'shipping_location': 'zip_code'})
    wf_nutrients = wf_nutrients.rename(columns={'normalize_text(f.brand_owner)': 'brand_owner'})

    wf_nutrients['source_wf'] = 1
    wf_nutrients['source_wal'] = 0

    wal_nutrients['source_wf'] = 0
    wal_nutrients['source_wal'] = 1

    shared_cols = ['nutrient_id', 'price', 'latitude', 'longitude', 'brand_owner', 'source_wf', 'source_wal', 'zip_code']
    wf_selected = wf_nutrients[shared_cols]
    wal_selected = wal_nutrients[shared_cols]

    encoded_nutrients = pd.concat([wf_selected, wal_selected], ignore_index=True)
    encoded_nutrients['brand_owner_encoded'] = LabelEncoder().fit_transform(encoded_nutrients.brand_owner)
    encoded_nutrients = encoded_nutrients.drop(columns=['brand_owner'])
    encoded_nutrients = encoded_nutrients.dropna()

    # CALCULATE RESIDUALS
    X = encoded_nutrients[['nutrient_id', 'brand_owner_encoded', 'source_wf', 'source_wal', 'latitude', 'longitude']]
    y = encoded_nutrients['price']

    encoded_nutrients.to_sql("encoded_nutrients", conn, if_exists='replace', index=False)

    model = RandomForestRegressor()
    model.fit(X, y)

    preds = model.predict(X)
    encoded_nutrients['residual'] = y - preds

    # CLUSTER RESIDUALS FOR DEVIATIONS
    residuals = encoded_nutrients[['residual', 'latitude', 'longitude']].values

    kmeans = KMeans(n_clusters=30, random_state=42)
    encoded_nutrients['residual_cluster'] = kmeans.fit_predict(residuals)

    finalized_nutrients = encoded_nutrients[['nutrient_id', 'price', 'latitude', 'longitude', 'residual_cluster']]
    finalized_nutrients.to_sql(name='finalized_nutrients', con=conn, if_exists='replace', index=False)

    global nutrients_arr
    nutrients_arr = encoded_nutrients

def init_clusters(conn, cursor):
    print("Initializing clusters...")
    cursor.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='finalized_nutrients' ''')
    if cursor.fetchone()[0] == 0:
        create_clusters(conn)
    else:
        print("Reading from table...")
        nutrients = pd.read_sql_query('SELECT * FROM finalized_nutrients', con=conn)
        global nutrients_arr
        nutrients_arr = nutrients

def get_clusters(max_clusters=500):
    features_list = []
    global nutrients_arr
    for i in range(min(nutrients_arr.shape[0], max_clusters)):
        # Random offsets are necessary since all of the lon/lat pairs are the same for every zip code. This gives them a bit better of a spread.
        r = random.Random()
        lon_offset = (r.randrange(0, 50) - r.randrange(0, 50)) / 1000
        lat_offset = (r.randrange(0, 50) - r.randrange(0, 50)) / 1000

        row = nutrients_arr.iloc[i]
        nutrient = row.nutrient_id
        price = row.price
        lat = row.latitude
        lon = row.longitude
        cluster = row.residual_cluster
        features_list.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon) + lon_offset, float(lat) + lat_offset]
            },
            "properties": {
                "nutrient": int(nutrient),
                "price": float(price),
                "cluster": int(cluster)
            }
        })

    final_json = {"type": "FeatureCollection", "features": features_list}

    return jsonify(final_json)
        