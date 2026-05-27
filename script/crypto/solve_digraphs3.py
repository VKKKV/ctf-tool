#!/usr/bin/env python3
"""
Solve Digraph substitution cipher using hill climbing / frequency analysis
"""
from collections import Counter
import random
import math

ciphertext = "wbfamljibjxgxqjqqexgxqonfamlwaix eifajq pzijtvbjaecoxqijpz xqioonwa lzijwawaxgjiij wajqtvtvijwawaxhjqqeqeaeix ypxgwa mlfaxq xqfafa pzonxhxhontvjqqexq ijonxqioijbjla oyxgwa onxqym ypijqeqela jifafapz tefaoiix uzmlxqijbj xqioonwa qfijaeoyfabjpz xgwa wafaqejqxqonfamlxr xhxgmloitvxhonxhlzjijimlix"

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

# Get unique digraphs and assign letters
unique_digraphs = sorted(set(t for t in tokens if t != ' '))
print(f"Unique digraphs: {len(unique_digraphs)}")
digraph_to_idx = {d: i for i, d in enumerate(unique_digraphs)}
idx_to_digraph = {i: d for i, d in enumerate(unique_digraphs)}

# Convert to index sequence
seq = [digraph_to_idx[t] if t != ' ' else -1 for t in tokens]

# We have 30 unique digraphs for 26 letters - maybe some represent capitals/punctuation
# Let's create a mapping from index to plaintext letter (a-z)
# We'll use 26 letters, indices 0-29

# English quadgram frequencies
# Let's load some from internal data
english_freqs = {
    'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253,
    'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094,
    'i': 0.06966, 'j': 0.00153, 'k': 0.00772, 'l': 0.04025,
    'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929,
    'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
    'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150,
    'y': 0.01974, 'z': 0.00074
}

# Let's just try a simple approach: try to find the substitution manually
# by looking at patterns

# Print the ciphertext as letters
print("\nCiphertext as letter sequence (spaces preserved):")
print(' '.join([str(digraph_to_idx[t]) if t != ' ' else '|' for t in tokens]))

# Let's look for repeated patterns
# The digraph 'fa' appears 12 times, 'xq' 12 times, 'wa' 12 times
# These likely map to common English letters like e, t, a

# Common English letters: e, t, a, o, i, n, s, h, r
# Top digraphs: fa(12), xq(12), wa(12), ij(10), on(9), ml(7), xg(7), qe(7)

# Let's try an approach: find 'the' pattern
# In English, 'the' is very common. Let's look for three-letter sequences
# in the ciphertext that repeat

# Find all 3-digraph sequences (3 letters of plaintext)
tri_sequences = Counter()
for i in range(len(tokens) - 3):
    if tokens[i] != ' ' and tokens[i+1] != ' ' and tokens[i+2] != ' ':
        tri = (tokens[i], tokens[i+1], tokens[i+2])
        tri_sequences[tri] += 1

print("\nTop 20 trigraph sequences:")
for seq, count in tri_sequences.most_common(20):
    print(f"  {''.join(seq)}: {count}")

# Also find repeated 2-digraph sequences (bigrams)
bi_sequences = Counter()
for i in range(len(tokens) - 2):
    if tokens[i] != ' ' and tokens[i+1] != ' ':
        bi = (tokens[i], tokens[i+1])
        bi_sequences[bi] += 1

print("\nTop 20 digraph sequences (plaintext bigrams):")
for seq, count in bi_sequences.most_common(20):
    print(f"  {''.join(seq)}: {count}")

# Let's also look at what words have repeated patterns
# Like word 8: xq-fa-fa would be ?ee or ?ll or ?ss, etc.
print("\n\nLooking at word structure patterns:")

# Word 8: xqfafa = [xq, fa, fa] = ?-?-? where last two are same
# This could be: see, too, all, off, add, etc.
# Word 8 = "xqfafa" - pattern: A-B-B -> likely "see", "too", "all", "bee", "off", "add"

# Word 0 (first 4): wb-fa-ml-ji-bj-xg-xq-jq-qe-xg-xq-on-fa-ml-wa-ix (16 letters)
# Word 13: yp-ij-qe-qe-la = A-B-C-C-D pattern

# Let me try a different approach: manually assign based on known patterns
# and see if we can make sense of it.

# The repeated digraphs in word 0: fa appears twice, ml appears twice, xg appears twice, xq appears twice
# The plaintext likely has repeated letters too.

print("\n\nAttempting manual decryption with frequency mapping...")

# Most common English letters: e,t,a,o,i,n,s,h,r,d,l,c,u,m,w,f,g,y,p,b,v,k,j,x,q,z
# Most common digraphs in cipher: fa(12), xq(12), wa(12), ij(10), on(9), ml(7), xg(7), qe(7)

# Let's try: fa->e, xq->t, wa->a (most common to most common)
# Or: since English distribution varies: e~12%, t~9%, a~8%, o~7.5%, i~7%, n~6.7%, s~6.3%

mapping = {
    'fa': 'e',  # most common
    'xq': 't',  # 2nd most common
    'wa': 'a',  # 3rd most common
    'ij': 'o',  # 4th most common
    'on': 'n',  # or i/n
    'ml': 's',  # 
    'xg': 'r',
    'qe': 'i',
    'jq': 'h',
    'xh': 'd',
}

def decrypt(tokens, mapping):
    result = []
    for t in tokens:
        if t == ' ':
            result.append(' ')
        else:
            result.append(mapping.get(t, '_'))
    return ''.join(result)

print("With mapping attempt:")
print(decrypt(tokens, mapping))

