import sqlite3
from anxiety_app import app
from flask import render_template, request, redirect, url_for, make_response

# Establish connection to the database
def connect_db():
    conn = sqlite3.connect("anxiety.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = connect_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()
        db.close()

init_db()

# Convert numbers to letters (used in the quiz)
@app.template_filter("getLetter")
def getLetter(number):
    return chr(int(number) + 96).upper() + ")"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test-info")
def info():
    return render_template("info.html")

@app.route("/anxiety-test", methods=["GET", "POST"])
def anxietyTest():
    if request.method == "POST":
        try:
            # Get the value of param 'question', try to convert it to an int.
            # If its 'None' catch the error and redirect.
            questionNumber = int(request.args.get("question"))
            slug = request.path
            data = getTestData(slug.replace("/", ""), questionNumber)

            # Check if parameter is between the range of possible questions
            if 0 < questionNumber <= data["totalQuestions"]:
                return render_template("quiz.html", data=data, questionNumber=questionNumber)
            else:
                raise Exception("-Invalid number.")
        except (TypeError, Exception) as err:
            print("####### -Error.")
            print(err)
            return redirect(url_for("anxietyTest"))
    else:
        # Get first question, its answers and the num of total questions
        if request.args:
            return redirect(url_for("anxietyTest"))

        slug = request.path
        data = getTestData(slug.replace("/", ""), 1)
        if data is None:
            return redirect(url_for("info"))

        return render_template("quiz.html", data=data, questionNumber=1)

@app.route("/results")
def results():
    return "TODO"

def getTestData(slug, questionNumber):
    # First fetch general information about the test
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, total_questions, same_answers FROM tests WHERE slug = ?", (slug,))
    testInfo = cursor.fetchone()

    # Check if the answers will be the same for all the test. 
    if testInfo["same_answers"] == True:
        cursor.execute('''SELECT q.question, a.answer, a.value FROM questions q INNER JOIN answers a ON q.test_id=a.test_id WHERE q.question_number = ? AND q.test_id = ?''', (questionNumber, testInfo["id"]))
        testData = cursor.fetchall()

    conn.close()

    formattedData = {
        "question": testData[0]["question"],
        "answers": {},
        "values": {},
        "totalQuestions": testInfo["total_questions"]
    }

    length = len(testData)
    for row in range(0, length):
        formattedData["answers"][row] = testData[row]["answer"]
        formattedData["values"][row] = testData[row]["value"]

    print("---------------------------")
    print(formattedData)
    print("---------------------------")

    return formattedData