"""app.py (starting point): it works, but the SQL, the connection and the printing are all mixed together."""
from db import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT first_name, last_name, email FROM student ORDER BY last_name")
for student in cursor.fetchall():
    print(student["first_name"], student["last_name"], student["email"])
cursor.close()
conn.close()