#!/usr/bin/env python3
import json, math, random
from pathlib import Path
from collections import defaultdict, Counter

C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']

def inline(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def front(ct):
    n=len(ct)//5; pref=ct[:n]; data=ct[n:]
    return [(int(pref[i],16),int(data[4*i:4*i+2],16),int(data[4*i+2:4*i+4],16)) for i in range(n)]
def idx(pos,layer,order): return pos*5+layer if order=='char' else layer*10+pos
def obs(ct,layout,order,pos):
    toks=(front if layout=='front' else inline)(ct)
    out=[]
    for layer in range(5):
        p,a,b=toks[idx(pos,layer,order)]
        vals=[p,a>>4,a&15,b>>4,b&15,a%71,b%71,(b-a)%71,(a^b)%71,(a+b)%71]
        out.extend(vals)
    # add pairwise d71/s71 relationships within block
    d=[out[layer*10+7] for layer in range(5)]
    s=[out[layer*10+9] for layer in range(5)]
    for i in range(5):
        for j in range(i+1,5):
            out.append((d[j]-d[i])%71); out.append((s[j]-s[i])%71); out.append((d[i]^d[j])%71)
    return out
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
def train_model(train,layout,order):
    # Gaussian-ish model over circular residues: use hist bins for every feature per pos,char
    cnt=defaultdict(Counter); prior=Counter(); totals=Counter()
    for text,ct in train:
        for pos,ch in enumerate(text):
            prior[(pos,ch)]+=1
            xs=obs(ct,layout,order,pos)
            for k,v in enumerate(xs):
                cnt[(pos,ch,k)][v]+=1; totals[(pos,ch,k)]+=1
    return cnt,prior,totals,len(obs(train[0][1],layout,order,0))
def score(cnt,prior,totals,nfeat,pos,xs,ch,alpha=0.2):
    sc=math.log(prior[(pos,ch)]+1)
    for k,v in enumerate(xs):
        # cardinality rough: prefix/nibble 16, mod features 71
        card=16 if k%10 in (0,1,2,3,4) and k<50 else 71
        sc+=math.log((cnt[(pos,ch,k)][v]+alpha)/(totals[(pos,ch,k)]+alpha*card))
    return sc
def eval_layout(rows,layout,order):
    random.seed(44)
    ids=list(range(len(rows))); random.shuffle(ids)
    test=set(ids[:min(350,len(ids)//5)])
    train=[r for i,r in enumerate(rows) if i not in test]
    tests=[r for i,r in enumerate(rows) if i in test and len(set(r[0]))>7]
    cnt,prior,totals,nfeat=train_model(train,layout,order)
    top1=top5=n=0
    for text,ct in tests:
        for pos,ch in enumerate(text):
            xs=obs(ct,layout,order,pos)
            ranks=sorted(((score(cnt,prior,totals,nfeat,pos,xs,c),c) for c in C), reverse=True)
            pred=[c for _,c in ranks[:5]]
            n+=1; top1+=pred[0]==ch; top5+=ch in pred
    return top1/n if n else 0, top5/n if n else 0, len(tests)
def target(rows,layout,order):
    cnt,prior,totals,nfeat=train_model(rows,layout,order)
    out=''; tops=[]
    for pos in range(10):
        xs=obs(TARGET,layout,order,pos)
        ranks=sorted(((score(cnt,prior,totals,nfeat,pos,xs,c),c) for c in C), reverse=True)[:10]
        out+=ranks[0][1]; tops.append(''.join(c for _,c in ranks))
    return out,tops
def main():
    rows=load(); print('rows',len(rows), 'randomish',sum(len(set(t))>7 for t,_ in rows), flush=True)
    for layout in ['inline','front']:
        for order in ['char','layer']:
            r=eval_layout(rows,layout,order)
            print(layout,order,'top1=%.4f top5=%.4f tests=%d'%r,'target',target(rows,layout,order), flush=True)
if __name__=='__main__': main()
