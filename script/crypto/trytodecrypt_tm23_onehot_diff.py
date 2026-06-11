#!/usr/bin/env python3
import json, random
from pathlib import Path
from collections import defaultdict, Counter
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
PATHS=['/tmp/tm23_relation_probe.jsonl','/tmp/tm23_probe.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_repeated_allchars.jsonl']
def inline(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def front(ct):
 n=len(ct)//5; pref=ct[:n]; data=ct[n:]
 return [(int(pref[i],16),int(data[4*i:4*i+2],16),int(data[4*i+2:4*i+4],16)) for i in range(n)]
def idx(pos,layer,order): return pos*5+layer if order=='char' else layer*10+pos
def feat(ct,layout,order):
 toks=(front if layout=='front' else inline)(ct); out=[]
 for pos in range(10):
  row=[]
  for layer in range(5):
   p,a,b=toks[idx(pos,layer,order)]
   row.append((p,a%71,b%71,(b-a)%71,(a^b)%71,(a+b)%71))
  out.append(row)
 return out
def load():
 by=defaultdict(list)
 for path in PATHS:
  if not Path(path).exists(): continue
  for line in open(path):
   try:j=json.loads(line)
   except Exception: continue
   t=j.get('text',''); ct=j.get('ct','').upper()
   if len(t)==10 and len(ct)==250: by[t].append(ct)
 return by
def diffvec(fa,fb,pos):
 out=[]
 for layer in range(5):
  for k in range(6):
   out.append((fb[pos][layer][k]-fa[pos][layer][k])%71)
 return out
def dist(x,y): return sum(a!=b for a,b in zip(x,y))
def main():
 by=load(); print('texts',len(by))
 # one-hot pairs base 0/a, variants 1,b,B,! at each position
 pairs=[]
 for base in ['0','a']:
  btxt=base*10
  for pos in range(10):
   for ch in ['1','b','B','!']:
    t=base*pos+ch+base*(9-pos)
    if btxt in by and t in by:
     for ct0 in by[btxt][:2]:
      for ct1 in by[t][:2]: pairs.append((base,ch,pos,ct0,ct1))
 print('pairs',len(pairs))
 for layout in ['inline','front']:
  for order in ['char','layer']:
   print('\n',layout,order)
   # Does changed plaintext position have smallest/largest diff concentration?
   hit=tot=0; spread=Counter(); proto=defaultdict(list)
   for base,ch,pos,ct0,ct1 in pairs:
    f0=feat(ct0,layout,order); f1=feat(ct1,layout,order)
    scores=[]
    for p in range(10):
     dv=diffvec(f0,f1,p)
     # nonzero count + entropy-ish unique count
     scores.append((sum(v!=0 for v in dv), len(set(dv)), p))
    # if one char local, changed pos should be extremal; test both
    if max(scores)[2]==pos or min(scores)[2]==pos: hit+=1
    tot+=1
    spread[max(scores)[2]-pos]+=1
    proto[(base,ch,pos)].append(diffvec(f0,f1,pos))
   print('extreme hit',hit,'/',tot,'=',round(hit/tot,3) if tot else 0,'maxpos-pos common',spread.most_common(8))
   # stability of same base/ch/pos differential vectors across reps
   st=[]
   for key,vs in proto.items():
    if len(vs)<2: continue
    med=min(vs,key=lambda v:sum(dist(v,w) for w in vs))
    st.append(sum(dist(med,v) for v in vs)/(len(vs)*len(med)))
   print('same onehot diff avg hamming ratio',round(sum(st)/len(st),3) if st else None,'n',len(st))
if __name__=='__main__': main()
