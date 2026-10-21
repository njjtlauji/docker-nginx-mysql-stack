"""A tiny visit counter that stores visits in MySQL.

Endpoints:
  GET /        -> records a visit and returns the total count
  GET /health  -> 200 if the app can reach the database
"""
import os
import time

import pymysql
from flask import Flask, jsonify

app = Flask(__name__)


def get_connection(retries: int = 10, delay: float = 2.0):
    """Connect to MySQL, retrying while the database starts up."""
    last_error = None
    for _ in range(retries):
        try:
            return pymysql.connect(
                host=os.environ["DB_HOST"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"],
                connect_timeout=5,
                autocommit=True,
            )
        except pymysql.MySQLError as exc:
            last_error = exc
            time.sleep(delay)
    raise last_error


def init_db():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS visits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


@app.route("/")
def index():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO visits () VALUES ()")
        cur.execute("SELECT COUNT(*) FROM visits")
        (count,) = cur.fetchone()
    return jsonify(message="Hello from Docker + Nginx + MySQL", visits=count)


@app.route("/health")
def health():
    try:
        with get_connection(retries=1) as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return jsonify(status="ok"), 200
    except Exception as exc:  # noqa: BLE001 - report any DB failure
        return jsonify(status="error", detail=str(exc)), 503


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
