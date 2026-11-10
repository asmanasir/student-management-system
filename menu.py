"""app.py: no SQL here any more. It only asks student_repo.py for the data, and prints it."""
from student_repo import get_all_students

students = get_all_students()
for student in students:
    print(student["first_name"], student["last_name"], student["email"])