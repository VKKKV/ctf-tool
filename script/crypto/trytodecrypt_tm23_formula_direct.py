#!/usr/bin/env python3
import itertools, json, math, random
from pathlib import Path
from collections import Counter, defaultdict

C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']

def inline(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def front(ct):
 n=len(ct)//5; pref=ct[:n]; data=ct[n:]
 return [(int(pref[i],16),int(data[4*i:4*i+2],16),int(data[4*i+2:4*i+4],16)) for i in range(n)]
def idx(pos,layer,order): return pos*5+layer if order=='char' else layer*10+pos
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
def values(ct,layout,order,pos,expr):
 toks=(front if layout=='front' else inline)(ct)
 arr=[]
 for layer in range(5):
  p,a,b=toks[idx(pos,layer,order)]
  d={'p':p,'a':a%71,'b':b%71,'d':(b-a)%71,'x':(a^b)%71,'s':(a+b)%71,'ah':a>>4,'al':a&15,'bh':b>>4,'bl':b&15}
  arr.append(d[expr])
 return arr
def pred_from_expr(vs, formula):
 # formula: linear combination of 5 layer values + const mod 71, or pair op
 kind=formula[0]
 if kind=='lin':
  _,coeffs,c=formula
  return (sum(co*vs[i] for i,co in enumerate(coeffs))+c)%71
 if kind=='pair':
  _,i,j,op,c=formula
  if op=='sub': z=vs[j]-vs[i]
  elif op=='add': z=vs[j]+vs[i]
  elif op=='xor': z=vs[j]^vs[i]
  else: z=vs[i]-vs[j]
  return (z+c)%71
 raise KeyError(kind)
def formulas():
 out=[]
 coeff_sets=[]
 for coeffs in itertools.product([-1,0,1], repeat=5):
  if sum(abs(x) for x in coeffs) in (1,2,3): coeff_sets.append(coeffs)
 for coeffs in coeff_sets:
  for c in range(71): out.append(('lin',coeffs,c))
 for i in range(5):
  for j in range(i+1,5):
   for op in ['sub','rsub','add','xor']:
    for c in range(71): out.append(('pair',i,j,op,c))
 return out
def eval_formula(rows,layout,order,expr,formula):
 # evaluate as direct decoder: predicted charset index must equal plaintext char index
 ids=[i for i,(t,_) in enumerate(rows) if len(set(t))>7]
 random.seed(31); random.shuffle(ids); ids=ids[:300]
 ok=topish=n=0
 hist=Counter()
 for ri in ids:
  t,ct=rows[ri]
  for pos,ch in enumerate(t):
   pred=pred_from_expr(values(ct,layout,order,pos,expr),formula)
   true=C.index(ch)
   diff=(pred-true)%71
   hist[diff]+=1
   n+=1
 # allow unknown constant bias: best diff bucket tells if formula is char+bias
 best=hist.most_common(1)[0][1] if hist else 0
 return best/n if n else 0, hist.most_common(3)
def target(layout,order,expr,formula,bias):
 out=''
 for pos in range(10):
  pred=(pred_from_expr(values(TARGET,layout,order,pos,expr),formula)-bias)%71
  out+=C[pred]
 return out
def main():
 rows=load(); fs=formulas(); print('rows',len(rows),'formulas',len(fs),flush=True)
 best=[]
 for layout in ['inline','front']:
  for order in ['char','layer']:
   for expr in ['p','a','b','d','x','s','ah','al','bh','bl']:
    local=[]
    for f in fs:
     sc,common=eval_formula(rows,layout,order,expr,f)
     if sc>0.055: local.append((sc,layout,order,expr,f,common))
    local=sorted(local,reverse=True)[:8]
    if local:
     print('\n',layout,order,expr,flush=True)
     for sc,la,od,ex,f,common in local:
      bias=common[0][0]
      print('score %.4f bias %s target %s formula %r common %r'%(sc,bias,target(la,od,ex,f,bias),f,common),flush=True)
      best.append((sc,la,od,ex,f,common))
 print('\nBEST')
 for sc,la,od,ex,f,common in sorted(best,reverse=True)[:30]:
  bias=common[0][0]
  print('score %.4f %s %s %s bias %s target %s formula %r'%(sc,la,od,ex,bias,target(la,od,ex,f,bias),f),flush=True)
if __name__=='__main__': main()
