def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def extended_gcd(q, p):
    if q == 0:
        return p, 0, 1
    else:
        g, y, x = extended_gcd(p % q, q)
        return g, x - (p // q) * y, y


p = 26513
q = 32321

g, x, y = extended_gcd(q, p)

print(f"p = {p}")
print(f"q = {q}")
print(f"g = {g}")
print(f"x = {x}")
print(f"y = {y}")
