from anxiety_app import app
from flask import render_template, request, redirect, url_for, make_response

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
    # Length of the quiz
    totalQuestions = len(questions)

    if request.method == "POST":
        # TODO If the user is sending the form, validate it and return a new url
        if request.mimetype == "multipart/form-data":
            req = request.form

            return make_response({"url": "results?=3GR2Y6FHF267D2GJ34G34U"})
        else :
            try:
                # Get the value of param 'question', try to convert it to an int.
                # If its 'None' catch the error and redirect.
                questionNumber = int(request.args.get("question"))

                # Check if parameter is between the range of possible questions
                if 0 < questionNumber <= totalQuestions:
                    return render_template("questions.html", question=questions[questionNumber], questionNumber=questionNumber, totalQuestions=totalQuestions)
                else:
                    raise Exception("-Invalid number.")
            except (TypeError, Exception):
                return redirect(url_for("anxietyTest"))
    else:
        if request.args:
            return redirect(url_for("anxietyTest"))
        return render_template("quiz.html", question=questions[1], questionNumber=1, totalQuestions=totalQuestions)

@app.route("/results")
def results():
    return "TODO"

# Example DICT
questions = {
    1: {
        "question": "Fidgeting, restlessness or pacing, tremor of hands, furrowed brow, strained face, sighing or rapid respiration, facial pallor, swallowing, etc.",
        "answers": {
            1: "Not possible",
            2: "I don't know",
            3: "More less"
        },
        "answersValues": {
            1: 5,
            2: 4,
            3: 3
        }
    },
    2: {
        "question": "What do you think about this website in general?",
        "answers": {
            1: "Not possible",
            2: "I don't know",
            3: "More less"
        },
        "answersValues": {
            1: 5,
            2: 4,
            3: 3
        }
    },
    3: {
        "question": "Do you believe that you can become someone that noone thinks you can be?, or its all a lie?",
        "answers": {
            1: "Not possible",
            2: "I don't know",
            3: "More less"
        },
        "answersValues": {
            1: 5,
            2: 4,
            3: 3
        }
    }
}