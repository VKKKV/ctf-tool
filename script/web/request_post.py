import requests

URL = "http://localhost/gate"

HEAD = {
    "Host": "challenge.localhost:80",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
}

# POST = {"access_code": "dezevikr"}
POST = {"pin": "gdaabxwh"}


def main():
    res = requests.post(URL, headers=HEAD, data=POST)
    print(res.text.strip())


if __name__ == "__main__":
    main()

# @app.route("/gate", methods=["POST"])
# def challenge():
#     if "Firefox" not in flask.request.headers.get("User-Agent"):
#         flask.abort(400, "You are using an incorrect client to access this resource!")
#
#     if flask.request.form.get("pin", None) != "gdaabxwh":
#         flask.abort(403, "Incorrect value for post parameter pin!")
#
#     return f"""
#         <html>
#           <head><title>Talking Web</title></head>
#         <body>
#           <h1>Great job!</h1>
#           <p>{open("/flag").read().strip()}</p>
#         </body>
#         </html>
#     """
#
#
# app.secret_key = os.urandom(8)
# app.config["SERVER_NAME"] = "challenge.localhost:80"
# app.run("challenge.localhost", 80)
#
