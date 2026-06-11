#!/usr/bin/env python3
import json, math, random
from pathlib import Path
from collections import defaultdict, Counter

C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_relation_probe.jsonl','/tmp/tm23_probe.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_repeated_allchars.jsonl']

def inline(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def front(ct):
 n=len(ct)//5; pref=ct[:n]; data=ct[n:]
 return [(int(pref[i],16),int(data[4*i:4*i+2],16),int(data[4*i+2:4*i+4],16)) for i in range(n)]
def idx(pos,layer,order): return pos*5+layer if order=='char' else layer*10+pos
def vals(ct,layout,order):
 toks=(front if layout=='front' else inline)(ct); out=[]
 for pos in range(10):
  row=[]
  for layer in range(5):
   p,a,b=toks[idx(pos,layer,order)]
   row.append({'p':p,'a':a%71,'b':b%71,'d':(b-a)%71,'x':(a^b)%71,'s':(a+b)%71})
  out.append(row)
 return out
def load():
 by=defaultdict(list)
 for path in PATHS:
  p=Path(path)
  if not p.exists(): continue
  for line in p.read_text().splitlines():
   try:j=json.loads(line)
   except: continue
   t=j.get('text',''); ct=j.get('ct','').upper()
   if len(t)==10 and len(ct)==250: by[t].append(ct)
 return by
def dist(a,b):
 # multiset-friendly nearest distance for small mod-71 vectors
 return sum(min((x-y)%71,(y-x)%71) for x,y in zip(a,b))
def signature(ct,layout,order,pos,kind):
 v=vals(ct,layout,order)[pos]
 if kind=='raw_d': return [r['d'] for r in v]
 if kind=='pair_d': return [(v[j]['d']-v[i]['d'])%71 for i in range(5) for j in range(i+1,5)]
 if kind=='pair_a': return [(v[j]['a']-v[i]['a'])%71 for i in range(5) for j in range(i+1,5)]
 if kind=='pair_b': return [(v[j]['b']-v[i]['b'])%71 for i in range(5) for j in range(i+1,5)]
 if kind=='mix': return [(v[j]['d']-v[i]['d'])%71 for i in range(5) for j in range(i+1,5)] + [(v[j]['x']-v[i]['x'])%71 for i in range(5) for j in range(i+1,5)]
 raise KeyError(kind)
def classify(by,layout,order,kind):
 chars=[t[0] for t in by if len(set(t))==1 and len(t)==10]
 # prototypes per char,pos from repeated strings
 proto={}
 for ch in chars:
  cts=by[ch*10]
  for pos in range(10):
   sigs=[signature(ct,layout,order,pos,kind) for ct in cts]
   # medoid
   best=min(sigs, key=lambda s: sum(dist(s,o) for o in sigs))
   proto[(ch,pos)]=best
 tests=[]
 for t,cts in by.items():
  if len(t)==10 and len(set(t))>7:
   tests.extend((t,ct) for ct in cts)
 random.seed(5); random.shuffle(tests); tests=tests[:200]
 top1=top5=n=0
 for t,ct in tests:
  for pos,ch in enumerate(t):
   sig=signature(ct,layout,order,pos,kind)
   ranks=sorted((dist(sig,proto[(c,pos)]),c) for c in chars if (c,pos) in proto)
   pred=[c for _,c in ranks[:5]]
   n+=1; top1+=pred[0]==ch; top5+=ch in pred
 return top1/n if n else 0, top5/n if n else 0, len(chars), len(tests)
def target(by,layout,order,kind):
 chars=[t[0] for t in by if len(set(t))==1 and len(t)==10]
 proto={}
 for ch in chars:
  for pos in range(10):
   sigs=[signature(ct,layout,order,pos,kind) for ct in by[ch*10]]
   proto[(ch,pos)]=min(sigs, key=lambda s: sum(dist(s,o) for o in sigs))
 out=''; tops=[]
 for pos in range(10):
  sig=signature(TARGET,layout,order,pos,kind)
  ranks=sorted((dist(sig,proto[(c,pos)]),c) for c in chars if (c,pos) in proto)
  out+=ranks[0][1]; tops.append(''.join(c for _,c in ranks[:8]))
 return out,tops
def main():
 by=load(); print('texts',len(by),'repeated',sum(1 for t in by if len(set(t))==1 and len(t)==10))
 for layout in ['inline','front']:
  for order in ['char','layer']:
   for kind in ['raw_d','pair_d','pair_a','pair_b','mix']:
    r=classify(by,layout,order,kind)
    print(layout,order,kind,'top1=%.4f top5=%.4f chars=%d tests=%d'%r,'target',target(by,layout,order,kind))
if __name__=='__main__': main()
