"""The data layer for courses and enrollments. All the SQL for the course pages lives here, like student_repo.py for students.

Every function follows the same five steps as student_repo.py:
1. connect   2. make a cursor that gives rows as dicts   3. run the SQL
4. give the result back (and commit if we changed something)   5. always close
"""
import mysql.connector
from mysql.connector import errorcode

from db import get_connection


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


# ------------------------------------------------------------------ reading

def get_courses():
    """Every course, with taken = how many students take it."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(COURSE_WITH_TAKEN + " GROUP BY c.course_id ORDER BY c.course_code")
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def get_course(course_code):
    """One course with its number of students, or None."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(COURSE_WITH_TAKEN + " WHERE c.course_code = %s GROUP BY c.course_id", (course_code,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def students_in_course(course_code):
    """The students who take the course, with the date they started."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.student_id, s.first_name, s.last_name, s.email, s.class_name, e.enrolled_on
            FROM enrollment e
            JOIN student s ON s.student_id = e.student_id
            JOIN course c ON c.course_id = e.course_id
            WHERE c.course_code = %s
            ORDER BY s.last_name, s.first_name
        """, (course_code,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def students_not_in_course(course_code):
    """The students who could still join: for the dropdown on the course page."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.student_id, s.first_name, s.last_name
            FROM student s
            WHERE s.student_id NOT IN (
                SELECT e.student_id FROM enrollment e
                JOIN course c ON c.course_id = e.course_id
                WHERE c.course_code = %s)
            ORDER BY s.last_name, s.first_name
        """, (course_code,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def courses_for_student(student_id):
    """The courses one student takes: for the student page."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.course_code, c.course_name, e.enrolled_on
            FROM enrollment e
            JOIN course c ON c.course_id = e.course_id
            WHERE e.student_id = %s
            ORDER BY c.course_code
        """, (student_id,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def courses_not_for_student(student_id):
    """NEW: the courses a student does NOT take yet, with their seats: for the dropdown on the Edit page."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(COURSE_WITH_TAKEN + """
            WHERE c.course_id NOT IN (SELECT course_id FROM enrollment WHERE student_id = %s)
            GROUP BY c.course_id
            ORDER BY c.course_code
        """, (student_id,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def courses_by_student():
    """NEW: which courses each student takes, for the student list: {1: ['DB101', 'WEB101'], 2: [...], ...}"""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.student_id, c.course_code
            FROM enrollment e
            JOIN course c ON c.course_id = e.course_id
            ORDER BY c.course_code
        """)
        result = {}
        for row in cursor.fetchall():
            result.setdefault(row["student_id"], []).append(row["course_code"])   # a new list the first time
        return result
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# ------------------------------------------------------------------ changing

def add_course(course_code, course_name, teacher, max_students):
    """C: save a new course and return its id. Raises CourseExists if the code is taken."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO course (course_code, course_name, teacher, max_students)
            VALUES (%s, %s, %s, %s)
        """, (course_code, course_name, teacher, max_students))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:                  # 1062: the UNIQUE course_code
            raise CourseExists(f"{course_code} already exists") from err
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def update_course(course_code, course_name, teacher, max_students):
    """U: change a course. The code is the key, so it does not change."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE course SET course_name = %s, teacher = %s, max_students = %s
            WHERE course_code = %s
        """, (course_name, teacher, max_students, course_code))
        conn.commit()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def delete_course(course_code):
    """D: delete a course. Raises CourseInUse if students still take it (the foreign key in enrollment)."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM course WHERE course_code = %s", (course_code,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == errorcode.ER_ROW_IS_REFERENCED_2:         # 1451: a row in enrollment points to it
            raise CourseInUse(f"{course_code} still has students") from err
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def enroll(student_id, course_code):
    """C on enrollment: put a student in a course, with today's date.
    Raises NotFound (no such student or course), CourseFull, or AlreadyEnrolled.
    Everything happens on ONE connection, and only the commit at the end saves it.
    """
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT student_id FROM student WHERE student_id = %s", (student_id,))
        if cursor.fetchone() is None:
            raise NotFound(f"There is no student {student_id}")
        # FOR UPDATE locks the course row until commit/rollback: two people can't take the last seat at once.
        cursor.execute("SELECT course_id, max_students FROM course WHERE course_code = %s FOR UPDATE", (course_code,))
        course = cursor.fetchone()
        if course is None:
            raise NotFound(f"There is no course {course_code}")
        cursor.execute("SELECT COUNT(*) AS taken FROM enrollment WHERE course_id = %s", (course["course_id"],))
        if cursor.fetchone()["taken"] >= course["max_students"]:
            raise CourseFull(f"{course_code} is full")
        cursor.execute("""
            INSERT INTO enrollment (student_id, course_id, enrolled_on)
            VALUES (%s, %s, CURDATE())
        """, (student_id, course["course_id"]))
        conn.commit()                                            # save, and let go of the lock
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:                  # the primary key (student_id, course_id)
            raise AlreadyEnrolled(f"Student {student_id} already takes {course_code}") from err
        raise
    except Exception:
        conn.rollback()                                          # NotFound / CourseFull: let go of the lock
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def unenroll(student_id, course_code):
    """D on enrollment: take a student out of a course. Returns True if there was something to remove."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE e FROM enrollment e
            JOIN course c ON c.course_id = e.course_id
            WHERE e.student_id = %s AND c.course_code = %s
        """, (student_id, course_code))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()