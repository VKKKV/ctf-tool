#!/usr/bin/env python3
import json, math, random
from pathlib import Path
from collections import defaultdict,Counter
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_diff_random_pairs.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']

def parse(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def ids(pos,layout): return [pos*5+l for l in range(5)] if layout=='char' else [l*10+pos for l in range(5)]
def fv(ct,pos,layout):
    ts=parse(ct); out=[]
    for i in ids(pos,layout):
        p,a,b=ts[i]; out += [p,a%71,b%71,(b-a)%71,(a+b)%71,(a^b)%71,a>>4,a&15,b>>4,b&15]
    # include neighbors in token stream
    for i in ids(pos,layout):
        for off in [-11,-10,-9,-1,1,9,10,11]:
            p,a,b=ts[(i+off)%50]; out += [(b-a)%71,(a^b)%71]
    return out

def load():
    rows=[]; seen=set()
    for path in PATHS:
        if not Path(path).exists(): continue
        for line in open(path):
            try:j=json.loads(line)
            except: continue
            t=j.get('text',''); ct=j.get('ct','').upper()
            if len(t)==10 and len(ct)==250 and not ct.startswith('ERR') and (t,ct) not in seen:
                seen.add((t,ct)); rows.append((t,ct))
    return rows

def train(rows,layout):
    cnt=defaultdict(Counter); tot=Counter(); pri=Counter()
    for t,ct in rows:
        diff=[i for i,ch in enumerate(t) if ch!='0']
        if len(diff)!=1: continue
        pos=diff[0]; ch=t[pos]; pri[(pos,ch)]+=1
        for k,v in enumerate(fv(ct,pos,layout)):
            cnt[(pos,ch,k)][v]+=1; tot[(pos,ch,k)]+=1
    return cnt,tot,pri

def pred(model,ct,pos,layout):
    cnt,tot,pri=model; fs=fv(ct,pos,layout); ranks=[]
    for ch in C:
        sc=math.log(pri[(pos,ch)]+0.1)
        for k,v in enumerate(fs): sc+=math.log((cnt[(pos,ch,k)][v]+0.05)/(tot[(pos,ch,k)]+3.55))
        ranks.append((sc,ch))
    return [c for _,c in sorted(ranks,reverse=True)]
def eval(rows,layout):
    one=[r for r in rows if sum(ch!='0' for ch in r[0])==1]
    random.seed(77); random.shuffle(one); split=int(len(one)*0.8)
    model=train(one[:split],layout); n=t1=t5=0
    for t,ct in one[split:]:
        pos=[i for i,ch in enumerate(t) if ch!='0'][0]; ch=t[pos]
        p=pred(model,ct,pos,layout); n+=1; t1+=p[0]==ch; t5+=ch in p[:5]
    tg=''.join(pred(model,TARGET,pos,layout)[0] for pos in range(10))
    tops=[''.join(pred(model,TARGET,pos,layout)[:8]) for pos in range(10)]
    return len(one),n,t1/n if n else 0,t5/n if n else 0,tg,tops

def main():
    rows=load(); print('rows',len(rows),'onepos',sum(sum(ch!='0' for ch in t)==1 for t,_ in rows))
    for layout in ['char','layer']: print(layout,eval(rows,layout))
if __name__=='__main__': main()
