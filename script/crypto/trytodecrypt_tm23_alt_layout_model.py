#!/usr/bin/env python3
import json, random, math
from pathlib import Path
from collections import Counter, defaultdict
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']

def toks(ct): return [int(ct[i:i+5],16) for i in range(0,len(ct),5)]
def vals(ct):
    ts=toks(ct); xs=[]
    for v in ts:
        p=(v>>16)&15; a=(v>>8)&255; b=v&255
        xs.append((p,a,b,a%71,b%71,(b-a)%71,(a+b)%71,(a^b)%71,v%71))
    return xs
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

def feature_set(ct, layout, pos, kind):
    xs=vals(ct); inds=[]
    for layer in range(5):
        inds.append(pos*5+layer if layout=='char' else layer*10+pos)
    base=[xs[i] for i in inds]
    out=[]
    if kind=='raw':
        for x in base: out += list(x)
    elif kind=='rel':
        for i in range(5):
            for j in range(i+1,5):
                for k in [3,4,5,6,7,8]:
                    out.append((base[j][k]-base[i][k])%71)
                    out.append((base[j][k]+base[i][k])%71)
                    out.append((base[j][k]^base[i][k])%71)
    elif kind=='seq':
        allv=[]
        for x in xs: allv.append(x[5])
        for i in inds:
            for off in [-11,-10,-9,-2,-1,0,1,2,9,10,11]:
                out.append(allv[(i+off)%50])
                out.append((allv[i]-allv[(i+off)%50])%71)
    return out

def learn(train, layout, kind, usepos=True):
    cnt=defaultdict(Counter); tot=Counter(); pcnt=Counter()
    for text,ct in train:
        for pos,ch in enumerate(text):
            keypos=pos if usepos else -1
            pcnt[(keypos,ch)]+=1
            fs=feature_set(ct,layout,pos,kind)
            for k,v in enumerate(fs): cnt[(keypos,ch,k)][v]+=1; tot[(keypos,ch,k)]+=1
    return cnt,tot,pcnt

def predict(model, ct, pos, layout, kind, usepos=True):
    cnt,tot,pcnt=model; keypos=pos if usepos else -1; fs=feature_set(ct,layout,pos,kind); ranks=[]
    for ch in C:
        sc=math.log(pcnt[(keypos,ch)]+1)
        for k,v in enumerate(fs): sc += math.log((cnt[(keypos,ch,k)][v]+0.1)/(tot[(keypos,ch,k)]+7.1))
        ranks.append((sc,ch))
    return [c for _,c in sorted(ranks, reverse=True)]

def eval_combo(rows, layout, kind, usepos):
    random.seed(99); r=rows[:]; random.shuffle(r)
    split=max(50,int(len(r)*0.8)); train=r[:split]; test=[x for x in r[split:] if len(set(x[0]))>7]
    model=learn(train,layout,kind,usepos)
    n=t1=t5=0
    for text,ct in test:
        for pos,ch in enumerate(text):
            p=predict(model,ct,pos,layout,kind,usepos)
            n+=1; t1+=p[0]==ch; t5+=ch in p[:5]
    tg=''.join(predict(model,TARGET,pos,layout,kind,usepos)[0] for pos in range(10))
    tops=[''.join(predict(model,TARGET,pos,layout,kind,usepos)[:8]) for pos in range(10)]
    return n,t1/n if n else 0,t5/n if n else 0,tg,tops

def main():
    rows=load(); print('rows',len(rows),'randomish',sum(len(set(t))>7 for t,_ in rows))
    for layout in ['char','layer']:
        for kind in ['raw','rel','seq']:
            for usepos in [True,False]:
                n,t1,t5,tg,tops=eval_combo(rows,layout,kind,usepos)
                print(layout,kind,'pos' if usepos else 'nopos','n',n,'top1 %.4f top5 %.4f'%(t1,t5),'target',tg,'tops',tops)
if __name__=='__main__': main()
