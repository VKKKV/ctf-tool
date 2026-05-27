#!/usr/bin/env python3
import sys, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
# WARNING: API key was hardcoded here. Use env var instead.
import os
KEY=os.environ.get('TTD_API_KEY', 'YOUR_API_KEY_HERE')
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
CT20='8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91'

def enc(id,text):
    url='http://api.trytodecrypt.com/encrypt?key=%s&id=%d&text=%s'%(KEY,id,urllib.parse.quote(text))
    with urllib.request.urlopen(url,timeout=15) as r:
        return r.read().decode().strip().upper()

def g_inline(ct): return [ct[i:i+5] for i in range(0,len(ct),5)]
def g_front(ct):
    n=len(ct)//5; return [ct[i]+ct[n+4*i:n+4*i+4] for i in range(n)]

target_inline=set(g_inline(CT20)); target_front=set(g_front(CT20))
print('target inline',g_inline(CT20))
print('target front',g_front(CT20))
for ch in C:
    ci=Counter(); cf=Counter()
    for k in range(80):
        s=enc(20,ch)
        ci.update(g_inline(s)); cf.update(g_front(s))
    hit_i=target_inline & set(ci)
    hit_f=target_front & set(cf)
    if hit_i or hit_f:
        print('HIT',repr(ch),'inline',hit_i,'front',hit_f)
    print(repr(ch),'uniq_inline',len(ci),'top',ci.most_common(3),'uniq_front',len(cf),file=sys.stderr)
