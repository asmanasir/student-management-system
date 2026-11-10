from db import get_connection


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

        def find_student(email):
            """Return one student as a dict, or None if no student has that email."""
            conn = get_connection()
            cursor = None
            try:
                cursor = conn.cursor(dictionary=True)
                sql = """
                    SELECT student_id, first_name, last_name, email, class_name
                    FROM student
                    WHERE email = %s
                """
                cursor.execute(sql, (email,))  # the comma makes it a tuple
                return cursor.fetchone()  # None if no row matched
            finally:
                if cursor is not None:
                    cursor.close()
                conn.close()