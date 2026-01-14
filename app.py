from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from ai_engine import predict_disease
from datetime import datetime

app = Flask(__name__)
app.secret_key = "health_secure"

client = MongoClient("mongodb+srv://terminator:1234567890@cluster0.kdcjwdl.mongodb.net/?appName=Cluster0")
db = client.healthcare

users = db.users
logs = db.health_logs
ops = db.op_requests

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        users.insert_one({
            "name": request.form["name"],
            "email": request.form["email"],
            "phone": request.form["phone"],
            "password": request.form["password"]
        })
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = users.find_one({
            "email": request.form["email"],
            "password": request.form["password"]
        })
        if u:
            session["email"] = u["email"]
            return redirect("/update")
    return render_template("login.html")

@app.route("/update", methods=["GET","POST"])
def update():
    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":
        vitals = {
            "bp": request.form["bp"],
            "sugar": request.form["sugar"],
            "oxygen": request.form["oxygen"],
            "heart": request.form["heart"],
            "cholesterol": request.form["cholesterol"]
        }

        symptoms = request.form["symptoms"]
        result = predict_disease(vitals, symptoms)

        record = {
            "email": session["email"],
            "vitals": vitals,
            "symptoms": symptoms,
            "ai_result": result,
            "date": datetime.now()
        }

        logs.insert_one(record)

        if request.form["book"] == "yes":
            ops.insert_one(record)

        return render_template("done.html", result=result)

    return render_template("step_form.html")

app.run(debug=True)
