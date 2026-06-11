#!/usr/bin/env python3
import urllib.parse, urllib.request, time, json, random
KEY='75eb8096abfe95266f21b56bff649d41'
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
OUT='/tmp/tm23_diff_random_pairs.jsonl'

def enc(text):
    url='http://api.trytodecrypt.com/encrypt?'+urllib.parse.urlencode({'key':KEY,'id':'23','text':text})
    return urllib.request.urlopen(url,timeout=10).read().decode().strip().upper()
random.seed(20260527)
base='0'*10
with open(OUT,'a') as f:
    # controlled: each pos each char subset and some full charset single substitutions
    jobs=[]
    for pos in range(10):
        for ch in C:
            if ch!='0': jobs.append(base[:pos]+ch+base[pos+1:])
    random.shuffle(jobs)
    for text in jobs[:240]:
        for _ in range(2):
            try: ct=enc(text)
            except Exception as e: ct='ERR '+repr(e)
            f.write(json.dumps({'text':text,'ct':ct})+'\n'); f.flush(); time.sleep(0.04)
print(OUT)
