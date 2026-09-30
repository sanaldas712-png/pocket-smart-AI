import json
import os
import sqlite3
from functools import wraps

from dotenv import load_dotenv
from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
import gemini_service as ai  # noqa: E402
from validators import PARSERS  # noqa: E402

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS history (
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, planner TEXT NOT NULL,
  budget REAL, total REAL, result TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""
TITLES = {"home": "Home Interior Budget Planner", "party": "Party Budget Planner",
          "jewelry": "Jewelry Budget Planner"}


def create_app(db_path=None):
    app = Flask(__name__)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-change-me"),
        DATABASE=db_path or os.path.join(app.instance_path, "pocketsmart.db"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024)

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_):
        conn = g.pop("db", None)
        if conn:
            conn.close()

    with app.app_context():
        db().executescript(SCHEMA)

    def login_required(view):
        @wraps(view)
        def wrapped(*a, **kw):
            if "user_id" not in session:
                if request.method == "POST":
                    return jsonify(error="Please log in first."), 401
                return redirect(url_for("login"))
            return view(*a, **kw)
        return wrapped

    # ---------- public pages ----------
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            u = request.form.get("username", "").strip()
            p = request.form.get("password", "")
            if len(u) < 3 or len(p) < 6:
                flash("Username needs 3+ characters and password 6+.")
            else:
                try:
                    db().execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                                 (u, generate_password_hash(p)))
                    db().commit()
                    flash("Account created. Please log in.")
                    return redirect(url_for("login"))
                except sqlite3.IntegrityError:
                    flash("Username already taken.")
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            row = db().execute("SELECT * FROM users WHERE username = ?",
                               (request.form.get("username", "").strip(),)).fetchone()
            if row and check_password_hash(row["password_hash"], request.form.get("password", "")):
                session.clear()
                session.update(user_id=row["id"], username=row["username"])
                return redirect(url_for("dashboard"))
            flash("Invalid username or password.")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    # ---------- logged-in pages ----------
    @app.route("/dashboard")
    @login_required
    def dashboard():
        recent = db().execute("SELECT * FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 5",
                              (session["user_id"],)).fetchall()
        return render_template("dashboard.html", recent=recent, titles=TITLES)

    @app.route("/history")
    @login_required
    def history():
        rows = db().execute("SELECT * FROM history WHERE user_id = ? ORDER BY id DESC",
                            (session["user_id"],)).fetchall()
        return render_template("history.html", rows=rows, titles=TITLES,
                               results=[json.loads(r["result"]) for r in rows])

    def planner_page(kind):
        return render_template("planner.html", kind=kind, title=TITLES[kind])

    for kind in TITLES:
        app.add_url_rule(f"/{kind}-planner", f"{kind}_planner",
                         login_required(lambda k=kind: planner_page(k)))

    # ---------- API: /generate-home, /generate-party, /generate-jewelry ----------
    def generate(kind):
        try:
            data = PARSERS[kind](request.form, request.files)
        except ValueError as e:
            return jsonify(error=str(e)), 400
        result = ai.recommend(kind, data)
        db().execute("INSERT INTO history (user_id, planner, budget, total, result) VALUES (?,?,?,?,?)",
                     (session["user_id"], kind, data["budget"], result["total"], json.dumps(result)))
        db().commit()
        return jsonify(result)

    for kind in TITLES:
        app.add_url_rule(f"/generate-{kind}", f"generate_{kind}",
                         login_required(lambda k=kind: generate(k)), methods=["POST"])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
