#!/usr/bin/env python3
import json, math, random
from pathlib import Path
from collections import Counter, defaultdict

C = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET = 'E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS = ['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']

def inline(ct): return [(int(ct[i],16), int(ct[i+1:i+3],16), int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def front(ct):
    n=len(ct)//5; pref=ct[:n]; data=ct[n:]
    return [(int(pref[i],16), int(data[4*i:4*i+2],16), int(data[4*i+2:4*i+4],16)) for i in range(n)]
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
    random.seed(7)
    randomish=[r for r in rows if len(set(r[0]))>7]
    repeated=[r for r in rows if len(set(r[0]))==1]
    random.shuffle(randomish); random.shuffle(repeated)
    return randomish[:500]+repeated[:500]
def idx(pos,layer,order): return pos*5+layer if order=='char' else layer*10+pos
def arrays(toks,order):
    vals=[]
    for pos in range(10):
        row=[]
        for layer in range(5):
            p,a,b=toks[idx(pos,layer,order)]
            row.append({'p':p,'a':a,'b':b,'a71':a%71,'b71':b%71,'d71':(b-a)%71,'x71':(a^b)%71,'s71':(a+b)%71,'ah':a>>4,'al':a&15,'bh':b>>4,'bl':b&15})
        vals.append(row)
    return vals
def specs():
    out=[]
    for l in range(5):
      for n in ['p','a71','b71','d71','x71','s71','ah','al','bh','bl']:
        out.append(('single',l,n))
    for l1 in range(5):
      for l2 in range(l1+1,5):
        for n in ['a71','b71','d71','x71','s71']:
          for op in ['sub','rsub','add','xor']:
            out.append(('pair',l1,l2,n,op))
    for l in range(5):
      for n in ['a71','b71','d71','x71','s71']:
        for op in ['sub','rsub','add','xor']:
          out.append(('adj',l,n,op))
    return out
def feat(vals,pos,sp):
    if sp[0]=='single': return vals[pos][sp[1]][sp[2]]
    if sp[0]=='pair':
        _,l1,l2,n,op=sp; x=vals[pos][l1][n]; y=vals[pos][l2][n]
    else:
        _,l1,n,op=sp
        if pos==9: return None
        x=vals[pos][l1][n]; y=vals[pos+1][l1][n]
    if op=='sub': return (y-x)%71
    if op=='rsub': return (x-y)%71
    if op=='add': return (x+y)%71
    return (x^y)%71
def eval_all(parsed, splist):
    ids=[i for i,(t,_) in enumerate(parsed) if len(set(t))>7]
    random.seed(11); random.shuffle(ids); test=set(ids[:120])
    res=[]
    for sp in splist:
        tab=defaultdict(Counter); prior=Counter()
        for ri,(text,vals) in enumerate(parsed):
            if ri in test: continue
            for pos,ch in enumerate(text):
                v=feat(vals,pos,sp)
                if v is not None:
                    tab[(pos,v)][ch]+=1; prior[ch]+=1
        top1=top5=n=0
        for ri,(text,vals) in enumerate(parsed):
            if ri not in test: continue
            for pos,ch in enumerate(text):
                v=feat(vals,pos,sp)
                if v is None: continue
                cnt=tab.get((pos,v),{}); tot=sum(cnt.values())
                scores={c:math.log(prior[c]+1)+math.log((cnt.get(c,0)+0.5)/(tot+0.5*71)) for c in C}
                pred=[c for c,_ in sorted(scores.items(), key=lambda kv:kv[1], reverse=True)[:5]]
                n+=1; top1+=pred[0]==ch; top5+=ch in pred
        res.append((top1/n if n else 0, top5/n if n else 0, sp))
    return sorted(res, reverse=True)
def target_guess(rows,layout,order,sels):
    parser=front if layout=='front' else inline
    parsed=[(t,arrays(parser(ct),order)) for t,ct in rows]
    tv=arrays(parser(TARGET),order)
    tab=defaultdict(Counter); prior=Counter()
    for text,vals in parsed:
        for pos,ch in enumerate(text):
            prior[ch]+=1
            for si,sp in enumerate(sels):
                v=feat(vals,pos,sp)
                if v is not None: tab[(si,pos,v)][ch]+=1
    out=''; tops=[]
    for pos in range(10):
        scores={c:math.log(prior[c]+1) for c in C}
        for si,sp in enumerate(sels):
            v=feat(tv,pos,sp); cnt=tab.get((si,pos,v),{}); tot=sum(cnt.values())
            for c in C: scores[c]+=math.log((cnt.get(c,0)+0.5)/(tot+0.5*71))
        top=sorted(scores.items(), key=lambda kv:kv[1], reverse=True)[:8]
        out+=top[0][0]; tops.append(''.join(c for c,_ in top))
    return out,tops
def main():
    rows=load(); splist=specs(); print('rows',len(rows),'specs',len(splist),flush=True)
    for layout in ['inline','front']:
      parser=front if layout=='front' else inline
      for order in ['char','layer']:
        parsed=[(t,arrays(parser(ct),order)) for t,ct in rows]
        res=eval_all(parsed,splist)
        print('\n',layout,order,'BEST',flush=True)
        for a,b,sp in res[:15]: print('%.4f %.4f %r'%(a,b,sp),flush=True)
        sels=[sp for _,_,sp in res[:10]]
        print('TARGET',target_guess(rows,layout,order,sels),flush=True)
if __name__=='__main__': main()
