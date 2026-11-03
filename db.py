"""db.py: the ONLY file that knows how to connect to MySQL. The values come from .env."""
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Open and return a new connection to the Student Management System database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )