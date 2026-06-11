#!/usr/bin/env python3
import json, math, random
from pathlib import Path
from collections import Counter, defaultdict

C = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET = 'E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS = ['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']

def inline(ct):
    return [(int(ct[i],16), int(ct[i+1:i+3],16), int(ct[i+3:i+5],16)) for i in range(0, len(ct), 5)]

def front(ct):
    n = len(ct)//5; pref, data = ct[:n], ct[n:]
    return [(int(pref[i],16), int(data[4*i:4*i+2],16), int(data[4*i+2:4*i+4],16)) for i in range(n)]

def load():
    rows=[]; seen=set()
    for path in PATHS:
        p=Path(path)
        if not p.exists(): continue
        for line in p.read_text().splitlines():
            try: j=json.loads(line)
            except Exception: continue
            t=j.get('text',''); ct=j.get('ct','').upper()
            if len(t)==10 and len(ct)==250 and (t,ct) not in seen:
                seen.add((t,ct)); rows.append((t,ct))
    return rows

def idx(pos, layer, order):
    return pos*5+layer if order=='char' else layer*10+pos

def base(tok, name):
    p,a,b=tok
    if name=='p': return p
    if name=='a': return a
    if name=='b': return b
    if name=='a71': return a%71
    if name=='b71': return b%71
    if name=='d71': return (b-a)%71
    if name=='d256': return (b-a)%256
    if name=='x': return a^b
    if name=='x71': return (a^b)%71
    if name=='s71': return (a+b)%71
    if name=='ah': return a>>4
    if name=='al': return a&15
    if name=='bh': return b>>4
    if name=='bl': return b&15
    raise KeyError(name)

def feature(toks, pos, spec, order):
    kind=spec[0]
    if kind=='single':
        _, layer, name = spec
        return base(toks[idx(pos,layer,order)], name)
    if kind=='pair':
        _, layer1, layer2, name, op, mod = spec
        v1=base(toks[idx(pos,layer1,order)], name); v2=base(toks[idx(pos,layer2,order)], name)
    elif kind=='adjpos':
        _, layer, name, op, mod = spec
        if pos==9: return None
        v1=base(toks[idx(pos,layer,order)], name); v2=base(toks[idx(pos+1,layer,order)], name)
    elif kind=='allpos':
        _, layer, delta, name, op, mod = spec
        q=(pos+delta)%10
        v1=base(toks[idx(pos,layer,order)], name); v2=base(toks[idx(q,layer,order)], name)
    else:
        raise KeyError(kind)
    if op=='sub': return (v2-v1)%mod
    if op=='rsub': return (v1-v2)%mod
    if op=='add': return (v1+v2)%mod
    if op=='xor': return (v1^v2)%mod
    raise KeyError(op)

def specs():
    names=['p','a','b','a71','b71','d71','x','x71','s71','ah','al','bh','bl']
    out=[]
    for l in range(5):
        for n in names:
            out.append(('single',l,n))
    for l1 in range(5):
        for l2 in range(5):
            if l1==l2: continue
            for n in ['a','b','a71','b71','d71','x','x71','s71']:
                for op in ['sub','rsub','add','xor']:
                    for mod in ([71] if n.endswith('71') or n in ('d71','s71','x71') else [71,256]):
                        out.append(('pair',l1,l2,n,op,mod))
    for l in range(5):
        for n in ['a','b','a71','b71','d71','x','x71','s71']:
            for op in ['sub','rsub','add','xor']:
                for mod in ([71] if n.endswith('71') or n in ('d71','s71','x71') else [71,256]):
                    out.append(('adjpos',l,n,op,mod))
    for l in range(5):
        for delta in range(1,10):
            for n in ['d71','a71','b71','x71','s71']:
                for op in ['sub','rsub','add','xor']:
                    out.append(('allpos',l,delta,n,op,71))
    return out

def eval_spec(parsed, spec):
    random.seed(11)
    ids=[i for i,(t,_,_) in enumerate(parsed) if len(set(t))>7]
    random.shuffle(ids); test=set(ids[:180])
    train=[r for i,r in enumerate(parsed) if i not in test]
    tests=[r for i,r in enumerate(parsed) if i in test]
    tab=defaultdict(Counter); prior=Counter()
    for text,toks,order in train:
        for pos,ch in enumerate(text):
            v=feature(toks,pos,spec,order)
            if v is None: continue
            tab[(pos,v)][ch]+=1; prior[ch]+=1
    top1=top5=n=0
    for text,toks,order in tests:
        for pos,ch in enumerate(text):
            v=feature(toks,pos,spec,order)
            if v is None: continue
            cnt=tab.get((pos,v),{})
            scores={c:math.log(prior[c]+1)+math.log((cnt.get(c,0)+0.3)/(sum(cnt.values())+0.3*len(C))) for c in C}
            pred=[c for c,_ in sorted(scores.items(), key=lambda kv:kv[1], reverse=True)[:5]]
            n+=1; top1+=pred[0]==ch; top5+=ch in pred
    return (top1/n if n else 0, top5/n if n else 0, n)

def target_guess(rows, layout, order, specs_sel):
    parser=front if layout=='front' else inline
    parsed=[(t,parser(ct),order) for t,ct in rows]
    tab=defaultdict(Counter); prior=Counter()
    for text,toks,_ in parsed:
        for pos,ch in enumerate(text):
            prior[ch]+=1
            for si,sp in enumerate(specs_sel):
                v=feature(toks,pos,sp,order)
                if v is not None: tab[(si,pos,v)][ch]+=1
    tt=parser(TARGET)
    out=''; tops=[]
    for pos in range(10):
        scores={c:math.log(prior[c]+1) for c in C}
        for si,sp in enumerate(specs_sel):
            v=feature(tt,pos,sp,order)
            cnt=tab.get((si,pos,v),{}); tot=sum(cnt.values())
            for c in C: scores[c]+=math.log((cnt.get(c,0)+0.3)/(tot+0.3*len(C)))
        top=sorted(scores.items(), key=lambda kv:kv[1], reverse=True)[:8]
        out+=top[0][0]; tops.append(''.join(c for c,_ in top))
    return out,tops

def main():
    rows=load(); sp=specs()
    print('rows',len(rows),'specs',len(sp))
    allres=[]
    for layout in ['inline','front']:
        parser=front if layout=='front' else inline
        for order in ['char','layer']:
            parsed=[(t,parser(ct),order) for t,ct in rows]
            for k,s in enumerate(sp):
                r=eval_spec(parsed,s)
                allres.append((r[0],r[1],layout,order,s))
            print('done',layout,order)
    best=sorted(allres, reverse=True)[:30]
    print('BEST')
    for r in best:
        print('%.4f %.4f %s %s %r'%r)
    print('TARGET by top sets')
    for layout in ['inline','front']:
        for order in ['char','layer']:
            sels=[s for _,_,la,ordr,s in sorted([r for r in allres if r[2]==layout and r[3]==order], reverse=True)[:12]]
            print(layout,order,target_guess(rows,layout,order,sels))

if __name__=='__main__':
    main()
