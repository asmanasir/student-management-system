"""The web app for the Student Management System.
create_app() builds the app: it registers the blueprints (students and classes),
the home page, and the error pages. Start it from the project folder with
    python run.py      or      flask --app sms_web run --debug
"""
import os                                    # NEW: to read SECRET_KEY

import mysql.connector
from dotenv import load_dotenv               # NEW: reads the .env file
from flask import Flask, render_template

from . import classes, students

load_dotenv()                                # NEW: put the values from .env into os.environ


def create_app():
    app = Flask(__name__)

    # 0. NEW: the secret key from .env. flash() needs it to sign its messages.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # 1. The departments: each blueprint brings its own routes.
    app.register_blueprint(students.bp)      # every address that starts with /students
    app.register_blueprint(classes.bp)       # every address that starts with /classes

    # 2. The front page and the about page.
    @app.route("/")
    def home():
        return render_template("home.html")

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

    @app.errorhandler(mysql.connector.Error)
    def database_error(err):
        app.logger.error("database error %s", err.errno)
        return render_template("error.html", code=500,
                               message="Something went wrong with the database. Please try again later."), 500

    return app