#!/usr/bin/env python3
import itertools, json, math, statistics, sys, time, urllib.parse, urllib.request
from collections import defaultdict, Counter

# WARNING: API key was hardcoded here. Use env var instead.
import os
KEY=os.environ.get('TTD_API_KEY', 'YOUR_API_KEY_HERE')
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
CT20='8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91'
CT23='E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'

def enc(id, text):
    url='http://api.trytodecrypt.com/encrypt?key=%s&id=%d&text=%s' % (KEY,id,urllib.parse.quote(text))
    with urllib.request.urlopen(url, timeout=15) as r:
        s=r.read().decode().strip().upper()
    if not all(ch in '0123456789ABCDEF' for ch in s):
        raise RuntimeError(s)
    return s

def groups_inline(ct, step=5):
    return [(int(ct[i],16), int(ct[i+1:i+3],16), int(ct[i+3:i+5],16), ct[i:i+5]) for i in range(0,len(ct),step)]

def groups_front(ct):
    n=len(ct)//5
    pref=ct[:n]
    data=ct[n:]
    return [(int(pref[i],16), int(data[4*i:4*i+2],16), int(data[4*i+2:4*i+4],16), pref[i]+data[4*i:4*i+4]) for i in range(n)]

def vals_from_group(g):
    p,b1,b2,_=g
    return {
        'p':p,'b1':b1,'b2':b2,
        'd21':(b2-b1)%256,'d12':(b1-b2)%256,
        'd21m':(b2-b1)%71,'d12m':(b1-b2)%71,
        'x':b1^b2,'xp':b1^b2^p,
        's':(b1+b2)%256,'sp':(b1+b2+p)%256,
        'b1p':(b1-p)%256,'b2p':(b2-p)%256,
        'b1mp':(b1-p)%71,'b2mp':(b2-p)%71,
    }

def print_sample(id,texts):
    print('== sample id',id)
    for t in texts:
        xs=[]
        for _ in range(3):
            s=enc(id,t)
            xs.append(s)
            time.sleep(0.05)
        print(repr(t), [len(x) for x in xs], xs)

def analyze20():
    texts=['0'*18,'1'*18,'a'*18,'A'*18,'01'*9, C[:18]]
    samples={t:[enc(20,t) for _ in range(4)] for t in texts}
    print('== lengths20')
    for t,ss in samples.items(): print(repr(t), [len(s) for s in ss])
    for layout_name, layout in [('inline',groups_inline),('front',groups_front)]:
        print('\n== layout',layout_name)
        # compare within all-zero samples: which expressions are stable across positions/samples?
        for expr in ['p','b1','b2','d21m','d12m','x','xp','b1mp','b2mp']:
            arr=[]
            for s in samples['0'*18]:
                arr.append([vals_from_group(g)[expr] for g in layout(s)])
            # per position unique count across samples
            uniq=[len({row[i] for row in arr}) for i in range(18)]
            print(expr, 'uniq_across_same_plain_by_pos', uniq[:18], 'firstrow', arr[0][:18])
        # compare char deltas in same sample index
        base=samples['0'*18][0]
        for t in ['1'*18,'a'*18,'A'*18]:
            print('-- delta target',repr(t))
            for expr in ['b1','b2','d21m','d12m','x','xp','b1mp','b2mp']:
                a=[vals_from_group(g)[expr] for g in layout(base)]
                b=[vals_from_group(g)[expr] for g in layout(samples[t][0])]
                print(expr, [(b[i]-a[i])%71 for i in range(18)])
    return samples

def analyze23():
    texts=['0'*10,'1'*10,'a'*10,C[:10]]
    samples={t:[enc(23,t) for _ in range(3)] for t in texts}
    print('\n== lengths23')
    for t,ss in samples.items(): print(repr(t), [len(s) for s in ss])
    s=samples['0'*10][0]
    print('ct23 target len',len(CT23),'sample len',len(s))
    # 25-per-char -> 5 subgroups inline
    gs=groups_inline(s,5)
    print('first 20 5hex groups for 0*10:', [g[3] for g in gs[:20]])
    # front half pairing 25 5hex groups + 25 groups
    first=groups_inline(s[:125],5); second=groups_inline(s[125:],5)
    print('split group counts',len(first),len(second))
    print('first pairs', [(first[i][3],second[i][3], (second[i][2]-first[i][2])%71, (first[i][2]-second[i][2])%71) for i in range(10)])
    return samples

if __name__=='__main__':
    print_sample(20,['0','00','000','a','aa','0'*18])
    s20=analyze20()
    print_sample(23,['0','00','000','a','aa','0'*10])
    s23=analyze23()
