"""Your first Flask app. Run it with the green Run button, or: python practice/hello.py
Then open http://127.0.0.1python practice/hello.py:5000 in your browser.
"""
from flask import Flask

app = Flask(__name__)                     # 1. make the app


@app.route("/")                           # 2. when someone asks for the address "/" ...
def home():                               # ... Flask calls this function ...
    return "<h1>Student Management System</h1><p>Hello from Flask!</p>"   # ... and sends back what it returns


@app.route("/about")
def about():
    return "This app keeps track of the students at our school."


if __name__ == "__main__":
    app.run(debug=True)                   # 3. start the server (debug: restarts when you save)