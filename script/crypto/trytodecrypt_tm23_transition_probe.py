#!/usr/bin/env python3
import json, math, os, urllib.parse, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

KEY = os.environ.get('TTD_API_KEY', 'YOUR_API_KEY_HERE')
C = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
CT20 = '8221E4F2173368D6B6B6E5050935D986A8C4CA764CF8A8C4B734E99807140B19DB691998095CC4E3D6C60D6E91'
CT23 = 'E3F59F001361B62958E551B9702F2C6B25F9E3FC350062295A1A20182041493C447BA0767A393A1F278DB14268565F51575C65212A8386494B383F7375676845472F30494C737A406890988B8D50577A835960476B6F73686E6367668B787A494C33357EA4555E191C18216A6F353A173E2026474A8A8C3F481416759D'

def enc(tid, text):
    url = 'http://api.trytodecrypt.com/encrypt?key=%s&id=%d&text=%s' % (KEY, tid, urllib.parse.quote(text))
    with urllib.request.urlopen(url, timeout=15) as r:
        s = r.read().decode().strip().upper()
    if not s or any(ch not in '0123456789ABCDEF' for ch in s):
        raise RuntimeError(s)
    return s

def inline(ct):
    return [(int(ct[i], 16), int(ct[i+1:i+3], 16), int(ct[i+3:i+5], 16)) for i in range(0, len(ct), 5)]

def front(ct):
    n = len(ct) // 5
    pref, data = ct[:n], ct[n:]
    return [(int(pref[i], 16), int(data[4*i:4*i+2], 16), int(data[4*i+2:4*i+4], 16)) for i in range(n)]

def val(tok, name):
    p, a, b = tok
    if name == 'p': return p
    if name == 'a': return a
    if name == 'b': return b
    if name == 'd71': return (b-a) % 71
    if name == 'd256': return (b-a) % 256
    if name == 'x': return a ^ b
    if name == 's': return (a+b) % 256
    raise KeyError(name)

def idx(pos, layer, order):
    return pos*5+layer if order == 'char' else layer*10+pos

def load_rows():
    rows = []
    seen = set()
    for path in ['/tmp/tm23_random10.jsonl','/tmp/tm23_relation_probe.jsonl','/tmp/tm23_repeated_allchars.jsonl','/tmp/tm23_probe_more.jsonl','/tmp/tm23_probe.jsonl']:
        p = Path(path)
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            try:
                j = json.loads(line)
            except Exception:
                continue
            t, ct = j.get('text',''), j.get('ct','').upper()
            if len(t) == 10 and len(ct) == 250 and (t, ct) not in seen:
                seen.add((t, ct)); rows.append((t, ct))
    return rows

def transition_features(ct, layout, order):
    toks = (front if layout == 'front' else inline)(ct)
    out = []
    for pos in range(10):
        fs = []
        for name in ['a','b','d71','x','s']:
            block = [val(toks[idx(pos, layer, order)], name) for layer in range(5)]
            fs.extend((block[i+1] - block[i]) % 71 for i in range(4))
            fs.extend((block[i+1] ^ block[i]) & 0xff for i in range(4))
            fs.append(block.index(min(block)))
            fs.append(block.index(max(block)))
        out.append(tuple(fs))
    return out

def eval_feature(rows, layout, order):
    randomish = [(t,ct) for t,ct in rows if len(set(t)) > 7]
    hold = randomish[:min(160, len(randomish))]
    top1 = top5 = n = 0
    for ht, hct in hold:
        tab = defaultdict(Counter); prior = Counter()
        for t, ct in rows:
            if t == ht and ct == hct:
                continue
            fs = transition_features(ct, layout, order)
            for pos, ch in enumerate(t):
                prior[ch] += 1
                tab[(pos, fs[pos])][ch] += 1
        hfs = transition_features(hct, layout, order)
        for pos, ch in enumerate(ht):
            cnt = tab[(pos, hfs[pos])]
            scores = {c: math.log(prior[c]+1) + math.log((cnt.get(c,0)+0.2)/(sum(cnt.values())+0.2*len(C))) for c in C}
            pred = [c for c,_ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:5]]
            n += 1; top1 += pred[0] == ch; top5 += ch in pred
    return top1/n if n else 0, top5/n if n else 0

def main():
    rows = load_rows()
    print('rows', len(rows), 'randomish', sum(len(set(t)) > 7 for t,_ in rows))
    for layout in ['inline','front']:
        for order in ['char','layer']:
            a,b = eval_feature(rows, layout, order)
            target = transition_features(CT23, layout, order)
            print(layout, order, 'top1=%.4f top5=%.4f' % (a,b), 'target_f0=', target[0][:12])

if __name__ == '__main__':
    main()
