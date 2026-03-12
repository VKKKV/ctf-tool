import base64
import sys


def encode_to_bits(s):
    return b"".join(format(c, "08b").encode("latin1") for c in s)

correct_password = b"KO#_\x03\x8dG0"
correct_password = correct_password.hex().encode("l1")
correct_password = correct_password.hex().encode("l1")
correct_password = correct_password.hex().encode("l1")
correct_password = encode_to_bits(correct_password)

sys.stdout.buffer.write(correct_password)


