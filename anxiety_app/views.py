import os
import psycopg2.extras as ext

from flask_login import login_required, current_user, logout_user
from anxiety_app import app
from dotenv import load_dotenv
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    make_response,
    flash,
    abort,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from datetime import datetime

from anxiety_app.db import connect_db, single_query
from anxiety_app.forms import changePasswordForm
from anxiety_app.helpers import getNextQuestion, getTestResult, getQuote
from anxiety_app.auth import User

load_dotenv()

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


@app.route("/dashboard")
@login_required
def dashboard():
    date = single_query(
        "SELECT TO_CHAR(date_created, 'Month DD, YYYY') as date FROM users WHERE id = %s", (current_user.id,)
    )

    return render_template("users/dashboard.html", date=date["date"])


@app.route("/my-results")
@login_required
def myresults():
    userId = current_user.id

    userTests = single_query(
        "SELECT t.name, r.hash, r.id, r.date, r.keyword FROM tests t INNER JOIN results r ON t.id=r.test_id WHERE r.user_id = %s",
        (userId,),
        True,
    )

    return render_template("users/my-results.html", userTests=userTests)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def changePassword():
    form = changePasswordForm()

    if request.method == "POST" and form.validate_on_submit():
        password = form.data["password"]
        newPassword = form.data["newPassword"]

        try:
            userId = int(current_user.get_id())
        except ValueError as err:
            return redirect(url_for("login"))

        conn = connect_db()
        cursor = conn.cursor(cursor_factory=ext.DictCursor)
        cursor.execute("SELECT password FROM users WHERE id = %s", (userId,))
        userPassword = cursor.fetchone()["password"]

        if not check_password_hash(userPassword, password):
            flash("Incorrect password", "error")
            cursor.close()
            conn.close()
            return redirect(url_for("changePassword"))

        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (generate_password_hash(newPassword), userId),
        )
        conn.commit()

        cursor.close()
        conn.close()

        logout_user()

        flash("Success!", "success")
        flash("Please, log in again with your new password", "success")
        return redirect(url_for("changePassword"))

    return render_template("users/change-password.html", form=form)


@app.route("/")
def index():
    quote = getQuote()
    print(quote)

    return render_template("index.html", quote=quote)


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
            data = getNextQuestion(slug.replace("/", ""), questionNumber)

            # Check if parameter is between the range of possible questions
            if 0 < questionNumber <= data["totalQuestions"]:
                return render_template(
                    "questions.html", data=data, questionNumber=questionNumber
                )
            else:
                raise ValueError("-Invalid number.")
        except (TypeError, ValueError) as err:
            return redirect(url_for("anxietyTest"))
    else:
        # Get first question, its answers and the num of total questions
        if request.args:
            return redirect(url_for("anxietyTest"))

        slug = request.path
        data = getNextQuestion(slug.replace("/", ""), 1)

        if data is None:
            abort(500)

        return render_template("quiz.html", data=data, questionNumber=1)


@app.route("/<string:test>/results", methods=["POST"])
def calculateResults(test):
    if request.method == "POST":
        if request.mimetype == "multipart/form-data":
            url = getTestResult(test, request.form)

            return make_response({"url": url}, 200)
        else:
            abort(400)


@app.route("/results/<int:id>/<string:hash>")
def results(id, hash):
    conn = connect_db()
    cursor = conn.cursor(cursor_factory=ext.DictCursor)
    cursor.execute(
        "SELECT test_id, test_result, hash, user_id, keyword FROM results WHERE id = %s",
        (id,),
    )
    result = cursor.fetchone()

    if result == None or result["hash"] != hash:
        cursor.close()
        conn.close()
        abort(404)
    elif result["user_id"] != None:
        try:
            userId = int(current_user.get_id())
        except (TypeError, ValueError) as err:
            cursor.close()
            conn.close()
            abort(401)

        if userId != result["user_id"]:
            abort(403)

        cursor.execute(
            """SELECT qc.name, r.result FROM questions_categories qc INNER JOIN category_results r ON qc.id = r.category_id WHERE r.result_id = %s""",
            (id,),
        )
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template(
            "results.html", result=result, categories=categories, extraData=True
        )
    return render_template("results.html", result=result, extraData=False)


# Handle errors
@app.errorhandler(400)
def badRequest(e):
    return render_template("error.html", error=400, message="Bad request."), 400


@app.errorhandler(401)
def unauthorized(e):
    return (
        render_template(
            "error.html",
            error=401,
            message="You are not authorized to access this page.",
        ),
        401,
    )


@app.errorhandler(403)
def forbidden(e):
    return (
        render_template(
            "error.html",
            error=403,
            message="You don't have permission to access this resource.",
        )
    ), 403


@app.errorhandler(404)
def pageNotFound(e):
    return (
        render_template(
            "error.html",
            error=404,
            message="Sorry, the page you were looking for doesn't exist!",
        ),
        404,
    )


@app.errorhandler(405)
def wrongMethod(e):
    return render_template("error.html", error=405, message="Method not allowed"), 405


@app.errorhandler(500)
def internalError(e):
    return (
        render_template("error.html", error=500, message="Internal Server Error"),
        500,
    )
