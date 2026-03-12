import base64
import sys

def reverse_string(s):
    return s[::-1]

print("Enter the password:")
correct_password = b"\xc8\xf2#\xb4\x94@\x82N"


correct_password = correct_password[::-1]
correct_password = correct_password.hex().encode("l1")
correct_password = correct_password[::-1]
correct_password = correct_password[::-1]



correct_password = correct_password[::-1]
correct_password = correct_password.hex().encode("l1")
correct_password = base64.b64encode(correct_password)
correct_password = correct_password[::-1]


print(correct_password)

