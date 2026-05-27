#!/usr/bin/env python3
"""
Solve WeChall Training: Crypto - Digraphs
Using frequency analysis and pattern matching
"""
from collections import Counter
import re

ciphertext = "wbfamljibjxgxqjqqexgxqonfamlwaix eifajq pzijtvbjaecoxqijpz xqioonwa lzijwawaxgjiij wajqtvtvijwawaxhjqqeqeaeix ypxgwa mlfaxq xqfafa pzonxhxhontvjqqexq ijonxqioijbjla oyxgwa onxqym ypijqeqela jifafapz tefaoiix uzmlxqijbj xqioonwa qfijaeoyfabjpz xgwa wafaqejqxqonfamlxr xhxgmloitvxhonxhlzjijimlix"

# Parse into digraphs preserving spaces
def tokenize(text):
    tokens = []
    i = 0
    while i < len(text):
        if text[i] == ' ':
            tokens.append(' ')
            i += 1
        else:
            tokens.append(text[i:i+2])
            i += 2
    return tokens

tokens = tokenize(ciphertext)

# Count digraph frequencies
freq = Counter(t for t in tokens if t != ' ')
sorted_freq = freq.most_common()
print("Digraph frequencies (top 30):")
for d, c in sorted_freq:
    print(f"  {d}: {c}")

# Build frequency-based mapping
# English letter frequency order: e,t,a,o,i,n,s,h,r,d,l,c,u,m,w,f,g,y,p,b,v,k,j,x,q,z
# But the actual text might use different distribution

# Let's try to guess words using known patterns
# The last word "xhxgmloitvxhonxhlzjijimlix" is 13 digraphs (13 letters)
# Common endings: "successfully", "challenging", "congratulation", etc.

# Let me print all words with their digraph sequences
words_ct = ciphertext.split(' ')
print("\nWords by length (plaintext letters):")
for w in words_ct:
    print(f"  {w}: {len(w)//2} letters, digraphs: {[w[i:i+2] for i in range(0, len(w), 2)]}")

# Let me try to find which digraph appears as the first letter of many words
# This could be 't', 'a', 'o', 'i', 's', 'w', etc.
first_digraphs = Counter()
last_digraphs = Counter()
for w in words_ct:
    if len(w) >= 2:
        first_digraphs[w[0:2]] += 1
        last_digraphs[w[-2:]] += 1

print("\nMost common first digraphs of words:")
for d, c in first_digraphs.most_common(10):
    print(f"  {d}: {c}")

print("\nMost common last digraphs of words:")
for d, c in last_digraphs.most_common(10):
    print(f"  {d}: {c}")

# Let's try to use a known-plaintext approach.
# The text probably says something like:
# "Congratulations! You decrypted this message successfully..."
# The first word is 8 letters -> probably a common 8-letter word
# Actually let me recount: wbfamljibjxgxqjqqexgxqonfamlwaix 
# wb fa ml ji bj xg xq jq qe xg xq on fa ml wa ix = 16 digraphs = 16 plaintext letters

print("\nFirst word length:", len(words_ct[0])//2, "letters")
print("Last word length:", len(words_ct[-1])//2, "letters")

