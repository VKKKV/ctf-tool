#!/usr/bin/env python3
"""
Prime Number Utilities
Includes Sieve of Eratosthenes and a custom search for primes with prime digit sums.
"""

def sieve_of_eratosthenes(limit):
    """Returns a list of all primes up to the given limit."""
    if limit < 2:
        return []

    primes_flag = [True] * (limit + 1)
    primes_flag[0] = primes_flag[1] = False

    p = 2
    while p * p <= limit:
        if primes_flag[p]:
            for i in range(p * p, limit + 1, p):
                primes_flag[i] = False
        p += 1
    return [p for p in range(2, limit + 1) if primes_flag[p]]

def is_prime(n):
    """Standard primality test."""
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_special_primes(start_val, count=2):
    """
    Finds primes where the sum of their digits is also a prime number.
    Often used in crypto challenges.
    """
    found = []
    current = start_val
    while len(found) < count:
        current += 1
        digit_sum = sum(int(d) for d in str(current))
        if is_prime(current) and is_prime(digit_sum):
            found.append(current)
    return found

if __name__ == "__main__":
    # Example: Find two primes > 1,000,000 with prime digit sums
    results = find_special_primes(1000000, 2)
    print(f"[*] Found special primes: {results}")
    print(f"[*] Concatenated: {''.join(map(str, results))}")
