import base64

tokens = {
  "self-test (line 12)": "ORSXG5A=",
  "snapshot1 (line 16)": "QMFYHA3BPJZWKYLOM5XGC3TPNRSWM===",
  "encrypted1 (line 22)": "ONSWG4TFORQXIIDBNZSCAZLPON2XGYLSMUQHG43JMRPWK3TFFQQCK2LFNYQQ====",
  "encrypted2 (line 39)": "NRQWKZLBNZXWY3LTNFSW45DFMVZWKZLSOR3WKIDPMQQHK3TLMRSA4TBGRSAX====",
  "keyrot1 (line 61)": "ONSWG4TFORQXIIDBNZSCAZDPNR2WM===",
  "snapshot2 (line 68)": "PFZWK3LFNFXGO3TPNZQWY2LHNFSWY===",
  "encrypted3 (line 77)": "PFZWK3TFONRWGZLOMFQWC5LBNZ2WY4TFORXXIIDJNZSCA4DPOJSS2ZLFNRSA====",
  "keyrot2 (line 91)": "NRQWKZLBNZXWY3LTNFSW45DFMFZWKZM=",
  "snapshot3 (line 95)": "MJQXG5LFNFXGO2TPNZQWY3LHNFSWY===",
  "encrypted4 (line 108)": "YX2THEVPQ4LNRIMFCHIKFUCBRL2IGF6567KEFW7Q2AK5XIUEJXI7FUCE33VQ====",
}

for name, tok in tokens.items():
  try:
      decoded = base64.b32decode(tok)
      try:
          text = decoded.decode('utf-8')
          print(f"{name}: {text}")
      except:
          print(f"{name}: (binary) {decoded.hex()} | raw: {decoded}")
  except Exception as e:
      print(f"{name}: DECODE ERROR: {e}")

