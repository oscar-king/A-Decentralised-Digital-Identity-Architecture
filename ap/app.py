from flask import Flask
import os
app = Flask(__name__)

@app.route("/")
def index():

    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")

    if app_name:
        return f"Hello from {app_name} running in a Docker container behind nginx!"

    return "Hello from Flask"

if __name__ == '__main__':
    app.run()