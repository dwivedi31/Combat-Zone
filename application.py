from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50 import SQL
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import sqlite3
import os
import sys
from functools import wraps

app = Flask(__name__)
app.secret_key = 'combat'
db = SQL("sqlite:///CombatZone.db")

#creating table users to store user's information in database
db.execute("CREATE TABLE if not exists users(username primary key NOT NULL,first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT NOT NULL, hash TEXT NOT NULL)")


# ensure responses aren't cached
# if app.config["DEBUG"]:
#     @app.after_request
#     def after_request(response):
#         response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#         response.headers["Expires"] = 0
#         response.headers["Pragma"] = "no-cache"
#         return response

'''configuring app'''
#directory where sessions files will be stored
app.config["SESSION_FILE_DIR"] = gettempdir()
#no permanent session
app.config["SESSION_PERMANENT"] = False
#use filesystem interface
app.config["SESSION_TYPE"] = "filesystem"

#for adding support of server-side sessions
Session(app)

def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function



@app.route("/")
@login_required
def index():
    """ Home page """
    #fetching name of current user logged in
    first_name = db.execute("SELECT first_name from users WHERE username=:username", username=session["username"])[0]['first_name']
    last_name = db.execute("SELECT last_name from users WHERE username=:username", username=session["username"])[0]['last_name']

    return render_template("index.html", first_name=str(first_name), last_name=str(last_name))


@app.route("/login", methods=["GET", "POST"])
def login():

    """Log user in."""
    session.clear()
    # if user reached route via POST method
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            error = "Must provide username"
            return render_template("sorry.html", message=error)

        # ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            return render_template("sorry.html", message=error)

        # query database for username
        rows = db.execute("SELECT * FROM users \
                     WHERE username = :username", \
                     username=str(request.form.get("username")))

        # ensure username exists and password is correct
        if len(rows) != 1 or  not pwd_context.verify(str(request.form.get("password")), rows[0]["hash"]):
            error = "invalid username and/or password"
            return render_template("sorry.html", message=error)

        # remember which user has logged in

        session["username"] = str(request.form.get("username"))

        #fetch name of current user
        first_name = db.execute("SELECT first_name from users WHERE username=:username", username=session["username"])[0]['first_name']
        last_name = db.execute("SELECT last_name from users WHERE username=:username", username=session["username"])[0]['last_name']

        # redirect user to home page
        return render_template("index.html", first_name=first_name, last_name = last_name)

    # else if user reached route via GET request
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login page
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # if user reached route via POST method
    if request.method == "POST":

        #ensure name was submitted
        if not request.form.get("first_name"):
            error = "Must provide first_name"
            return render_template("sorry.html", message=error)
        elif not request.form.get("last_name"):
            error = "Must provide last_name"
            return render_template("sorry.html", message=error)
        # ensure username was submitted
        elif not request.form.get("username"):
            error = "Must provide username"
            return render_template("sorry.html", message=error)
        elif not request.form.get("email"):
            error = "Must provide email"
            return render_template("sorry.html", message=error)
        # ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            return render_template("sorry.html", message=error)

        # ensure password and verified password is the same
        elif request.form.get("password") != request.form.get("passwordagain"):
            error = "password doesn't match"
            return render_template("sorry.html", message=error)

        #fetching name from form page
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        #print name, request.form.get("username"), request.form.get("password")
        #print type(name), type(request.form.get("username")), type(request.form.get("password"))
        # insert the new user into users, storing the hash of the user's password
        result = db.execute("INSERT INTO users(username, first_name, last_name, email, hash) VALUES(:username, :first_name, :last_name, :email, :hash)", username=str(request.form.get("username")), first_name=str(first_name), last_name=str(last_name), email=str(request.form.get("email")), hash=pwd_context.hash(str(request.form.get("password"))))
        #check for username is unique or not
        if not result:
            error = "Username already exist"
            return render_template("sorry.html", message=error)
        # remember which user has logged in
        session["username"] = str(request.form.get("username"))
        # redirect user to home page
        return redirect(url_for("login"))

    # else if user reached route via GET request
    else:
        return render_template("register.html")
@app.route("/prob")
def prob():
    return render_template("prob.html")

if __name__ == '__main__':
    app.run(debug=True)
