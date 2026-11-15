"""Starts the web app. Run it from the project folder: python run.py"""
from sms_web import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)