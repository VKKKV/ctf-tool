"""ECB CPA via HTTP: notes and challenge source for SQLi + ECB oracle attack.

Challenge: Flask app encrypts SQL query results with AES-ECB.
Attack: Use SQLi (substr) to extract flag char-by-char, compare ECB blocks.
See request_aes_ecb_cpa_http.py for the working exploit.
"""

# Challenge source (for reference):
#
# db.execute("CREATE TABLE secrets AS SELECT ? AS flag", [open("/flag").read()])
#
# @app.route("/", methods=["GET"])
# def challenge_get():
#     query = flask.request.args.get("query") or "'A'"
#     sql = f"SELECT {query} FROM secrets"
#     pt = db.execute(sql).fetchone()[0]
#     ct = cipher.encrypt(pad(pt.encode(), cipher.block_size))
#     return ct.hex()
#
# Exploit: see request_aes_ecb_cpa_http.py
