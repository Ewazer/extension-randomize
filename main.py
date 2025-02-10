import os
from flask import Flask, render_template, session, redirect, url_for, request
import json
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
WTF_CSRF_SECRET_KEY = os.urandom(24)
DB_FILENAME = "extensions.db"

def get_random_extension_from_db():
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM extensions ORDER BY RANDOM() LIMIT 1;")
    random_extension = cursor.fetchone()
    conn.close()
    if not random_extension:
        return None

    column_names = [
        "id", "url", "name", "short_description", "long_description",
        "user_count", "languages", "manifest_version", "review_rating",
        "review_count", "similar_extension_ids", "logo_url",
        "banner_image_urls", "banner_video_urls", "category",
        "updated_at", "created_at", "email", "website_url",
        "is_indexed", "is_featured", "is_trader",
        "user_count_time_data", "review_count_time_data", "review_rating_time_data"
    ]

    return {column_names[i]: random_extension[i] for i in range(len(column_names))}

def get_filtered_extensions(category=None, min_rating=0, min_users=0, max_rating=None):
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    query = "SELECT * FROM extensions WHERE 1=1"
    params = []

    if category:
        categories = category.split(",") 
        query += " AND (" + " OR ".join(["category LIKE ?"] * len(categories)) + ")"
        params.extend([f"%{cat.strip()}%" for cat in categories])

    if min_rating:
        query += " AND review_rating >= ?"
        params.append(float(min_rating))

    if min_users:
        query += " AND user_count >= ?"
        params.append(int(min_users))

    if max_rating is not None:
        query += " AND review_rating <= ?"
        params.append(float(max_rating))

    query += " ORDER BY RANDOM() LIMIT 1"

    cursor.execute(query, params)
    random_extension = cursor.fetchone()
    conn.close()

    if not random_extension:
        return None

    column_names = [
        "id", "url", "name", "short_description", "long_description",
        "user_count", "languages", "manifest_version", "review_rating",
        "review_count", "similar_extension_ids", "logo_url",
        "banner_image_urls", "banner_video_urls", "category",
        "updated_at", "created_at", "email", "website_url",
        "is_indexed", "is_featured", "is_trader",
        "user_count_time_data", "review_count_time_data", "review_rating_time_data"
    ]

    return {column_names[i]: random_extension[i] for i in range(len(column_names))}

def get_extension_info(extension):
    return {
        "name": extension.get("name", False),
        "id": extension.get("id", False),
        "url": extension.get("url", False),
        "description-short": extension.get("short_description", False),
        "description": extension.get("long_description", False),
        "rating": round(extension.get("review_rating", 0), 2),
        "review": extension.get("review_count", False),
        "users": extension.get("user_count", False),
        "last_update": datetime.fromisoformat(extension.get("updated_at", False)).date(),
        "created": datetime.fromisoformat(extension.get("created_at", False)).date(),
        "logo": extension.get("logo_url", False),
        "banner": extension.get("banner_image_urls", False).split(", "),
        "category": extension.get("category", False).split('/'),
        "email": extension.get("email", False),
        "website": extension.get("website_url",False),
        "video": extension.get("banner_video_urls", False)
    }

@app.route('/')
def index():
    return redirect(url_for('random_extension'))

@app.route('/random')
def random_extension():
    category = request.args.get('category')
    min_rating = request.args.get('minRating', 0)
    min_users = request.args.get('minUsers', 0)
    max_rating = request.args.get('maxRating')

    extension = get_filtered_extensions(category, min_rating, min_users, max_rating)

    if not extension:
        return render_template('error.html',error="Error" , message="No valid extensions found for the applied filters.")

    extension_info = get_extension_info(extension)
    return render_template('random-extension.html', extension_info=extension_info)

if __name__ == "__main__":
    app.run(debug=True)
