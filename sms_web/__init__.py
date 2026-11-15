"""The web app for the Student Management System.
create_app() builds the app: it registers the blueprints (students, classes and courses),
the home page, and the error pages. Start it from the project folder with
    python run.py      or      flask --app sms_web run --debug
"""
import os                                    # to read SECRET_KEY

import mysql.connector
from dotenv import load_dotenv               # reads the .env file
from flask import Flask, render_template

import course_repo                           # Lecture 5: the courses
import student_repo as repo
from . import classes, courses, students


load_dotenv()                                # put the values from .env into os.environ


def create_app():
    app = Flask(__name__)

    # 0. The secret key from .env. flash() needs it to sign its messages.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # 1. The departments: each blueprint brings its own routes.
    app.register_blueprint(students.bp)      # every address that starts with /students
    app.register_blueprint(classes.bp)       # every address that starts with /classes
    app.register_blueprint(courses.bp)       # every address that starts with /courses

    # 2. The front page (a dashboard with numbers) and the about page.
    @app.route("/")
    def home():
        courses_ = course_repo.get_courses()
        return render_template("home.html",
                               students=repo.get_all_students(),
                               classes=repo.class_overview(),
                               courses=courses_,
                               full_courses=[c for c in courses_ if c["taken"] >= c["max_students"]])

    @app.route("/about")
    def about():
        return render_template("about.html")

    # 3. Error pages: one calm sentence for the user.
    @app.errorhandler(404)
    def not_found(err):
        return render_template("error.html", code=404, message="We couldn't find that page."), 404

    @app.errorhandler(400)
    def bad_request(err):
        return render_template("error.html", code=400, message=err.description), 400

    @app.errorhandler(405)                   # e.g. /students/2/delete typed in the address bar
    def method_not_allowed(err):
        return render_template("error.html", code=405,
                               message="This page only works with a button, not by typing the address."), 405

    @app.errorhandler(mysql.connector.Error)
    def database_error(err):
        app.logger.error("database error %s", err.errno)
        return render_template("error.html", code=500,
                               message="Something went wrong with the database. Please try again later."), 500

    return app
