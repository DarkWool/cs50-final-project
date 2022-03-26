from anxiety_app import app

@app.route("/")
def index():
    return "First commit!"