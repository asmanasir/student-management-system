"""The data layer for courses and enrollments. All the SQL for the course pages lives here, like student_repo.py for students.
It uses the same connection helper as student_repo.py: one database, one way to talk to it.
"""
import mysql.connector
from mysql.connector import errorcode

from student_repo import transaction


class CourseExists(Exception):
    """Another course already has this code (MySQL 1062)."""


class CourseInUse(Exception):
    """The course still has students, so MySQL refuses to delete it (1451)."""


class CourseFull(Exception):
    """No free seats."""


class AlreadyEnrolled(Exception):
    """The student already takes the course (1062 on the primary key)."""


class NotFound(Exception):
    """No such course or student."""


# One SELECT for "a course with its number of students". LEFT JOIN: a course with no students still comes back, with taken = 0.
COURSE_WITH_TAKEN = """
    SELECT c.course_id, c.course_code, c.course_name, c.teacher, c.max_students,
           COUNT(e.student_id) AS taken
    FROM course c
    LEFT JOIN enrollment e ON e.course_id = c.course_id
"""


# ---------- Read ----------
def get_courses():
    """Every course, with taken = how many students take it."""
    with transaction() as cur:
        cur.execute(COURSE_WITH_TAKEN + " GROUP BY c.course_id ORDER BY c.course_code")
        return cur.fetchall()


def get_course(course_code):
    """One course with its number of students, or None."""
    with transaction() as cur:
        cur.execute(COURSE_WITH_TAKEN + " WHERE c.course_code = %s GROUP BY c.course_id", (course_code,))
        return cur.fetchone()


def students_in_course(course_code):
    """The students who take the course, with the date they started."""
    with transaction() as cur:
        cur.execute("""
            SELECT s.student_id, s.first_name, s.last_name, s.email, s.class_name, e.enrolled_on
            FROM enrollment e
            JOIN student s ON s.student_id = e.student_id
            JOIN course c ON c.course_id = e.course_id
            WHERE c.course_code = %s
            ORDER BY s.last_name, s.first_name""", (course_code,))
        return cur.fetchall()


def students_not_in_course(course_code):
    """The students who could still join: for the dropdown on the course page."""
    with transaction() as cur:
        cur.execute("""
            SELECT s.student_id, s.first_name, s.last_name
            FROM student s
            WHERE s.student_id NOT IN (
                SELECT e.student_id FROM enrollment e
                JOIN course c ON c.course_id = e.course_id
                WHERE c.course_code = %s)
            ORDER BY s.last_name, s.first_name""", (course_code,))
        return cur.fetchall()


def courses_for_student(student_id):
    """The courses one student takes: for the student page."""
    with transaction() as cur:
        cur.execute("""
            SELECT c.course_code, c.course_name, e.enrolled_on
            FROM enrollment e
            JOIN course c ON c.course_id = e.course_id
            WHERE e.student_id = %s
            ORDER BY c.course_code""", (student_id,))
        return cur.fetchall()


# ---------- Create, Update, Delete ----------
def add_course(course_code, course_name, teacher, max_students):
    """Save a new course and return its id. Raise CourseExists if the code is taken."""
    with transaction() as cur:
        try:
            cur.execute("INSERT INTO course (course_code, course_name, teacher, max_students) VALUES (%s, %s, %s, %s)",
                        (course_code, course_name, teacher, max_students))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:                  # 1062: the UNIQUE course_code
                raise CourseExists(f"{course_code} already exists") from err
            raise
        return cur.lastrowid


def update_course(course_code, course_name, teacher, max_students):
    """Change a course. The code is the key, so it does not change."""
    with transaction() as cur:
        cur.execute("UPDATE course SET course_name = %s, teacher = %s, max_students = %s WHERE course_code = %s",
                    (course_name, teacher, max_students, course_code))


def delete_course(course_code):
    """Delete a course. Raise CourseInUse if students still take it (the foreign key in enrollment)."""
    with transaction() as cur:
        try:
            cur.execute("DELETE FROM course WHERE course_code = %s", (course_code,))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ROW_IS_REFERENCED_2:         # 1451: a row in enrollment points to it
                raise CourseInUse(f"{course_code} still has students") from err
            raise


def enroll(student_id, course_code):
    """Put a student in a course, with today's date.
    Raise NotFound (no such student or course), CourseFull, or AlreadyEnrolled. Everything in ONE transaction.
    """
    with transaction() as cur:
        cur.execute("SELECT student_id FROM student WHERE student_id = %s", (student_id,))
        if cur.fetchone() is None:
            raise NotFound(f"There is no student {student_id}")
        # FOR UPDATE locks the course row until the transaction ends: two people can't take the last seat at once.
        cur.execute("SELECT course_id, max_students FROM course WHERE course_code = %s FOR UPDATE", (course_code,))
        course = cur.fetchone()
        if course is None:
            raise NotFound(f"There is no course {course_code}")
        cur.execute("SELECT COUNT(*) AS taken FROM enrollment WHERE course_id = %s", (course["course_id"],))
        if cur.fetchone()["taken"] >= course["max_students"]:
            raise CourseFull(f"{course_code} is full")
        try:
            cur.execute("INSERT INTO enrollment (student_id, course_id, enrolled_on) VALUES (%s, %s, CURDATE())",
                        (student_id, course["course_id"]))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:                  # the primary key (student_id, course_id)
                raise AlreadyEnrolled(f"Student {student_id} already takes {course_code}") from err
            raise


def unenroll(student_id, course_code):
    """Take a student out of a course. Return True if there was something to remove."""
    with transaction() as cur:
        cur.execute("""
            DELETE e FROM enrollment e
            JOIN course c ON c.course_id = e.course_id
            WHERE e.student_id = %s AND c.course_code = %s""", (student_id, course_code))
        return cur.rowcount > 0