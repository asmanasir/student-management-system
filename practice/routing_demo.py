"""Routing practice with our six students. No database yet: the students are a Python list.
Run it: python practice/routing_demo.py
Then try the addresses in the comments above each route.
"""
from flask import Flask, abort, request, url_for
from markupsafe import escape

app = Flask(__name__)

STUDENTS = [
    {"student_id": 1, "first_name": "Amir", "last_name": "Hassan", "email": "amir@school.no", "class_name": "2A"},
    {"student_id": 2, "first_name": "Emma", "last_name": "Berg", "email": "emma@school.no", "class_name": "2A"},
    {"student_id": 3, "first_name": "Jonas", "last_name": "Lie", "email": "jonas@school.no", "class_name": "2B"},
    {"student_id": 4, "first_name": "Sara", "last_name": "Khan", "email": "sara@school.no", "class_name": "2B"},
    {"student_id": 5, "first_name": "Nora", "last_name": "Haugen", "email": "nora@school.no", "class_name": "2A"},
    {"student_id": 6, "first_name": "Ali", "last_name": "Dahl", "email": "ali@school.no", "class_name": "2B"},
]


# 1. A fixed address.   http://127.0.0.1:5000/
@app.route("/")
def home():
    return "<h1>Student Management System</h1><p>See the <a href='/students'>students</a>.</p>"


# 2. A fixed address that returns data. A list or a dict becomes JSON.
#    http://127.0.0.1:5000/students
#    http://127.0.0.1:5000/students?class=2B
@app.route("/students")
def student_list():
    class_name = request.args.get("class")          # None if it isn't in the address
    students = STUDENTS
    if class_name:
        students = [s for s in students if s["class_name"] == class_name]
    return students


# 3. An address with a variable part. <int:...> only accepts whole numbers.
#    http://127.0.0.1:5000/students/1     -> Amir
#    http://127.0.0.1:5000/students/99    -> 404, we said so
#    http://127.0.0.1:5000/students/amir  -> 404, Flask said so (not a number)
@app.route("/students/<int:student_id>")
def student_detail(student_id):
    for s in STUDENTS:
        if s["student_id"] == student_id:
            return s
    abort(404)


# 4. A variable part that is text.   http://127.0.0.1:5000/hello/Sara
#    escape() makes sure that what the user typed is shown as text, never run as HTML.
@app.route("/hello/<name>")
def hello(name):
    return f"Hello, {escape(name)}! Welcome to the Student Management System."


# 5. You choose the status code yourself.   http://127.0.0.1:5000/maintenance
@app.route("/maintenance")
def maintenance():
    return "Sorry, the system is closed for maintenance.", 503


# 6. url_for(): ask for an address by the function's name.   http://127.0.0.1:5000/links
@app.route("/links")
def links():
    return {
        "home": url_for("home"),
        "amir": url_for("student_detail", student_id=1),
        "class 2B": url_for("student_list", **{"class": "2B"}),
    }


if __name__ == "__main__":
    app.run(debug=True)