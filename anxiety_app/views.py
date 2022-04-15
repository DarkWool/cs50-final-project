import os
import sqlite3
import shortuuid
import flask_login
from anxiety_app import app
from dotenv import load_dotenv
from flask import render_template, request, redirect, url_for, make_response, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators

load_dotenv()

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

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


# Login stuff
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(flask_login.UserMixin):
    def __init__(self, id, username, firstName, email, password):
        self.id = id
        self.username = username
        self.firstName = firstName
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    userInfo = cursor.fetchone()
    if userInfo is None:
        return None
    else:
        return User(userInfo["id"], userInfo["username"], userInfo["first_name"], userInfo["email"], userInfo["password"]) 


class SignUpForm(FlaskForm):
    username = StringField("Username", [
        validators.InputRequired(), 
        validators.Length(min=4, max=20, message="Username must be at least 4 characters long and max 20")
    ])

    firstName = StringField("First Name", [
        validators.InputRequired(),
        validators.Length(min=2, max=20),
    ])

    email = StringField("Email", [
        validators.InputRequired(), 
        validators.Email()
    ])

    password = PasswordField("Password", [
        validators.InputRequired(),
        validators.Regexp("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).{8,24}$", 0,
            '''Password must contain at least one lowercase and one capital letter, a number and it must be 
            between 8 and 24 characters long'''),
        validators.EqualTo("confirmPassword", message="Passwords doesn't match")
    ])

    confirmPassword = PasswordField("Repeat Password", [
        validators.InputRequired(),
    ])

class LoginForm(FlaskForm):
    username = StringField("Username", [
        validators.InputRequired()
    ])
    password = PasswordField("Password", [
        validators.InputRequired(),
    ])

class changePasswordForm(FlaskForm):
    password = PasswordField("Current password", [
        validators.InputRequired(),
        validators.DataRequired()
    ])

    newPassword = PasswordField("New password", [
        validators.InputRequired(),
        validators.DataRequired(),
        validators.Regexp("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).{8,24}$", 0,
            '''Password must contain at least one lowercase and one capital letter, a number and it must be 
            between 8 and 24 characters long'''),
        validators.EqualTo("confirmPassword", message="Passwords doesn't match")
    ])

    confirmPassword = PasswordField("Confirm password", [
        validators.InputRequired(),
        validators.DataRequired()
    ])


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.data["username"]
        password = form.data["password"]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        userData = cursor.fetchone()

        if userData is None or not check_password_hash(userData["password"], password):
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))
        user = load_user(userData["id"])
        flask_login.login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("auth/login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = SignUpForm()
    if request.method == "POST" and form.validate_on_submit():
        # Get data from the form
        username = form.data["username"]
        firstName = form.data["firstName"]
        email = form.data["email"]
        password = generate_password_hash(form.data["password"], method="pbkdf2:sha256")

        # Search if username or email specified do not exist on the Database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?", (username, email))
        duplicateUser = cursor.fetchone()

        # It duplicateUser is None means that the username or email have not been taken yet
        if duplicateUser is None:       
            cursor.execute("INSERT INTO users (username, first_name, email, password) VALUES (?, ?, ?, ?)",
                (username, firstName, email, password))
            conn.commit()
            id = cursor.lastrowid

            # Create a new user object
            user = User(id, username, firstName, email, password)

            # Pass the User object to the login_user function
            flask_login.login_user(user)
            conn.close()
            return redirect("/dashboard")

        conn.close()
        flash("Email / username already registered")
        return redirect(url_for("signup"))
    return render_template("auth/signup.html", form=form)


@app.route("/dashboard")
@flask_login.login_required
def dashboard():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date_created FROM users WHERE id = ?", (flask_login.current_user.id,))
    date = cursor.fetchone()["date_created"]
    conn.close()

    return render_template("users/dashboard.html", date=date)


@app.route("/my-results")
@flask_login.login_required
def myresults():
    userId = flask_login.current_user.id
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT t.name, r.hash, r.id, r.date, r.test_result FROM tests t INNER JOIN results r ON t.id=r.test_id WHERE r.user_id = ?", (userId,))
    userTests =  cursor.fetchall()
    
    conn.close()

    return render_template("users/my-results.html", userTests=userTests)


@app.route("/change-password", methods=["GET", "POST"])
@flask_login.login_required
def changePassword():
    form = changePasswordForm()

    if request.method == "POST" and form.validate_on_submit():
        password = form.data["password"]
        newPassword = form.data["newPassword"]

        try:
            userId = int(flask_login.current_user.get_id())
        except Exception as err:
            return redirect(url_for("login"))

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id = ?", (userId,))
        userPassword = cursor.fetchone()["password"]

        if not check_password_hash(userPassword, password):
            flash("Incorrect password")
            return redirect(url_for("changePassword"))

        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (generate_password_hash(newPassword), userId))
        conn.commit()
        conn.close()
        flash("Your password has been changed", "success")
        return redirect(url_for("changePassword"))

    return render_template("users/change-password.html", form=form)


@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))


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


@app.route("/<string:test>/results", methods=["POST"])
def calculateResults(test):
    if request.method == "POST":
        if request.mimetype == "multipart/form-data":
            url = getTestResult(test, request.form)

            return make_response({"url": url}, 200)


@app.route("/results/<int:id>/<string:hash>")
def results(id, hash):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT test_id, test_result, hash, user_id FROM results WHERE id = ?", (id,))
    result = cursor.fetchone()

    if result == None or result["hash"] != hash:
        return redirect(url_for("info"))
    elif result["user_id"] != None:
        try:
            userId = int(flask_login.current_user.get_id())
            cursor.execute('''SELECT qc.name, r.result FROM questions_categories qc INNER JOIN category_results r ON qc.id = r.category_id WHERE r.result_id = ?''', (id,))
            categories = cursor.fetchall()
            conn.close()

            if userId != result["user_id"]:
                return redirect(url_for("info"))

            return (render_template("results.html", categories=categories, extraData=True))
        except Exception as err:
            print(err)
            conn.close()
            return redirect(url_for("info"))

    # if flask_login.current_user.is_authenticated:

    conn.close()
    return (render_template("results.html", extraData=False))


def getTestResult(slug, formData):
    # Fetch general info about the test
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, total_questions FROM tests WHERE slug = ?", (slug,))
    testInfo = cursor.fetchone()

    # Get categories of the test
    cursor.execute("SELECT category_id FROM questions WHERE test_id = ?", (testInfo["id"],))
    categoriesList = cursor.fetchall();

    # Get values from answers table
    cursor.execute("SELECT value FROM answers WHERE test_id = ?", (testInfo["id"],))
    testData = cursor.fetchall()

    answerValues = []
    categoriesResults = {}
    totalQuestions = len(categoriesList) + 1
    userResult = 0

    for row in testData:
        answerValues.append(row["value"])

    maxValue = max(answerValues)

    for row in categoriesList:
        if row["category_id"] in categoriesResults:
            categoriesResults[row["category_id"]]["total"] += maxValue
        else:
            categoriesResults[row["category_id"]] = {
                "id": row["category_id"],
                "total": maxValue,
                "userResult": 0
            }

    for index in range(1, totalQuestions):
        try:
            userAnswer = int(formData.get(f"question{index}"))
        except (TypeError, ValueError) as err:
            continue

        if userAnswer in answerValues:
            categoryId = categoriesList[index - 1]["category_id"]
            categoriesResults[categoryId]["userResult"] += userAnswer
            userResult += userAnswer

    # Generate a new UUID to associate with the id of the new test result
    uuid = shortuuid.uuid()

    if flask_login.current_user.is_authenticated:
        cursor.execute('''INSERT INTO results (test_id, test_result, hash, user_id) VALUES(?, ?, ?, ?)''',
        (testInfo["id"], userResult, uuid, flask_login.current_user.id))

        userResultId = cursor.lastrowid

        finalResults = []
        for category in categoriesResults:
            result = getPercentage(categoriesResults[category]["userResult"], categoriesResults[category]["total"])
            finalResults.append((userResultId, categoriesResults[category]["id"], result))

        cursor.executemany("INSERT INTO category_results VALUES (?, ?, ?)", (finalResults))
    else:
        # Insert the results into the db and retrieve the id of the row inserted
        cursor.execute('''INSERT INTO results (test_id, test_result, hash) VALUES(?, ?, ?)''',
        (testInfo["id"], userResult, uuid))
        userResultId = cursor.lastrowid

    conn.commit()
    conn.close()

    return f"results/{userResultId}/{uuid}"


def getPercentage(num, total):
    return num / total * 100;


def getTestData(slug, questionNumber):
    # First fetch general information about the test
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT t.id, COUNT(q.test_id) AS total_questions FROM tests t
    INNER JOIN questions q ON t.id = q.test_id WHERE t.slug = ?''', (slug,))
    testInfo = cursor.fetchone()

    # Get x question with answers of the current test  
    cursor.execute('''SELECT q.question, a.answer, a.value FROM questions q INNER JOIN answers a 
    ON q.test_id=a.test_id WHERE q.question_number = ? AND q.test_id = ?''', (questionNumber, testInfo["id"]))
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