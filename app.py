import os
import socket
from flask import Flask, request, redirect
from markupsafe import escape
import psycopg2

app = Flask(__name__)
VERSION = "v1"


def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ.get("DB_NAME", "learning_db"),
        user=os.environ.get("DB_USER", "learning_user"),
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )


def init_db(cur):
    cur.execute("CREATE TABLE IF NOT EXISTS courses (id SERIAL PRIMARY KEY, title TEXT NOT NULL)")
    cur.execute("SELECT COUNT(*) FROM courses")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO courses (title) VALUES ('DevOps Basics'), ('AWS Fundamentals'), ('Docker 101')")


@app.route("/")
def home():
    with get_conn() as conn, conn.cursor() as cur:
        init_db(cur)
        cur.execute("SELECT title FROM courses ORDER BY id")
        courses = "".join(f"<li>{escape(r[0])}</li>" for r in cur.fetchall())
    server = os.environ.get("APP_SERVER", socket.gethostname())
    return f"""
    <h1>Online Learning Platform</h1>
    <p>Version: <b>{VERSION}</b> | Served by: <b>{server}</b></p>
    <h3>Courses</h3><ul>{courses}</ul>
    <form method="post" action="/add">
      <input name="title" placeholder="New course" required>
      <button type="submit">Add course</button>
    </form>
    """


@app.route("/add", methods=["POST"])
def add():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO courses (title) VALUES (%s)", (request.form["title"],))
    return redirect("/")


@app.route("/health")
def health():
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return {"status": "ok", "database": "connected", "version": VERSION}
    except Exception as e:
        return {"status": "error", "database": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
