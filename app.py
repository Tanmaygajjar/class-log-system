from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"

def get_db():
    return sqlite3.connect("database.db")


@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        name = request.form["name"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT * FROM users WHERE name=?", (name,))
        user = cur.fetchone()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["name"] = user[1]
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute(
        "SELECT entry_time, exit_time, work_done FROM logs WHERE user_id=? AND date=?",
        (session["user_id"], today)
    )

    log = cur.fetchone()

    return render_template("dashboard.html", log=log, name=session["name"])

@app.route("/enter")
def enter():

    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    # Check if entry already exists today
    cur.execute(
        "SELECT * FROM logs WHERE user_id=? AND date=?",
        (session["user_id"], date)
    )

    existing_log = cur.fetchone()

    if existing_log:
        return redirect("/dashboard")

    # Insert entry if not already entered
    cur.execute(
        "INSERT INTO logs (user_id,date,entry_time) VALUES (?,?,?)",
        (session["user_id"], date, time)
    )

    db.commit()

    return redirect("/dashboard")


@app.route("/exit")
def exit():

    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    cur.execute("""
        SELECT * FROM logs
        WHERE user_id=? AND date=? AND exit_time IS NULL
    """, (session["user_id"], date))

    log = cur.fetchone()

    if not log:
        return redirect("/dashboard")

    cur.execute("""
        UPDATE logs
        SET exit_time=?
        WHERE user_id=? AND date=? AND exit_time IS NULL
    """, (time, session["user_id"], date))

    db.commit()

    return redirect("/dashboard")


@app.route("/logs")
def logs():

    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    cur.execute("""
SELECT users.name, logs.date, logs.entry_time, logs.exit_time, logs.work_done
FROM logs
JOIN users ON users.id = logs.user_id
ORDER BY logs.date DESC
""")

    data = cur.fetchall()

    return render_template("logs.html", data=data)


@app.route("/save_work", methods=["POST"])
def save_work():

    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    work = request.form["work_done"]

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        UPDATE logs
        SET work_done=?
        WHERE user_id=? AND date=?
    """, (work, session["user_id"], today))

    db.commit()

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    
    session.clear()
    return redirect("/")


@app.route("/reset_today")
def reset_today():

    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        DELETE FROM logs
        WHERE user_id=? AND date=?
    """, (session["user_id"], today))

    db.commit()

    return redirect("/dashboard")


app.run(debug=True)