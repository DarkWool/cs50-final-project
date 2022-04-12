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
    cursor.execute("SELECT t.name, r.hash, r.id, r.date, r.test_result, t.max_score FROM tests t INNER JOIN results r ON t.id=r.test_id WHERE r.user_id = ?", (userId,))
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
        except:
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
    cursor.execute("SELECT test_result, hash, user_id FROM results WHERE id = ?", (id,))
    result = cursor.fetchone()

    # Check if the test result is private (for logged users)
    if result["user_id"] is not None:
        try:
            userId = int(flask_login.current_user.get_id())
            if userId != result["user_id"]:
                return redirect(url_for("info"))
        except:
            return redirect(url_for("info"))

    # Users can get curious and experiment with urls, thats why you have to compare if the hash 
    #  of the result with the id they specified is the same as the hash on the URL
    # If this had not been implemented then users would be able to look for other person results easily.
    if result != None and result["hash"] == hash:
        print("SUCCESS, TEST FOUND!")
        if result["test_result"] <= 10:
            return "Your score is low"
        elif result["test_result"] <= 25:
            return "Mild anxiety"
        elif result["test_result"] <= 35:
            return "High anxiety"
        else:
            return "Extreme anxiety, please seek help when possible"
    else:
        print("Test was not found or the hash did not match")
        return redirect(url_for("info"))


def getTestResult(slug, formData):
    # Fetch general information about the test
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, total_questions, same_answers FROM tests WHERE slug = ?", (slug,))
    testGeneralInfo = cursor.fetchone()
    testTotalQuestions = testGeneralInfo["total_questions"]

    # Check if the answers are the same for all the questions
    if testGeneralInfo["same_answers"] == True:
        cursor.execute("SELECT value FROM answers WHERE test_id = ?", (testGeneralInfo["id"],))
        testData = cursor.fetchall()
        answers = []

        for row in testData:
            answers.append(row["value"])

        testTotalQuestions += 1
        userResult = 0

        # Iterate by the total number of questions (not by the length of the form sent by the user)
        # and get all the values of the form with the prefix of
        # 'question' followed by the curr value of 'index' and sum them.
        for index in range(1, testTotalQuestions):
            try:
                answerValue = int(formData.get(f"question{index}"))
            except:
                continue

            if answerValue in answers:
                userResult += answerValue

        # Generate a new UUID to associate with the id of the new test result
        uuid = shortuuid.uuid()

        if flask_login.current_user.is_authenticated:
            cursor.execute('''INSERT INTO results (test_id, test_result, hash, user_id) VALUES(?, ?, ?, ?)''',
            (testGeneralInfo["id"], userResult, uuid, flask_login.current_user.id))
        else:
            # Insert the results into the db and retrieve the id of the row inserted
            cursor.execute('''INSERT INTO results (test_id, test_result, hash) VALUES(?, ?, ?)''',
            (testGeneralInfo["id"], userResult, uuid))

        conn.commit()
        userResultId = cursor.lastrowid

    conn.close()

    return f"results/{userResultId}/{uuid}"


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