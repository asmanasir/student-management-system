"""The courses department: every page whose address starts with /courses.
Create, read, update and delete courses, and put students in and out of them.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import course_repo
import student_repo as repo
from .validation import validate_course

bp = Blueprint("courses", __name__)


def course_or_404(course_code):
    """The course, or stop with 404. Every route with <course_code> in the address starts with this."""
    course = course_repo.get_course(course_code.strip().upper())
    if course is None:
        abort(404)
    return course


# ---------- R: read ----------
@bp.route("/courses")
def course_list():
    """/courses: every course, with its seats."""
    return render_template("courses.html", courses=course_repo.get_courses())


@bp.route("/courses/<course_code>")
def course_detail(course_code):
    """/courses/DB101 (or /courses/db101): one course, its students, and who could still join."""
    course = course_or_404(course_code)
    students = course_repo.students_in_course(course["course_code"])
    candidates = course_repo.students_not_in_course(course["course_code"])
    return render_template("course.html", course=course, students=students, candidates=candidates)