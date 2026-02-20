#!/usr/bin/env python3

import json

from pwn import *  # pip install pwntools

HOST = "socket.cryptohack.org"
PORT = 11112

r = remote(HOST, PORT)


def json_recv():
    line = r.recvline()
    return json.loads(line.decode())


def json_send(hsh):
    request = json.dumps(hsh).encode()
    r.sendline(request)


print(r.recvline())
print(r.recvline())
print(r.recvline())
print(r.recvline())

request = {"buy": "flag"}
json_send(request)

response = json_recv()

print(response)
