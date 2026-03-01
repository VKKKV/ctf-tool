import os

from flask import Flask, request
from werkzeug.debug import DebuggedApplication

app = Flask(__name__)
secret = os.urandom(32)
app.wsgi_app = DebuggedApplication(
    app.wsgi_app, evalex=True, console_path=secret, pin_security=False
)
app.config["SECRET_KEY"] = secret
calculate = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
}


def safe_cast(val, to_type):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return None


@app.route("/calculator")
def flag():
    number_1 = safe_cast(request.args.get("number_1"), int)
    number_2 = safe_cast(request.args.get("number_2"), int)
    operation = safe_cast(request.args.get("operation"), str)
    if None in (number_1, number_2, operation) or not operation in calculate:
        return "Invalid calculator parameters"
    return "Calculation complete: %s" % calculate[operation](number_1, number_2)


if __name__ == "__main__":
    app.run()
