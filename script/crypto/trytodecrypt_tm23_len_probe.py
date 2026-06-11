#!/usr/bin/env python3
import json, math
from collections import Counter,defaultdict
PATH='/tmp/tm23_len_samples.jsonl'

def parse(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
rows=[]
for line in open(PATH):
    j=json.loads(line); t=j['text']; ct=j['ct']
    if not ct.startswith('ERR') and len(ct)==25*len(t): rows.append((t,ct))
print('rows',len(rows))
# For repeated chars, compare per-layer token statistics as length changes. If state is position-only, same char positions/layers should align.
for ch in ['0','a','A','!']:
    rs=[(len(t),parse(ct)) for t,ct in rows if set(t)=={ch}]
    print('\nchar',ch,'samples',len(rs))
    for featname,fi in [('p',0),('a71',1),('b71',2),('d71',3)]:
        # value extractor
        def val(tok):
            p,a,b=tok
            return [p,a%71,b%71,(b-a)%71][fi]
        # repeated equality across same position modulo small periods
        best=[]
        for period in range(1,26):
            good=tot=0
            buckets=defaultdict(Counter)
            for n,toks in rs:
                for i,tok in enumerate(toks): buckets[i%period][val(tok)]+=1
            for n,toks in rs:
                for i,tok in enumerate(toks):
                    common=buckets[i%period].most_common(1)[0][0]
                    good+=val(tok)==common; tot+=1
            best.append((good/tot,period))
        print(featname, sorted(best, reverse=True)[:5])
