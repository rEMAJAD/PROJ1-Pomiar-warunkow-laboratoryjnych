from flask import Flask, jsonify, send_from_directory
import sqlite3
import os

DB_PATH = "pomiar.db"

app = Flask(__name__)

def get_last_n(n=200):
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT strftime('%Y-%m-%d %H:%M:%S', ts), temp, hum
            FROM pomiary
            ORDER BY id DESC
            LIMIT ?
        """, (n,))
        rows = cur.fetchall()
        conn.close()
        rows.reverse()
        return rows
    except Exception as e:
        print("Blad bazy:", e)
        return []

@app.route("/api/data")
def api_data():
    rows = get_last_n(200)
    return jsonify([
        {"ts": ts, "temp": float(temp), "hum": float(hum)}
        for ts, temp, hum in rows
    ])

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
