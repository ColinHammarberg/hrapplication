import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
@app.route("/hrapplication")
def hrapplication():
    application = list(mongo.db.application.find())
    return render_template("hrapplication.html", application=application)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # This check if the user already exists in the databse
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})          
        if existing_user:
            flash("Username already exists. Please choose another username.")
            return redirect(url_for("register"))

        existing_email = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_email:
            flash("Email already exists. Please choose another email address.")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("hrapplication", username=session["user"]))

    return render_template("register.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))                            
                        return redirect(url_for(
                            "hrapplication", username=session["user"]))

            else:
                # The choosen password does not exist (function)
                flash("Incorrect Username and/or Password")
                return redirect(url_for("signin"))

        else:
            # The choosen username does not exist (function)
            flash("Incorrect Username and/or Password")
            return redirect(url_for("signin"))

    return render_template("signin.html")

@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("signin"))


@app.route("/add_feedback", methods=["GET", "POST"])
def add_feedback():
    if request.method == "POST":
        digital_meeting = "yes" if request.form.get(
            "digital_meeting") else "no"
        feedback = {
            "feedback_type": request.form.get("feedback_type"),
            "feedback_description": request.form.get("feedback_description"),
            "feedback_reflection": request.form.get("feedback_reflection"),
            
        }
        mongo.db.feedback.insert_one(feedback)
        flash("Your requested therapy session has been registered")
        return redirect(url_for("hrapplication"))

    return render_template("feedback.html")

# The application will find the username from the mongo database


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    user = mongo.db.users.find_one(
        {"username": session["user"]})

    if 'user' in session:
        return render_template(
            "profile.html", username=user['username'], user=user)

    return redirect(url_for("signin"))

# Lets the user/client to contact


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        emails = {
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "message": request.form.get("message"),
        }
        mongo.db.emails.insert_one(emails)
        flash("Your email was successfully sent")
        return redirect(url_for("hrapplication"))

    return render_template("contact.html")

# Documentation page (Client Diary)


@app.route("/add_documentation", methods=["GET", "POST"])
def add_documentation():
    if request.method == "POST":
        therapist_read = "Yes" if request.form.get("therapist_read") else "No"
        diary = {
            "diary_date": request.form.get("diary_date"),
            "diary_type": request.form.get("diary_type"),
            "diary_description": request.form.get("diary_description"),
            "diary_reflection": request.form.get("diary_reflection"),
            "therapist_note": request.form.get("therapist_note"),
            "therapist_read": therapist_read,
            "made_by": session["user"]
        }
        mongo.db.diary.insert_one(diary)
        flash("Your diary has been updated")
        return redirect(url_for("love_therapy"))

    return render_template("add_documentation.html")



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)