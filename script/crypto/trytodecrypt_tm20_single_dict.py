#!/usr/bin/env python3
import urllib.parse, urllib.request, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter
KEY='REMOVED'
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
CT20='8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91'
TG=[CT20[i:i+5] for i in range(0,len(CT20),5)]
TG_FRONT=[CT20[i]+CT20[len(CT20)//5+4*i:len(CT20)//5+4*i+4] for i in range(len(CT20)//5)]

def enc_one(ch):
    url='http://api.trytodecrypt.com/encrypt?key=%s&id=20&text=%s'%(KEY,urllib.parse.quote(ch))
    for a in range(3):
        try:
            with urllib.request.urlopen(url,timeout=5) as r:
                s=r.read().decode().strip().upper()
            if len(s)==5: return ch,s
            return ch,'ERR:'+s[:50]
        except Exception as e:
            if a==2: return ch,'EXC:'+repr(e)[:50]
            time.sleep(0.2)

hits=[]; counts=Counter(); by=defaultdict(Counter)
N=200
with ThreadPoolExecutor(max_workers=10) as ex:
    futs=[ex.submit(enc_one,ch) for ch in C for _ in range(N)]
    for i,f in enumerate(as_completed(futs),1):
        ch,s=f.result(); counts[s]+=1; by[ch][s]+=1
        if s in TG or s in TG_FRONT:
            hits.append((ch,s,'inline' if s in TG else 'front'))
            print('HIT',hits[-1],flush=True)
        if i%500==0:
            print('progress',i,'hits',len(hits),file=sys.stderr,flush=True)
print('DONE hits',hits)
for ch in C:
    print(repr(ch), by[ch].most_common(10), file=sys.stderr)
