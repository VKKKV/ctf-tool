#!/usr/bin/env python3
"""
Solve WeChall Training: Crypto - Digraphs
Digraph substitution cipher - each pair of letters = one plaintext letter
"""

ciphertext = "wbfamljibjxgxqjqqexgxqonfamlwaix eifajq pzijtvbjaecoxqijpz xqioonwa lzijwawaxgjiij wajqtvtvijwawaxhjqqeqeaeix ypxgwa mlfaxq xqfafa pzonxhxhontvjqqexq ijonxqioijbjla oyxgwa onxqym ypijqeqela jifafapz tefaoiix uzmlxqijbj xqioonwa qfijaeoyfabjpz xgwa wafaqejqxqonfamlxr xhxgmloitvxhonxhlzjijimlix"

# Split into digraphs (preserving spaces)
def get_digraphs(text):
    result = []
    i = 0
    while i < len(text):
        if text[i] == ' ':
            result.append(' ')
            i += 1
        else:
            result.append(text[i:i+2])
            i += 2
    return result

tokens = get_digraphs(ciphertext)
print("Number of tokens:", len(tokens))

# Get unique digraphs
unique = set(t for t in tokens if t != ' ')
print(f"Unique digraphs ({len(unique)}):", sorted(unique))

# Count frequency
from collections import Counter
freq = Counter(t for t in tokens if t != ' ')
print("\nTop 20 most frequent digraphs:")
for digraph, count in freq.most_common(20):
    print(f"  {digraph}: {count}")

# Let's try to solve this with frequency analysis and pattern matching
# English most common letters: e,t,a,o,i,n,s,h,r,d,l,c,u,m,w,f,g,y,p,b,v,k,j,x,q,z

# The first word likely starts the sentence - could be "congratulations" or "this"
# Let's check the structure

print("\nFirst few digraphs:", tokens[:20])
print("\nLooking for patterns...")

# Let's try to find common English words
# If we look at the first token sequence:
# wb fa ml ji bj xg xq jq qe xg xq on fa ml wa ix
# Let's try to brute-force map by trying to guess words

# The ciphertext has spaces, so words are separated
words_cipher = ciphertext.split(' ')
print(f"\nNumber of words: {len(words_cipher)}")
for i, w in enumerate(words_cipher):
    print(f"  Word {i}: {w} ({len(w)//2} chars)")
