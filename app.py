import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_THIS_SECRET_KEY")

db_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url, pool_pre_ping=True)
CENTERS = [f"Center {i}" for i in range(1, 11)]


def init_db():
    with engine.begin() as c:
        if db_url.startswith("sqlite"):
            c.execute(text("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """))
            c.execute(text("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    center TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        else:
            c.execute(text("""
                CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """))
            c.execute(text("""
                CREATE TABLE IF NOT EXISTS entries (
                    id SERIAL PRIMARY KEY,
                    center VARCHAR(80) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

        if c.execute(text("SELECT COUNT(*) FROM admins")).scalar() == 0:
            username = os.environ.get("ADMIN_USERNAME", "admin")
            password = os.environ.get("ADMIN_PASSWORD", "admin123")
            c.execute(
                text("INSERT INTO admins(username,password_hash) VALUES (:u,:p)"),
                {"u": username, "p": generate_password_hash(password)}
            )


@app.route("/", methods=["GET", "POST"])
def entry():
    if request.method == "POST":
        center = request.form.get("center", "")
        name = request.form.get("name", "").strip()
        value = request.form.get("value", "").strip()

        if center not in CENTERS or not name or not value:
            flash("सभी जानकारी भरना जरूरी है।", "error")
        else:
            with engine.begin() as c:
                c.execute(
                    text("INSERT INTO entries(center,name,value) VALUES (:c,:n,:v)"),
                    {"c": center, "n": name, "v": value}
                )
            flash("Entry सफलतापूर्वक सेव हो गई।", "success")
            return redirect(url_for("entry"))

    return render_template("entry.html", centers=CENTERS)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        with engine.begin() as c:
            admin = c.execute(
                text("SELECT * FROM admins WHERE username=:u"),
                {"u": request.form.get("username", "")}
            ).mappings().first()

        if admin and check_password_hash(
            admin["password_hash"],
            request.form.get("password", "")
        ):
            session["admin"] = admin["username"]
            return redirect(url_for("dashboard"))

        flash("गलत Login ID या Password", "error")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))

    center = request.args.get("center", "All")

    with engine.begin() as c:
        if center == "All":
            rows = c.execute(
                text("SELECT * FROM entries ORDER BY id DESC")
            ).mappings().all()
        else:
            rows = c.execute(
                text("SELECT * FROM entries WHERE center=:c ORDER BY id DESC"),
                {"c": center}
            ).mappings().all()

    return render_template(
        "dashboard.html",
        rows=rows,
        center=center,
        centers=CENTERS
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/health")
def health():
    return "OK", 200


init_db()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
