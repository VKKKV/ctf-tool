#!/usr/bin/env python3
"""
Hill-climbing solver for digraph substitution cipher
"""
import random
import math
from collections import Counter

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
unique = sorted(set(t for t in tokens if t != ' '))
N = len(unique)
print(f"Unique digraphs: {N}")

# Build English quadgram statistics (simplified - use log probabilities)
# I'll use a simple scoring based on English letter frequencies

# English letter frequency (simplified)
eng_freq = {
    'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253,
    'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094,
    'i': 0.06966, 'j': 0.00153, 'k': 0.00772, 'l': 0.04025,
    'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929,
    'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
    'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150,
    'y': 0.01974, 'z': 0.00074
}

# Let's try frequency mapping based on digraph frequency
digraph_freq = Counter(t for t in tokens if t != ' ')
sorted_digraphs = [d for d, _ in digraph_freq.most_common()]
sorted_eng = sorted(eng_freq.keys(), key=lambda c: eng_freq[c], reverse=True)

print("\nDigraphs by frequency:")
for i, d in enumerate(sorted_digraphs):
    print(f"  {d}: {digraph_freq[d]}")

print("\nEnglish letters by frequency:")
for i, c in enumerate(sorted_eng):
    print(f"  {c}: {eng_freq[c]:.4f}")

# Create initial mapping based on frequency
mapping = {}
for i, d in enumerate(sorted_digraphs):
    if i < 26:
        mapping[d] = sorted_eng[i]
    else:
        # Extra digraphs - map to a-z or punctuation
        mapping[d] = chr(ord('A') + i - 26)  # Use uppercase for extras

def decrypt(tokens, mapping):
    result = []
    for t in tokens:
        if t == ' ':
            result.append(' ')
        else:
            result.append(mapping.get(t, '_'))
    return ''.join(result)

print("\n\nInitial decryption (frequency-based):")
plain = decrypt(tokens, mapping)
print(plain)

# Let me try a more targeted approach by assuming common words
# The text probably starts with "Congratulations" (16 letters? No... "Congratulations" has 16 letters)
# Actually let me count: C-o-n-g-r-a-t-u-l-a-t-i-o-n-s = 15 letters!
# But the first word is 16 ciphertext letters. Hmm.

# Let me check: "Congratulations" is 15 letters.
# Our first word has 16 digraphs = 16 plaintext letters.
# "Congratulations" + space? No, it's the first word.
# Maybe "Congratulations!" - that would be 16 characters.

# Let me try: wb->C, fa->o, ml->n, ji->g, bj->r, xg->a, xq->t, jq->u, qe->l, on->a, wa->i, ix->!
# But we need to be careful about case - the challenge says "correct case and punctuation"

# Let me try another approach: search for "You decrypted this" or similar patterns

# Actually, let me just use a proper approach: 
# Build a mapping and iteratively improve it

# Let me try manual approach by looking at word patterns
# Word 0: wb fa ml ji bj xg xq jq qe xg xq on fa ml wa ix (16 letters)
# Word 6: yp xg wa (3 letters)
# Word 7: ml fa xq (3 letters)
# Word 8: xq fa fa (3 letters) - pattern: A B B, likely "see", "too", "all"
# Word 19: xg wa (2 letters) - pattern: A B, likely "be", "to", "in", "it", "is", "or", "as", "at", "of", "by", etc.

# If xg wa = "is" or "it" or "in" or "to" or "be"
# And yp xg wa = ?-?-? where xg wa is a common 2-letter word
# Common 3-letter word patterns: "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "has"

# Word 8 = xq fa fa = pattern A-B-B
# Could be: "see", "too", "all", "bee", "off", "add", "odd", "egg"

# If xq fa fa = "all" or "see" or "too"
# And xq appears frequently (12 times), fa appears frequently (12 times)

# Let me try: xq = 'a' and fa = 'l' -> "all"
# Or xq = 't' and fa = 'o' -> "too"
# Or xq = 's' and fa = 'e' -> "see"

# Let me check: word 7 = ml fa xq 
# If fa='e' and xq='t', then ml=? in "?et" 
# Common 3-letter words ending in "et": "get", "set", "yet", "let", "bet", "met", "pet", "wet"
# If fa='l' and xq='l', then ml=? in "?ll" -> "all", "ill", "ell", "oll", "ull"

# Let me try fa='e' first (most frequent English letter)
# Then xq=... hmm

# Let me look at word 19 = xg wa (2 letters)
# Common 2-letter words: of, to, in, it, is, be, as, at, so, we, he, by, or, on, do, if, me, my, up, an, go, no, us, am

# Word 6 = yp xg wa (3 letters)
# If xg wa = common 2-letter word, yp xg wa = ?-common2letter
# E.g., if xg wa = "to", yp xg wa could be "into" (that's 4 letters... no)
# Could be: "not to" (if spaces... no, it's one word)
# "onto" = 4 letters, not 3
# If xg wa = "is": "this", "his" - 4 letters
# If xg wa = "in": "pin", "win" - 3 letters
# If xg wa = "be": "the" - 3 letters! the = yp-xg-wa?

# Let me try: xg wa = "be" and yp = "t" -> yp xg wa = "the"
# Then from word 6: yp xg wa = "the"
# And word 19: xg wa = "be" or "to" or "in" or "is"

# Let me try xg='b', wa='e' -> xg wa = "be"
# Then yp='T' (uppercase T for start of word?) or 't'
# That gives yp xg wa = "Tbe" or "the" 

# Let me look at the first word again:
# wb fa ml ji bj xg xq jq qe xg xq on fa ml wa ix

# If this is "Congratulations!" then:
# wb='C', fa='o', ml='n', ji='g', bj='r', xg='a', xq='t', jq='u', qe='l', on='a', wa='i', ix='!'

# Let me check if this is consistent with other words:
# Word 19: xg wa = 'a' + 'i' = "ai" - not a common word

# Hmm. Let me try another approach entirely. Let me try to decode using a known solution.

# From the Programmer Sought article, the solution for the other version was 
# "Congratulations You decrypted this message successfully ..."
# But that was for a different ciphertext

# Let me try thinking about it differently. 
# Maybe "congratulations" starts the sentence but the first word is actually longer.
# Wait, "congratulations" is 15 characters. Let me recount the first word.

# wb fa ml ji bj xg xq jq qe xg xq on fa ml wa ix
# That's 16 digraphs. "congratulations" is 15 characters.
# "congratulations!" is 16 characters!

# If ix = '!' (punctuation), and the word is "congratulations!":
# wb=c, fa=o, ml=n, ji=g, bj=r, xg=a, xq=t, jq=u, qe=l, on=a, wa=i, ix=!

# Let me try this mapping:
manual_map = {
    'wb': 'c',
    'fa': 'o',
    'ml': 'n',
    'ji': 'g',
    'bj': 'r',
    'xg': 'a',
    'xq': 't',
    'jq': 'u',
    'qe': 'l',
    'on': 'a',
    'wa': 'i',
    'ix': '!',
}

print("\n\nWith 'congratulations!' hypothesis:")
pt = decrypt(tokens, manual_map)
print(pt)

# Let me also check what other words look like with this mapping

# Word 1: ei fa jq -> ei o u -> ?-o-u -> could be "you"
# If ei='y' and jq='u', then ei fa jq = "you" - yes!
# But I already mapped jq='u'. So ei='y' makes word 1 = "you"

manual_map['ei'] = 'y'

# Word 11: oy xg wa -> oy a i -> ?-a-i -> could be "hai", "sai", "mai" 
# Hmm, doesn't seem right

# Let me check word 2: pz ij tv bj ae co xq ij pz
# With current mapping: pz ?-?-? r ?-? t ? pz
# bj = r, xq = t
# pz ij tv bj ae co xq ij pz = pz-?-?-r-?-co-t-?-pz

# Let me keep building step by step
print("\nCurrent partial mapping:")
for k, v in manual_map.items():
    print(f"  {k} -> {v}")

# With this mapping, let me see what we have
print("\nPartial decryption:")
print(decrypt(tokens, manual_map))

