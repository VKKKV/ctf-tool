import string

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from pwn import *
from pwn import context, enhex, log, process, remote, unhex, xor

# PKCS#7 default pad()

context.log_level = "info"

charset = string.printable.strip()

log.info("Start")

URL = "http://challenge.localhost/"
CHARSET = string.printable.strip() + "}"

print()

r.interactive()

# challenge here

db.execute("""CREATE TABLE secrets AS SELECT ? AS flag""", [open("/flag").read()])

curl -X GET "http://challenge.localhost/?query='A'"

@app.route("/", methods=["GET"])
def challenge_get():
    query = flask.request.args.get("query") or "'A'"

    try:
        sql = f"SELECT {query} FROM secrets"
        print(f"DEBUG: {sql=}")
        pt = db.execute(sql).fetchone()[0]
    except sqlite3.Error as e:
        flask.abort(500, f"Query: {query}\nError: {e}")
    except TypeError:
        # no records found
        pt = "A"

    ct = cipher.encrypt(pad(pt.encode(), cipher.block_size))

    return f"""
        <html><body>Welcome to pwn.secret!
        <form>SELECT <input type=text name=query value='{query}'> FROM secrets<br><input type=submit value=Submit></form>
        <hr>
        <b>Query:</b> <pre>{sql}</pre><br>
        <b>Results:</b><pre>{ct.hex()}</pre>
        </body></html>
    """
