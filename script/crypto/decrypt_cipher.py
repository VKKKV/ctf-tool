#!/usr/bin/env python3
C = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! "
OFF = 2

def dec(s,OFF=OFF):
    r = []
    for i in range(0, len(s), 2):
        r.append(C[int(s[i:i+2], 16) - OFF])
    return "".join(r)

if __name__ == "__main__":
    for a in input().split():
        for off in range(len(C)):
            try:
                print("idx:", off)
                print(dec(a, off))
            except IndexError:
                pass
