from anxiety_app import app
from flask import render_template

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test-info")
def info():
    return render_template("info.html")