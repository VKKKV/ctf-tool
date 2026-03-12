import requests

URL = "http://localhost/"

HEAD = {
    "Host": "challenge.localhost:80",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
}

# auto redirect

def main():
    res = requests.get(URL, headers=HEAD)
    print(res.text.strip())


if __name__ == "__main__":
    main()

# @app.route("/", methods=["GET"])
# def challenge_redirector():
#     if name_of_program_for(peer_process_of(flask.request.input_stream.fileno())) not in ["python3"]:
#         flask.abort(400, "You are using an incorrect client to access this resource!")
#
#     return flask.redirect(f"/{secret_endpoint}-mission")
#
#
# @app.route(f"/{secret_endpoint}-mission", methods=["GET"])
# def challenge():
#     if name_of_program_for(peer_process_of(flask.request.input_stream.fileno())) not in ["python3"]:
#         flask.abort(400, "You are using an incorrect client to access this resource!")
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
# hacker@talking-web~http-redirects-p
