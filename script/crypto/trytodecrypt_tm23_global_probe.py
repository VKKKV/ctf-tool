#!/usr/bin/env python3
import json, math, random
from pathlib import Path
from collections import Counter, defaultdict
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
TARGET='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'
PATHS=['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']
def inline(ct): return [(int(ct[i],16),int(ct[i+1:i+3],16),int(ct[i+3:i+5],16)) for i in range(0,len(ct),5)]
def front(ct):
    n=len(ct)//5; pref=ct[:n]; data=ct[n:]
    return [(int(pref[i],16),int(data[4*i:4*i+2],16),int(data[4*i+2:4*i+4],16)) for i in range(n)]
def idx(pos,layer,mode): return pos*5+layer if mode=='char' else layer*10+pos
def rankvals(vals):
    order=sorted(range(len(vals)), key=lambda i:(vals[i],i)); r=[0]*len(vals)
    for k,i in enumerate(order): r[i]=k
    return r
def load():
    rows=[]; seen=set()
    for path in PATHS:
        p=Path(path)
        if not p.exists(): continue
        for line in p.read_text().splitlines():
            try:j=json.loads(line)
            except: continue
            t=j.get('text',''); ct=j.get('ct','').upper()
            if len(t)==10 and len(ct)==250 and (t,ct) not in seen:
                seen.add((t,ct)); rows.append((t,ct))
    randomish=[r for r in rows if len(set(r[0]))>7]
    repeated=[r for r in rows if len(set(r[0]))==1]
    random.seed(3)
    # enough for signal test, fast enough
    return randomish[:250] + repeated[:355]
def make_features(toks, mode):
    arrays={
      'a':[t[1] for t in toks], 'b':[t[2] for t in toks], 'd71':[(t[2]-t[1])%71 for t in toks],
      'd256':[(t[2]-t[1])%256 for t in toks], 'xor':[t[1]^t[2] for t in toks], 'sum256':[(t[1]+t[2])%256 for t in toks],
    }
    ranks={k:rankvals(v) for k,v in arrays.items()}
    out=[]
    for pos in range(10):
      row=[]
      for layer in range(5):
        i=idx(pos,layer,mode); feat={}
        for name,arr in arrays.items():
          r=ranks[name][i]
          feat[name+'_q']=min(9, r//5)
          feat[name+'_med']=int(r>=25)
          order=sorted(range(50), key=lambda j:(arr[j],j))
          feat[name+'_prev']=order[r-1]//5 if r>0 else -1
          feat[name+'_next']=order[r+1]//5 if r<49 else -1
        for name,arr in arrays.items():
          block=[arr[idx(pos,l,mode)] for l in range(5)]
          feat[name+'_minpos']=block.index(min(block)); feat[name+'_maxpos']=block.index(max(block))
        row.append(feat)
      out.append(row)
    return out
def eval(rows, layout, mode, fs, bypos):
    parser=front if layout=='front' else inline
    parsed=[(t,make_features(parser(ct),mode)) for t,ct in rows]
    tests=[i for i,(t,_) in enumerate(parsed) if len(set(t))>7]
    random.seed(4); random.shuffle(tests); tests=tests[:120]
    top1=top5=n=0
    for hold in tests:
      tab=defaultdict(Counter); prior=Counter()
      for ri,(text,featrows) in enumerate(parsed):
        if ri==hold: continue
        for pos,ch in enumerate(text):
          prior[ch]+=1
          for layer in range(5):
            key=(pos if bypos else -1,layer,tuple(featrows[pos][layer][k] for k in fs)); tab[key][ch]+=1
      text,featrows=parsed[hold]
      for pos,ch in enumerate(text):
        scores={c:math.log(prior[c]+1) for c in C}
        for layer in range(5):
          key=(pos if bypos else -1,layer,tuple(featrows[pos][layer][k] for k in fs)); cnt=tab.get(key,{}); tot=sum(cnt.values())
          for c in C: scores[c]+=math.log((cnt.get(c,0)+0.5)/(tot+0.5*len(C)))
        pred=[c for c,_ in sorted(scores.items(), key=lambda kv:kv[1], reverse=True)[:5]]
        n+=1; top1+=pred[0]==ch; top5+=ch in pred
    return top1/n,top5/n,n
def target(rows, layout, mode, fs, bypos):
    parser=front if layout=='front' else inline
    parsed=[(t,make_features(parser(ct),mode)) for t,ct in rows]
    tab=defaultdict(Counter); prior=Counter()
    for text,featrows in parsed:
      for pos,ch in enumerate(text):
        prior[ch]+=1
        for layer in range(5):
          key=(pos if bypos else -1,layer,tuple(featrows[pos][layer][k] for k in fs)); tab[key][ch]+=1
    tf=make_features(parser(TARGET),mode); out=''; tops=[]
    for pos in range(10):
      scores={c:math.log(prior[c]+1) for c in C}
      for layer in range(5):
        key=(pos if bypos else -1,layer,tuple(tf[pos][layer][k] for k in fs)); cnt=tab.get(key,{}); tot=sum(cnt.values())
        for c in C: scores[c]+=math.log((cnt.get(c,0)+0.5)/(tot+0.5*len(C)))
      top=sorted(scores.items(), key=lambda kv:kv[1], reverse=True)[:5]
      out+=top[0][0]; tops.append(''.join(c for c,_ in top))
    return out,tops
rows=load(); print('rows_used',len(rows),'randomish',sum(len(set(t))>7 for t,_ in rows),'repeated',sum(len(set(t))==1 for t,_ in rows), flush=True)
# same plaintext order stability
for layout,parser in [('inline',inline),('front',front)]:
  by=defaultdict(list)
  for t,ct in rows: by[t].append(ct)
  for name,fn in [('a',lambda x:x[1]),('b',lambda x:x[2]),('d71',lambda x:(x[2]-x[1])%71),('xor',lambda x:x[1]^x[2])]:
    vals=[]
    for t,cts in by.items():
      if len(cts)<3: continue
      seq=[]
      for ct in cts[:8]:
        arr=[fn(tok) for tok in parser(ct)]; seq.append([r//5 for r in rankvals(arr)])
      eq=tot=0
      for i in range(50):
        c=Counter(s[i] for s in seq); eq+=c.most_common(1)[0][1]; tot+=len(seq)
      vals.append(eq/tot)
    print('rankbin_stability',layout,name,round(sum(vals)/len(vals),3) if vals else 'NA', flush=True)
sets=[('a_q','b_q','d71_q'),('a_med','b_med','d71_med','xor_med'),('a_prev','a_next','b_prev','b_next'),('d71_prev','d71_next','xor_prev','xor_next'),('a_minpos','a_maxpos','b_minpos','b_maxpos','d71_minpos','d71_maxpos')]
res=[]
for layout in ['inline','front']:
  for mode in ['char','layer']:
    for fs in sets:
      for bypos in [False,True]:
        r=eval(rows,layout,mode,fs,bypos); res.append((*r,layout,mode,fs,bypos)); print('VAL %.4f %.4f n=%d %s %s %s bypos=%s'%((*r,layout,mode,fs,bypos)), flush=True)
print('BEST')
for r in sorted(res, reverse=True)[:12]: print(r)
print('TARGET')
for r in sorted(res, reverse=True)[:8]:
  _,_,_,layout,mode,fs,bypos=r
  print(layout,mode,fs,bypos,target(rows,layout,mode,fs,bypos))
