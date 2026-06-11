#!/usr/bin/env python3
import itertools, json, random
from pathlib import Path
from collections import Counter
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
   if len(t)==10 and len(ct)==250 and len(set(t))>7 and (t,ct) not in seen:
    seen.add((t,ct)); rows.append((t,ct))
 random.seed(31); random.shuffle(rows)
 return rows[:180]
def extract(ct,layout,order,expr):
 toks=(front if layout=='front' else inline)(ct); out=[]
 for pos in range(10):
  row=[]
  for layer in range(5):
   p,a,b=toks[idx(pos,layer,order)]
   d={'p':p,'a':a%71,'b':b%71,'d':(b-a)%71,'x':(a^b)%71,'s':(a+b)%71,'ah':a>>4,'al':a&15,'bh':b>>4,'bl':b&15}
   row.append(d[expr])
  out.append(row)
 return out
def main():
 rows=load(); print('rows',len(rows),flush=True)
 coeffs=[c for c in itertools.product([-1,0,1], repeat=5) if 1<=sum(abs(x) for x in c)<=2]
 for layout in ['inline','front']:
  for order in ['char','layer']:
   for expr in ['p','a','b','d','x','s','ah','al','bh','bl']:
    data=[(t,extract(ct,layout,order,expr)) for t,ct in rows]
    best=[]
    # linear coeffs: score by most common bias pred-true
    for co in coeffs:
     hist=Counter()
     for t,arr in data:
      for pos,ch in enumerate(t):
       pred=sum(co[i]*arr[pos][i] for i in range(5))%71
       hist[(pred-C.index(ch))%71]+=1
     bias,cnt=hist.most_common(1)[0]
     if cnt/(len(data)*10)>0.045: best.append((cnt/(len(data)*10),bias,('lin',co)))
    for i in range(5):
     for j in range(i+1,5):
      for op in ['sub','rsub','add','xor']:
       hist=Counter()
       for t,arr in data:
        for pos,ch in enumerate(t):
         x,y=arr[pos][i],arr[pos][j]
         pred={'sub':y-x,'rsub':x-y,'add':x+y,'xor':x^y}[op]%71
         hist[(pred-C.index(ch))%71]+=1
       bias,cnt=hist.most_common(1)[0]
       if cnt/(len(data)*10)>0.045: best.append((cnt/(len(data)*10),bias,('pair',i,j,op)))
    if best:
     print('\n',layout,order,expr,flush=True)
     for sc,bias,f in sorted(best,reverse=True)[:8]:
      arr=extract(TARGET,layout,order,expr); out=''
      for pos in range(10):
       if f[0]=='lin': pred=sum(f[1][i]*arr[pos][i] for i in range(5))%71
       else:
        _,i,j,op=f; x,y=arr[pos][i],arr[pos][j]; pred={'sub':y-x,'rsub':x-y,'add':x+y,'xor':x^y}[op]%71
       out+=C[(pred-bias)%71]
      print('%.4f bias=%d target=%s %r'%(sc,bias,out,f),flush=True)
if __name__=='__main__': main()
