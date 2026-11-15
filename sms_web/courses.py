"""The courses department: every page whose address starts with /courses.
C, R, U and D for courses, and putting students in and out of them (enrollment).
Same pattern as students.py: find it or 404 → check → change → catch → flash → redirect.
"""
import re

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import course_repo
import student_repo as repo

bp = Blueprint("courses", __name__)

COURSE_CODE_PATTERN = r"[A-Z]{2,4}\d{3}"           # 2–4 letters and 3 digits: DB101, PRG101


def validate_course(form):
    """The rules for a course, used by Add AND Edit. Returns (data, errors): errors is {} when all is OK."""
    data = {
        "course_code": form.get("course_code", "").strip().upper(),
        "course_name": form.get("course_name", "").strip(),
        "teacher": form.get("teacher", "").strip(),
        "max_students": form.get("max_students", "").strip(),
    }
    errors = {}
    if not re.fullmatch(COURSE_CODE_PATTERN, data["course_code"]):
        errors["course_code"] = "The code is 2–4 letters and 3 digits, like DB101."
    for field, label, limit in [("course_name", "Course name", 100), ("teacher", "Teacher", 50)]:
        if not data[field]:
            errors[field] = f"{label} is required."
        elif len(data[field]) > limit:
            errors[field] = f"{label} can be at most {limit} characters."
    try:
        data["max_students"] = int(data["max_students"])          # "25" -> 25, "" or "many" -> ValueError
        if not 1 <= data["max_students"] <= 200:
            errors["max_students"] = "Max students must be between 1 and 200."
    except ValueError:
        errors["max_students"] = "Max students must be a whole number."
    return data, errors


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


# ---------- C: create ----------
@bp.route("/courses/new", methods=["GET", "POST"])
def course_new():
    """GET: an empty form. POST: check, save, and go to the new course."""
    form, errors = {}, {}
    if request.method == "POST":
        form, errors = validate_course(request.form)
        if not errors:
            try:
                course_repo.add_course(form["course_code"], form["course_name"], form["teacher"], form["max_students"])
            except course_repo.CourseExists:
                errors["course_code"] = f"{form['course_code']} already exists."
            else:
                flash(f"{form['course_code']} {form['course_name']} was added.", "success")
                return redirect(url_for("courses.course_detail", course_code=form["course_code"]))
    return render_template("course_form.html", form=form, errors=errors, editing=False,
                           heading="Add a course", action=url_for("courses.course_new")), (400 if errors else 200)


# ---------- U: update ----------
@bp.route("/courses/<course_code>/edit", methods=["GET", "POST"])
def course_edit(course_code):
    """GET: the form, filled in. POST: check (also against the students who take it), save, go back."""
    course = course_or_404(course_code)
    code = course["course_code"]
    form, errors = course, {}
    if request.method == "POST":
        data = request.form.to_dict()
        data["course_code"] = code                       # the code comes from the address, never from the form
        form, errors = validate_course(data)
        if "max_students" not in errors and form["max_students"] < course["taken"]:
            errors["max_students"] = f"{course['taken']} students already take {code}: the number can't be lower."
        if not errors:
            course_repo.update_course(code, form["course_name"], form["teacher"], form["max_students"])
            flash(f"{code} {form['course_name']} was saved.", "success")
            return redirect(url_for("courses.course_detail", course_code=code))
    return render_template("course_form.html", form=form, errors=errors, editing=True,
                           heading=f"Edit {code}",
                           action=url_for("courses.course_edit", course_code=code)), (400 if errors else 200)


# ---------- D: delete ----------
@bp.route("/courses/<course_code>/delete", methods=["GET", "POST"])
def course_delete(course_code):
    """GET: ask "Are you sure?" (asking changes nothing). POST: delete, or explain why the database said no."""
    course = course_or_404(course_code)
    code = course["course_code"]
    if request.method == "POST":
        try:
            course_repo.delete_course(code)
        except course_repo.CourseInUse:
            flash(f"{code} still has students. Remove them first.", "error")
            return redirect(url_for("courses.course_detail", course_code=code))
        flash(f"{code} {course['course_name']} was deleted.", "success")
        return redirect(url_for("courses.course_list"))
    return render_template("course_delete.html", course=course)


# ---------- the link between students and courses ----------
@bp.route("/courses/<course_code>/enroll", methods=["POST"])
def course_enroll(course_code):
    """POST only: put the student chosen in the dropdown in the course."""
    code = course_or_404(course_code)["course_code"]
    try:
        student_id = int(request.form.get("student_id", ""))     # form data is text: "3" -> 3
    except ValueError:
        flash("Please choose a student.", "error")
        return redirect(url_for("courses.course_detail", course_code=code))
    try:
        course_repo.enroll(student_id, code)
    except course_repo.NotFound:
        abort(404)
    except course_repo.CourseFull:
        flash(f"{code} is full.", "error")
    except course_repo.AlreadyEnrolled:
        flash(f"The student already takes {code}.", "error")
    else:
        student = repo.get_student(student_id)
        flash(f"{student['first_name']} {student['last_name']} is now in {code}.", "success")
    return redirect(url_for("courses.course_detail", course_code=code))


@bp.route("/courses/<course_code>/students/<int:student_id>/remove", methods=["POST"])
def course_remove(course_code, student_id):
    """POST only: take one student out of the course."""
    code = course_or_404(course_code)["course_code"]
    student = repo.get_student(student_id)
    if student is None or not course_repo.unenroll(student_id, code):
        abort(404)
    flash(f"{student['first_name']} {student['last_name']} was removed from {code}.", "success")
    return redirect(url_for("courses.course_detail", course_code=code))
