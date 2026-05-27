#!/usr/bin/env python3
import urllib.parse, urllib.request, time
# WARNING: API key was hardcoded here. Use env var instead.
import os
KEY=os.environ.get('TTD_API_KEY', 'YOUR_API_KEY_HERE')
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
CT20='8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91'

def enc(text):
    url='http://api.trytodecrypt.com/encrypt?key=%s&id=20&text=%s'%(KEY,urllib.parse.quote(text))
    with urllib.request.urlopen(url,timeout=15) as r: return r.read().decode().strip().upper()

def solve(ans):
    url='http://api.trytodecrypt.com/solve?key=%s&id=20&solution=%s'%(KEY,urllib.parse.quote(ans))
    with urllib.request.urlopen(url,timeout=15) as r: return r.read().decode().strip()

def groups(ct): return [ct[i:i+5] for i in range(0,len(ct),5)]
def idxs_from_batch(text, ct): return dict(zip(groups(ct), text))

target=groups(CT20)
print('target groups',target)
# Try full-length batches. Comment says longer than plaintext may break, so use exactly 18.
queries=[]
# sliding windows of charset length 18
for off in range(0,len(C)-17,6): queries.append(C[off:off+18])
# random-ish repeated coverage via rotations
for off in range(len(C)): queries.append(''.join(C[(off+i*7)%len(C)] for i in range(18)))
# common phrase probes exactly 18 chars
queries += ['TryToDecrypt! now!','R2D2:C3PO:BB8abc','mississippimississ']
known=[{} for _ in range(18)]
for qi,q in enumerate(queries,1):
    ct=enc(q)
    if len(ct)!=90:
        print('bad len',q,len(ct),ct); continue
    gs=groups(ct)
    for pos,(g,ch) in enumerate(zip(gs,q)):
        known[pos][g]=ch
    cand=''.join(known[i].get(target[i],'?') for i in range(18))
    if qi%10==0 or cand.count('?')<18:
        print(qi,repr(q),'cand',cand)
    if '?' not in cand:
        print('FOUND',cand,'solve',solve(cand)); break
    time.sleep(0.05)
print('final cand',''.join(known[i].get(target[i],'?') for i in range(18)))
for i in range(18): print(i,'known',len(known[i]),'target',target[i],known[i].get(target[i]))
