#!/usr/bin/env python3
import urllib.parse, urllib.request, time, json
KEY='75eb8096abfe95266f21b56bff649d41'
C='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_.,;:?! '
OUT='/tmp/tm23_len_samples.jsonl'

def enc(text):
    url='http://api.trytodecrypt.com/encrypt?'+urllib.parse.urlencode({'key':KEY,'id':'23','text':text})
    return urllib.request.urlopen(url,timeout=10).read().decode().strip().upper()
with open(OUT,'a') as f:
    for n in range(1,51):
        for ch in ['0','a','A','!']:
            text=ch*n
            try: ct=enc(text)
            except Exception as e: ct='ERR '+repr(e)
            f.write(json.dumps({'text':text,'ct':ct})+'\n'); f.flush()
            time.sleep(0.03)
print(OUT)
