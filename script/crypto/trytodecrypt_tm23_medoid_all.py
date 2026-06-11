#!/usr/bin/env python3
import json, math, itertools, random
from pathlib import Path
from collections import Counter, defaultdict
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl','/tmp/tm23_len_samples.jsonl']

def toks(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def block(ct,pos,layout):
    ts=toks(ct)
    if layout=='char': ids=[pos*5+l for l in range(5)]
    else: ids=[l*10+pos for l in range(5)]
    return [ts[i] for i in ids]
def feats(ct,pos,layout,kind):
    b=block(ct,pos,layout)
    seq=[]
    for p,a,c in b:
        seq.extend([p,a,c,a%71,c%71,(c-a)%71,(a+c)%71,(a^c)%71,a>>4,a&15,c>>4,c&15])
    if kind=='local': return seq
    out=seq[:]
    for i,j in itertools.combinations(range(5),2):
        pi,ai,bi=b[i]; pj,aj,bj=b[j]
        valsi=[pi,ai%71,bi%71,(bi-ai)%71,(ai+bi)%71,(ai^bi)%71]
        valsj=[pj,aj%71,bj%71,(bj-aj)%71,(aj+bj)%71,(aj^bj)%71]
        for x,y in zip(valsi,valsj): out += [(y-x)%71,(x-y)%71,(x+y)%71,(x^y)%71]
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
            if len(t)==10 and len(ct)==250 and not ct.startswith('ERR') and (t,ct) not in seen:
                seen.add((t,ct)); rows.append((t,ct))
    return rows

def dist(a,b): return sum(x!=y for x,y in zip(a,b))/max(len(a),1)
def medoid(vs):
    if len(vs)==1: return vs[0]
    sample=vs if len(vs)<=40 else random.sample(vs,40)
    best=None
    for v in sample:
        s=sum(dist(v,u) for u in sample)
        if best is None or s<best[0]: best=(s,v)
    return best[1] if best is not None else []
def build(rows,layout,kind):
    groups=defaultdict(list)
    for t,ct in rows:
        for pos,ch in enumerate(t): groups[(pos,ch)].append(feats(ct,pos,layout,kind))
    return {k:medoid(v) for k,v in groups.items()}
def predict(model,ct,pos,layout,kind):
    v=feats(ct,pos,layout,kind); ranks=[]
    for ch in C:
        m=model.get((pos,ch))
        ranks.append((dist(v,m) if m else 999,ch))
    return [ch for _,ch in sorted(ranks)]
def eval_model(rows,layout,kind):
    random.seed(123); rows=rows[:]; random.shuffle(rows); split=int(len(rows)*0.8)
    train=rows[:split]; test=[r for r in rows[split:] if len(set(r[0]))>7]
    model=build(train,layout,kind); n=t1=t5=0
    for t,ct in test:
        for pos,ch in enumerate(t):
            p=predict(model,ct,pos,layout,kind); n+=1; t1+=p[0]==ch; t5+=ch in p[:5]
    tg=''.join(predict(model,TARGET,pos,layout,kind)[0] for pos in range(10))
    tops=[''.join(predict(model,TARGET,pos,layout,kind)[:8]) for pos in range(10)]
    return n,t1/n if n else 0,t5/n if n else 0,tg,tops

def main():
    rows=load(); print('rows',len(rows),'unique texts',len(set(t for t,_ in rows)))
    for layout in ['char','layer']:
        for kind in ['local','pair']:
            print(layout,kind,eval_model(rows,layout,kind))
if __name__=='__main__': main()
