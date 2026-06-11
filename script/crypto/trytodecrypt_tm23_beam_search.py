#!/usr/bin/env python3
import json, math, random, itertools
from pathlib import Path
from collections import Counter, defaultdict

C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']

def inline(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def front(ct):
 n=len(ct)//5; pref=ct[:n]; data=ct[n:]
 return [(int(pref[i],16),int(data[4*i:4*i+2],16),int(data[4*i+2:4*i+4],16)) for i in range(n)]
def load():
 rows=[]; seen=set()
 for path in PATHS:
  p=Path(path)
  if not p.exists(): continue
  for line in p.read_text().splitlines():
   try:j=json.loads(line)
   except Exception: continue
   t=j.get('text',''); ct=j.get('ct','').upper()
   if len(t)==10 and len(ct)==250 and (t,ct) not in seen:
    seen.add((t,ct)); rows.append((t,ct))
 return rows
def idx(pos,layer,order): return pos*5+layer if order=='char' else layer*10+pos
def arr(ct,layout,order):
 toks=(front if layout=='front' else inline)(ct); out=[]
 for pos in range(10):
  row=[]
  for layer in range(5):
   p,a,b=toks[idx(pos,layer,order)]
   row.append({'p':p,'a71':a%71,'b71':b%71,'d71':(b-a)%71,'x71':(a^b)%71,'s71':(a+b)%71,'ah':a>>4,'al':a&15,'bh':b>>4,'bl':b&15})
  out.append(row)
 return out
def specs():
 out=[]
 for l in range(5):
  for n in ['p','a71','b71','d71','x71','s71','ah','al','bh','bl']:
   out.append(('single',l,n))
 for l1 in range(5):
  for l2 in range(l1+1,5):
   for n in ['a71','b71','d71','x71','s71']:
    for op in ['sub','add','xor']:
     out.append(('pair',l1,l2,n,op))
 for l in range(5):
  for n in ['a71','b71','d71','x71','s71']:
   for op in ['sub','add','xor']:
    out.append(('adj',l,n,op))
 return out
def feat(vals,pos,sp):
 if sp[0]=='single': return vals[pos][sp[1]][sp[2]]
 if sp[0]=='pair': _,l1,l2,n,op=sp; x=vals[pos][l1][n]; y=vals[pos][l2][n]
 else:
  _,l1,n,op=sp
  if pos==9: return None
  x=vals[pos][l1][n]; y=vals[pos+1][l1][n]
 if op=='sub': return (y-x)%71
 if op=='add': return (x+y)%71
 return (x^y)%71
def eval_combo(parsed, combo, folds=5):
 texts=sorted({t for t,_ in parsed}); random.seed(23); random.shuffle(texts)
 chunks=[set(texts[i::folds]) for i in range(folds)]
 top1=top5=n=0
 for test_texts in chunks:
  tab=defaultdict(Counter); prior=Counter()
  for text,vals in parsed:
   if text in test_texts: continue
   for pos,ch in enumerate(text):
    prior[ch]+=1
    for si,sp in enumerate(combo):
     v=feat(vals,pos,sp)
     if v is not None: tab[(si,pos,v)][ch]+=1
  for text,vals in parsed:
   if text not in test_texts or len(set(text))<=7: continue
   for pos,ch in enumerate(text):
    scores={c:math.log(prior[c]+1) for c in C}
    for si,sp in enumerate(combo):
     v=feat(vals,pos,sp); cnt=tab.get((si,pos,v),{}); tot=sum(cnt.values())
     for c in C: scores[c]+=math.log((cnt.get(c,0)+0.35)/(tot+0.35*71))
    pred=[c for c,_ in sorted(scores.items(),key=lambda kv:kv[1],reverse=True)[:5]]
    n+=1; top1+=pred[0]==ch; top5+=ch in pred
 return top1/n if n else 0, top5/n if n else 0, n
def guess(rows,layout,order,combo):
 parsed=[(t,arr(ct,layout,order)) for t,ct in rows]
 tab=defaultdict(Counter); prior=Counter()
 for text,vals in parsed:
  for pos,ch in enumerate(text):
   prior[ch]+=1
   for si,sp in enumerate(combo):
    v=feat(vals,pos,sp)
    if v is not None: tab[(si,pos,v)][ch]+=1
 tv=arr(TARGET,layout,order); out=''; tops=[]
 for pos in range(10):
  scores={c:math.log(prior[c]+1) for c in C}
  for si,sp in enumerate(combo):
   v=feat(tv,pos,sp); cnt=tab.get((si,pos,v),{}); tot=sum(cnt.values())
   for c in C: scores[c]+=math.log((cnt.get(c,0)+0.35)/(tot+0.35*71))
  top=sorted(scores.items(),key=lambda kv:kv[1],reverse=True)[:10]
  out+=top[0][0]; tops.append(''.join(c for c,_ in top))
 return out,tops

def main():
 rows=load(); random.seed(9)
 randomish=[r for r in rows if len(set(r[0]))>7]; repeated=[r for r in rows if len(set(r[0]))==1]
 rows=randomish+repeated[:500]
 print('rows',len(rows),'unique_texts',len({t for t,_ in rows}),'randomish',len(randomish))
 spl=specs()
 for layout,order in [('front','char'),('front','layer'),('inline','char'),('inline','layer')]:
  parsed=[(t,arr(ct,layout,order)) for t,ct in rows]
  singles=[]
  for sp in spl:
   a,b,n=eval_combo(parsed,(sp,),folds=5)
   singles.append((b,a,sp))
  singles=sorted(singles,reverse=True)
  print('\nBASE',layout,order)
  for b,a,sp in singles[:12]: print('single top1=%.4f top5=%.4f %r'%(a,b,sp))
  beam=[(singles[i][1],singles[i][0],(singles[i][2],)) for i in range(8)]
  for depth in [2,3,4]:
   cand=[]
   pool=[x[2] for x in singles[:35]]
   seen=set()
   for _,_,combo in beam:
    for sp in pool:
     if sp in combo: continue
     nc=tuple(list(combo)+[sp])
     key=tuple(sorted(map(repr,nc)))
     if key in seen: continue
     seen.add(key)
     a,b,n=eval_combo(parsed,nc,folds=5)
     cand.append((a,b,nc))
   beam=sorted(cand,key=lambda x:(x[1],x[0]),reverse=True)[:10]
   print('depth',depth,'best')
   for a,b,combo in beam[:5]: print(' combo top1=%.4f top5=%.4f %s'%(a,b,combo))
  best=beam[0][2]
  print('TARGET',guess(rows,layout,order,best),'combo',best)
if __name__=='__main__': main()
