"""The data layer: the ONLY file that talks to MySQL.

Every function follows the same five steps:
1. connect   2. make a cursor that gives rows as dicts   3. run the SQL
4. give the result back (and commit if we changed something)   5. always close
"""
import mysql.connector
from mysql.connector import errorcode

from db import get_connection


class EmailTaken(Exception):
    """Another student already has this email (MySQL error 1062: the UNIQUE rule)."""


# ------------------------------------------------------------------ reading

def get_all_students():
    """Return every student as a list of dicts, sorted by last name."""
    conn = get_connection()                       # 1. connect
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)     # 2. each row comes back as a dict
        cursor.execute("""
            SELECT student_id, first_name, last_name, email, class_name
            FROM student
            ORDER BY last_name, first_name
        """)                                      # 3. run the SQL
        return cursor.fetchall()                  # 4. give all rows to the caller
    finally:
        if cursor is not None:                    # 5. always close, whatever happened
            cursor.close()
        conn.close()


def search_students(text):
    """Return the students whose first or last name contains the text, like "ha"."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        pattern = f"%{text}%"                     # % = "anything" in SQL LIKE
        cursor.execute("""
            SELECT student_id, first_name, last_name, email, class_name
            FROM student
            WHERE first_name LIKE %s OR last_name LIKE %s
            ORDER BY last_name, first_name
        """, (pattern, pattern))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def find_student(email):
    """Return one student as a dict, or None if no student has that email."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT student_id, first_name, last_name, email, class_name
            FROM student
            WHERE email = %s
        """, (email,))                            # the comma makes it a tuple
        return cursor.fetchone()                  # None if no row matched
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def get_student(student_id):
    """Return one student as a dict, or None if there is no student with that id."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT student_id, first_name, last_name, email, class_name
            FROM student
            WHERE student_id = %s
        """, (student_id,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def class_overview():
    """Return every class with its number of students: [{'class_name': '2A', 'student_count': 3}, ...]"""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT class_name, COUNT(*) AS student_count
            FROM student
            GROUP BY class_name
            ORDER BY class_name
        """)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def students_in_class(class_name):
    """Return the students in one class, sorted by last name. [] if nobody is in that class."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT student_id, first_name, last_name, email, class_name
            FROM student
            WHERE class_name = %s
            ORDER BY last_name, first_name
        """, (class_name,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# ------------------------------------------------------------------ changing

def add_student(first_name, last_name, email, class_name):
    """Save a new student and return the new student_id.
    Raises EmailTaken if another student already has the email."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO student (first_name, last_name, email, class_name)
            VALUES (%s, %s, %s, %s)
        """, (first_name, last_name, email, class_name))
        conn.commit()                             # save the change for real
        return cursor.lastrowid                   # the id MySQL gave the new row
    except mysql.connector.Error as err:
        conn.rollback()                           # undo the half-done change
        if err.errno == errorcode.ER_DUP_ENTRY:   # 1062: the email is already used
            raise EmailTaken(f"{email} is already in use") from err
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def delete_student(student_id):
    """Delete one student. Returns True if a student was deleted, False if the id didn't exist."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        conn.commit()
        return cursor.rowcount == 1               # how many rows were deleted
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()