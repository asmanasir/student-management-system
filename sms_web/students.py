"""The students department: every page whose address starts with /students."""
from flask import Blueprint, abort, render_template, request

import student_repo as repo

bp = Blueprint("students", __name__)


@bp.route("/students")
def student_list():
    """/students: every student. (Worked example: read it, then run it.)"""
    students = repo.get_all_students()
    return render_template("students.html", students=students)
    # TODO Task 5 (⭐⭐⭐): read q from request.args. If q has text, use repo.search_students(q).
    # If q is shorter than 2 letters: abort(400, description="Please search for at least 2 letters.")
    # Send q to the template too, so the search box keeps the word.


@bp.route("/students/<int:student_id>")
def student_detail(student_id):
    """/students/1: one student."""
    # TODO Task 3 (⭐⭐): student = repo.get_student(student_id). If it is None: abort(404).
    # Otherwise: return render_template("student.html", student=student)
    return f"TODO Task 3: show student {student_id}"
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for   # + flash, redirect, url_for

@bp.route("/students/new", methods=["GET", "POST"])
def student_new():
    if request.method == "POST":                      # the form was sent
        print("The browser sent:", request.form)      # look in the Run window!
        new_id = repo.add_student(
            request.form.get("first_name", ""),
            request.form.get("last_name", ""),
            request.form.get("email", ""),
            request.form.get("class_name", ""),
        )
        flash("The student was added.", "success")
        return redirect(url_for("students.student_detail", student_id=new_id))
    return render_template("student_form.html")       # GET: show the empty form