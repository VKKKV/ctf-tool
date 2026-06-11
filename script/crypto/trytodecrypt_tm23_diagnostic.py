#!/usr/bin/env python3
# Diagnostic: TryToDecrypt Too Much Text23 randomized oracle analysis.
# No argparse; edit constants or run directly with uv run.
import json, math, random
from pathlib import Path
from collections import Counter, defaultdict
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl']

def inline(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16),ct[i:i+5]) for i in range(0,len(ct),5)]
def front(ct):
    n=len(ct)//5; pref=ct[:n]; data=ct[n:]
    return [(int(pref[i],16),int(data[4*i:4*i+2],16),int(data[4*i+2:4*i+4],16),pref[i]+data[4*i:4*i+4]) for i in range(n)]
def fd(tok):
    p,a,b,g=tok
    return {'p':p,'d71':(b-a)%71,'d256':(b-a)%256,'xor':a^b,'sum71':(a+b)%71,'ah':a>>4,'al':a&15,'bh':b>>4,'bl':b&15,'hi':(a>>4,b>>4),'lo':(a&15,b&15),'p_d71':(p,(b-a)%71)}
def idx(pos,layer,gmode): return pos*5+layer if gmode=='char-major' else layer*10+pos

def load():
    out=[]; seen=set()
    for path in PATHS:
        p=Path(path)
        if not p.exists(): continue
        for line in p.read_text().splitlines():
            try:j=json.loads(line)
            except Exception: continue
            text=j.get('text',''); ct=j.get('ct','').upper()
            if len(text)==10 and len(ct)==250 and (text,ct) not in seen:
                seen.add((text,ct)); out.append((text,ct))
    return out

def top_stability(rows):
    print('== repeated-char stability')
    for lname,parse in [('inline',inline),('front',front)]:
        for gmode in ['char-major','layer-major']:
            reps=[(t,parse(ct)) for t,ct in rows if len(set(t))==1]
            print(lname,gmode,'reps',len(reps))
            for feat in ['d71','p','hi','lo','p_d71']:
                ratios=[]
                for ch in C:
                    arr=[toks for t,toks in reps if t[0]==ch]
                    if len(arr)<2: continue
                    for pos in range(10):
                        for layer in range(5):
                            vals=[fd(toks[idx(pos,layer,gmode)])[feat] for toks in arr]
                            c=Counter(vals); ratios.append(c.most_common(1)[0][1]/len(vals))
                print(' ',feat,'avg_top',round(sum(ratios)/len(ratios),3),'perfect',sum(x==1 for x in ratios),'/',len(ratios))

def validate(rows, layout, gmode, feats=('d71',), bypos=False, max_tests=120):
    parse=front if layout=='front' else inline
    prepared=[]
    for text,ct in rows:
        toks=parse(ct); arr=[]
        for pos in range(10):
            arr.append([tuple(fd(toks[idx(pos,layer,gmode)])[f] for f in feats) for layer in range(5)])
        prepared.append((text,arr))
    tests=[i for i,(t,a) in enumerate(prepared) if len(set(t))>7]
    random.seed(23); random.shuffle(tests); tests=tests[:max_tests]
    n=t1=t5=0
    for hold in tests:
        table=defaultdict(Counter); prior=Counter()
        for ri,(text,arr) in enumerate(prepared):
            if ri==hold: continue
            for pos,ch in enumerate(text):
                prior[ch]+=1
                for layer,val in enumerate(arr[pos]): table[(pos if bypos else -1,layer,val)][ch]+=1
        text,arr=prepared[hold]
        for pos,ch in enumerate(text):
            scores={c:math.log(prior[c]+1) for c in C}
            for layer,val in enumerate(arr[pos]):
                cnt=table[(pos if bypos else -1,layer,val)]; tot=sum(cnt.values())
                for c in C: scores[c]+=math.log((cnt[c]+0.5)/(tot+0.5*len(C)))
            pred=[c for c,s in sorted(scores.items(),key=lambda kv:kv[1],reverse=True)[:5]]
            n+=1; t1+=pred[0]==ch; t5+=ch in pred
    return t1/n if n else 0,t5/n if n else 0,n

def main():
    rows=load(); print('rows',len(rows),'randomish',sum(1 for t,_ in rows if len(set(t))>7), flush=True)
    top_stability(rows)
    print('\n== held-out classifiers', flush=True)
    # Representative subset only; full Cartesian scan is slow and has already shown random-baseline accuracy.
    tests=[
        ('inline','char-major',('d71',)),
        ('inline','char-major',('p_d71',)),
        ('inline','layer-major',('d71','hi')),
        ('front','layer-major',('d71',)),
        ('front','layer-major',('p_d71',)),
        ('front','layer-major',('lo',)),
        ('front','char-major',('d71','hi')),
    ]
    for layout,gmode,feats in tests:
        v=validate(rows,layout,gmode,feats,False,max_tests=40)
        vp=validate(rows,layout,gmode,feats,True,max_tests=40)
        print(layout,gmode,feats,'val',tuple(round(x,4) if isinstance(x,float) else x for x in v),'bypos',tuple(round(x,4) if isinstance(x,float) else x for x in vp), flush=True)
if __name__=='__main__': main()
