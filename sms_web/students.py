"""The students department: every page whose address starts with /students.
C, R, U and D for students: new, list + detail, edit, delete.
"""
import re

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import student_repo as repo

bp = Blueprint("students", __name__)

EMAIL_PATTERN = r"[^@\s]+@[^@\s]+\.[a-z]{2,}"         # something@something.no
CLASS_PATTERN = r"\d[A-Z]"                           # 2A, 2B


def validate_student(form):
    """The rules for a student, used by Add AND Edit. Returns (data, errors): errors is {} when all is OK."""
    data = {
        "first_name": form.get("first_name", "").strip(),
        "last_name": form.get("last_name", "").strip(),
        "email": form.get("email", "").strip().lower(),
        "class_name": form.get("class_name", "").strip().upper(),
    }
    errors = {}
    for field, label in [("first_name", "First name"), ("last_name", "Last name")]:
        if not data[field]:
            errors[field] = f"{label} is required."
        elif len(data[field]) > 50:
            errors[field] = f"{label} can be at most 50 characters."
    if not re.fullmatch(EMAIL_PATTERN, data["email"]):
        errors["email"] = "Write an email like emma@school.no."
    if not re.fullmatch(CLASS_PATTERN, data["class_name"]):
        errors["class_name"] = "Choose a class, like 2A."
    return data, errors


# ---------- R: read ----------
@bp.route("/students")
def student_list():
    """/students: every student, or /students?q=ha: only the students whose name contains "ha"."""
    q = request.args.get("q", "").strip()
    if q:
        if len(q) < 2:
            abort(400, description="Please search for at least 2 letters.")
        students = repo.search_students(q)
    else:
        students = repo.get_all_students()
    return render_template("students.html", students=students, q=q)   # q: the search box keeps the word


@bp.route("/students/<int:student_id>")
def student_detail(student_id):
    """/students/1: one student."""
    student = repo.get_student(student_id)
    if student is None:
        abort(404)
    return render_template("student.html", student=student)


# ---------- C: create ----------
@bp.route("/students/new", methods=["GET", "POST"])
def student_new():
    """GET: an empty form. POST: check, save, and go to the new student."""
    form, errors = {}, {}
    if request.method == "POST":                      # the form was sent
        print("The browser sent:", request.form)      # look in the Run window!
        form, errors = validate_student(request.form)
        if not errors:
            try:
                new_id = repo.add_student(form["first_name"], form["last_name"], form["email"], form["class_name"])
            except repo.EmailTaken:
                errors["email"] = f"{form['email']} is already used by another student."
            else:
                flash(f"{form['first_name']} {form['last_name']} was added.", "success")
                return redirect(url_for("students.student_detail", student_id=new_id))
    return render_template("student_form.html", form=form, errors=errors,
                           heading="Add a student", action=url_for("students.student_new")), (400 if errors else 200)


# ---------- U: update ----------
@bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def student_edit(student_id):
    """GET shows the form, filled in. POST checks, saves, and goes back to the student."""
    student = repo.get_student(student_id)                 # 1. find it ...
    if student is None:
        abort(404)                                         #    ... or 404
    form, errors = student, {}                             # GET: the form shows what is in the database
    if request.method == "POST":
        form, errors = validate_student(request.form)      # 2. check (the same rules as Add)
        if not errors:
            try:
                # 3. change. student_id comes from the ADDRESS, never from the form
                repo.update_student(student_id, form["first_name"], form["last_name"],
                                    form["email"], form["class_name"])
            except repo.EmailTaken:                        # 4. catch
                errors["email"] = f"{form['email']} is already used by another student."
            else:
                flash(f"{form['first_name']} {form['last_name']} was saved.", "success")    # 5. flash
                return redirect(url_for("students.student_detail", student_id=student_id))  # 6. redirect
    return render_template("student_form.html", form=form, errors=errors,
                           heading=f"Edit {student['first_name']} {student['last_name']}",
                           action=url_for("students.student_edit", student_id=student_id)), (400 if errors else 200)


# ---------- D: delete ----------
@bp.route("/students/<int:student_id>/delete", methods=["POST"])
def student_delete(student_id):
    """POST only. Delete the student. Their enrollments go too (ON DELETE CASCADE)."""
    student = repo.get_student(student_id)                 # find it first: we need the name for the message
    if student is None or not repo.delete_student(student_id):
        abort(404)
    flash(f"{student['first_name']} {student['last_name']} was deleted.", "success")
    return redirect(url_for("students.student_list"))      # the student page is gone, so go to the list