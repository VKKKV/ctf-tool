#!/usr/bin/env python3
import itertools, urllib.parse, urllib.request, time, sys
KEY='REMOVED'
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
CT20='8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91'

def enc(text):
    url='http://api.trytodecrypt.com/encrypt?key=%s&id=20&text=%s'%(KEY,urllib.parse.quote(text))
    for a in range(4):
        try:
            with urllib.request.urlopen(url,timeout=6) as r:
                s=r.read().decode().strip().upper()
            if len(s)==90: return s
            return s
        except Exception:
            time.sleep(0.5*(a+1))
    return None

def solve(ans):
    url='http://api.trytodecrypt.com/solve?key=%s&id=20&solution=%s'%(KEY,urllib.parse.quote(ans))
    with urllib.request.urlopen(url,timeout=15) as r: return r.read().decode().strip()

def groups(ct): return [ct[i:i+5] for i in range(0,len(ct),5)]

target=groups(CT20)
# Use binary-style coverage: each position gets all charset chars over 71 requests.
known=[{} for _ in range(18)]
for off in range(len(C)):
    q=''.join(C[(off+i)%len(C)] for i in range(18))
    ct=enc(q)
    if not ct:
        print('timeout',off,file=sys.stderr); continue
    if len(ct)!=90:
        print('bad',off,ct,file=sys.stderr); continue
    for pos,(g,ch) in enumerate(zip(groups(ct),q)):
        known[pos][g]=ch
    cand=''.join(known[i].get(target[i],'?') for i in range(18))
    print(off,repr(q),cand)
    if '?' not in cand:
        print('FOUND',cand,'solve',solve(cand)); break
    time.sleep(0.2)
print('final',''.join(known[i].get(target[i],'?') for i in range(18)))
print([len(k) for k in known])
