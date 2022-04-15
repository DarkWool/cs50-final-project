from anxiety_app import app
from flask import redirect, url_for, render_template, request, flash
from flask_login import login_user, login_required, logout_user, LoginManager, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from anxiety_app.db import connect_db
from anxiety_app.forms import LoginForm, SignUpForm

# Login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
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
    conn.close()
    if userInfo is None:
        return None
    else:
        return User(userInfo["id"], userInfo["username"], userInfo["first_name"], userInfo["email"], userInfo["password"]) 

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.data["username"]
        password = form.data["password"]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        userData = cursor.fetchone()
        conn.close()

        if userData is None or not check_password_hash(userData["password"], password):
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))
        user = load_user(userData["id"])
        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("auth/login.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
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
            login_user(user)
            conn.close()
            return redirect("/dashboard")

        conn.close()
        flash("Email / username already registered")
        return redirect(url_for("signup"))
    return render_template("auth/signup.html", form=form)