#!/usr/bin/env python3
import json, math, os, random, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
KEY='REMOVED'
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
CT20='8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91'
OUT='/tmp/tm20_stats.jsonl'

def enc(text):
    url='http://api.trytodecrypt.com/encrypt?key=%s&id=20&text=%s'%(KEY,urllib.parse.quote(text))
    for a in range(3):
        try:
            with urllib.request.urlopen(url,timeout=6) as r:
                s=r.read().decode().strip().upper()
            return s if len(s)==90 else None
        except Exception:
            time.sleep(0.4*(a+1))
    return None

def gs(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def feats(g,i):
    p,b1,b2=g
    return {
      'p':p,'b1h':b1>>4,'b1l':b1&15,'b2h':b2>>4,'b2l':b2&15,
      'd71':(b2-b1)%71,'d256':(b2-b1)%256,'dm_p':(b2-b1-p)%71,'dp_p':(b2-b1+p)%71,
      'xor71':(b1^b2)%71,'sum71':(b1+b2)%71,
      'b1m71':b1%71,'b2m71':b2%71,
      'i':i,
    }

def solve(ans):
    url='http://api.trytodecrypt.com/solve?key=%s&id=20&solution=%s'%(KEY,urllib.parse.quote(ans))
    with urllib.request.urlopen(url,timeout=15) as r: return r.read().decode().strip()

target=[feats(g,i) for i,g in enumerate(gs(CT20))]
# collect samples: repeated-char strings isolate char distribution at every position
with open(OUT,'a') as f:
    for round in range(8):
        chars=list(C); random.shuffle(chars)
        for ch in chars:
            s=enc(ch*18)
            if not s: continue
            rec={'ch':ch,'ct':s}
            f.write(json.dumps(rec)+'\n'); f.flush()
            print('sample',round,repr(ch))
            time.sleep(0.1)

# score using categorical feature matches with Laplace smoothing
samples=[]
for line in open(OUT):
    try: samples.append(json.loads(line))
    except Exception: pass
cnt=defaultdict(lambda: defaultdict(Counter)); total=Counter()
for rec in samples:
    ch=rec['ch']; total[ch]+=1
    for i,g in enumerate(gs(rec['ct'])):
        fs=feats(g,i)
        for k,v in fs.items():
            if k!='i': cnt[(i,k)][ch][v]+=1

cand=[]
for i,t in enumerate(target):
    scores=[]
    for ch in C:
        sc=0.0
        n=max(1,total[ch])
        for k,v in t.items():
            if k=='i': continue
            # feature cardinalities rough
            card=256 if k in ('d256',) else (16 if k.endswith('h') or k.endswith('l') or k=='p' else 71)
            sc += math.log((cnt[(i,k)][ch][v]+0.5)/(n+0.5*card))
        scores.append((sc,ch))
    scores.sort(reverse=True)
    cand.append(scores)
    print('pos',i,'target',t,'top',[(ch,round(sc,2)) for sc,ch in scores[:8]])
ans=''.join(x[0][1] for x in cand)
print('best',ans)
try: print('solve',solve(ans))
except Exception as e: print('solve_error',e)
