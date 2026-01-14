from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "admin_secure"

client = MongoClient("mongodb+srv://terminator:1234567890@cluster0.kdcjwdl.mongodb.net/?appName=Cluster0")
db = client.healthcare

admins = db.admins
logs = db.health_logs
ops = db.op_requests

@app.route("/", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        admin = admins.find_one({
            "email": request.form["email"],
            "password": request.form["password"]
        })
        if admin:
            session["admin"] = True
            return redirect("/dashboard")
    return render_template("admin_login.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "admin" not in session:
        return redirect("/")

    search = request.form.get("search")
    records = logs.find({"email": search}) if search else logs.find()

    return render_template("admin_dashboard.html",
                           logs=records,
                           ops=ops.find())

app.run(port=5001, debug=True)
