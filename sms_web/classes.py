"""The classes department: every page whose address starts with /classes."""
from flask import Blueprint, abort, render_template

import student_repo as repo

bp = Blueprint("classes", __name__)


@bp.route("/classes")
def class_list():
    """/classes: every class, with its number of students."""
    classes = repo.class_overview()              # SQL counts the students (GROUP BY)
    return render_template("classes.html", classes=classes)


@bp.route("/classes/<class_name>")
def class_detail(class_name):
    """/classes/2B (or /classes/2b): the students in one class."""
    class_name = class_name.upper()
    students = repo.students_in_class(class_name)
    if not students:
        abort(404)                               # no such class
    return render_template("class.html", class_name=class_name, students=students)