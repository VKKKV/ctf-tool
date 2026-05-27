#!/usr/bin/env python3
"""
Solve Digraph substitution - corrected 'congratulations' mapping
"""
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

# "congratulations!" mapping
# wb fa ml ji bj xg xq jq qe xg xq on fa ml wa ix
#  c  o  n  g  r  a  t  u  l  a  t  i  o  n  s  !
mapping = {
    'wb': 'c', 'fa': 'o', 'ml': 'n', 'ji': 'g', 'bj': 'r', 
    'xg': 'a', 'xq': 't', 'jq': 'u', 'qe': 'l', 'on': 'i', 
    'wa': 's', 'ix': '!'
}

def decrypt(tokens, mapping):
    return ''.join(mapping.get(t, '_') for t in tokens)

print("Initial decryption:")
print(decrypt(tokens, mapping))

# Word 1: ei fa jq = ? o u -> "you"! So ei = y
mapping['ei'] = 'y'
print("\nAfter adding ei=y:")
print(decrypt(tokens, mapping))

# Word 2: pz ij tv bj ae co xq ij pz
# = pz ? ? r ? ? t ? pz
# From the structure: this could be "progress" or "password" or something
# Let me check: pz ij tv bj ae co xq ij pz
# If _ _ _ r _ _ t _ _ = 9 letters
# Common words with r in position 4 and t in position 7:
# "character" = c-h-a-r-a-c-t-e-r - has r in pos 4, t in pos 7... and ends with r
# pz=c, ij=h, tv=a, ae=a, co=c -> but we need different letters for different places
# Actually "character": c-h-a-r-a-c-t-e-r
# pz = c, ij = h, tv = a, bj = r, ae = a, co = c, xq = t, ij = h, pz = c
# Wait, pz appears at positions 1 and 9, and c is at positions 1 and 6 in "character"
# But my mapping already has bj=r and xq=t
# Let me check: pz ij tv bj ae co xq ij pz
#           =  c  h  a  r  a  c  t  h  c
# But ae appears later... Let me check if ae=a is consistent elsewhere

# Actually let me check word 14: ji fa fa pz = ? o o ? 
# ji fa fa pz = g o o ? 
# With pz = c: "goodc"? No...
# With pz = d: "good"? Yes! ji=g, fa=o, fa=o, pz=d
# So pz = d!

# Let me check word 15: te fa oi ix = ? o ? !
mapping['pz'] = 'd'
print("\nAfter adding pz=d:")
print(decrypt(tokens, mapping))

# Word 15: te fa oi ix = t e ? ! -> "teo!" no... 
# Actually ix=! so it's "teoi!" -> maybe "done!"? te=d, fa=o, oi=n, ix=!
# So te = d, oi = n

# But wait, I have ml=n already. So oi might be something else...
# "teoi" -> if te=d, fa=o, oi=n... but I already have ml=n
# Two different digraphs can't map to the same letter... unless one is uppercase?
# Actually, the challenge says "correct case and punctuation" - so maybe some digraphs 
# represent uppercase versions of the same letter?

# Actually wait, re-reading the challenge: "The message is in the current language, 
# is written with correct case and punctuation"
# So uppercase letters might have different digraph representations.

# So we could have:
# 'n' (lowercase) = ml
# 'N' (uppercase) = oi (or some other digraph)

# Word 15: te fa oi ix = ? o ? !
# If it's "done!" then te=d, fa=o, oi=n, ix=!
# te = d
# oi = N (uppercase N)

# Let me check word 10: ij on xq io ij bj la = ? i t ? ? r ?
# = _ i t _ _ r _ (7 letters)
# Could be "letters" (7 letters): l-e-t-t-e-r-s
# ij=l, on=i... wait on=i? Let me recount
# ij on xq io ij bj la = ? i t ? ? r ?
# If this is "letters": l-e-t-t-e-r-s
# ij=l, on=e, xq=t, io=t, ij=l, bj=r, la=s
# But xq is already t! Good.
# on=e? But I had on=i from "congratulations". Wait, let me check again.

# Word 0: wb fa ml ji bj xg xq jq qe xg xq on fa ml wa ix
# c  o  n  g  r  a  t  u  l  a  t  i  o  n  s  !
# Position 12 is 'i'? No wait...
# c-o-n-g-r-a-t-u-l-a-t-i-o-n-s-!
# pos: 1-c, 2-o, 3-n, 4-g, 5-r, 6-a, 7-t, 8-u, 9-l, 10-a, 11-t, 12-i, 13-o, 14-n, 15-s, 16-!
# So on = i (position 12 of "congratulations")
# Wait, that's wrong! "congratulations" spelled:
# c(1) o(2) n(3) g(4) r(5) a(6) t(7) u(8) l(9) a(10) t(11) i(12) o(13) n(14) s(15)
# wb(1) fa(2) ml(3) ji(4) bj(5) xg(6) xq(7) jq(8) qe(9) xg(10) xq(11) on(12) fa(13) ml(14) wa(15) ix(16)
# So on = i indeed!

# Hmm wait, but what if the first word is NOT "congratulations"?
# Let me look at what makes more sense.

# Actually, let me re-examine. The first word has 16 letters. 
# "congratulations" has 15 letters. "congratulations!" has 16 characters if we count '!' as a character.
# But ix is a digraph, so it represents ONE character.
# So the word has 16 plaintext characters.
# "congratulations!" = 16 characters. Yes!

# Let me double-check: C-O-N-G-R-A-T-U-L-A-T-I-O-N-S-!
# That's 16 characters. So on maps to 'i'. Indeed.

# But then for word 10: ij on xq io ij bj la
# With current mapping: ij-on-xq-io-ij-bj-la = ij-i-t-io-ij-r-la
# "letters" would be l-e-t-t-e-r-s
# ij=l, on=e... but on is mapped to i, not e!
# So it's not "letters" if on = i.

# Hmm, maybe "congratulations" is wrong? Let me think of a 16-letter word that starts 
# common sentences.

# "Congratulations" is 15 letters. Maybe it's "Congratulation" (14) or something else?
# Wait, I'm confused. Let me be precise:
# c-o-n-g-r-a-t-u-l-a-t-i-o-n-s = 15 letters
# So the first word tokens (16 digraphs) can't be "congratulations" alone.

# Unless... the first word is actually two words? No, there's no space.

# What 16-letter word/phrase? Let's see:
# "Cryptography" - 12 letters
# "Decipherment" - 12 letters
# "Congratulations" - 15 letters
# "Supercalifragilisticexpialidocious" - too long

# Hmm wait, maybe the first word isn't "congratulations". 
# Let me look again: the last word has 13 digraphs.
# Maybe the text says something like "Well done! You decrypted this message successfully!"

# Let me try a completely different approach. Let me look at word 8 again: xq fa fa = t-o-o = "too"
# And word 19: xg wa = a-s = "as"

# With xg=a, wa=s:
# Word 6: yp xg wa = yp a s = ?-a-s -> "has", "was", "gas", "pas"
# If yp='w', then "was"
# If yp='h', then "has"

# Word 11: oy xg wa = oy a s = ?-a-s -> same pattern

# Word 7: ml fa xq = n o t = "not"! 
# ml=n, fa=o, xq=t -> "not"! This is very promising.

# So our mapping so far:
# wb='c', fa='o', ml='n', ji='g', bj='r', xg='a', xq='t', jq='u', qe='l', 
# on='?', wa='s', ix='!', ei='y', pz='d'
# And from word 8 "xq fa fa" = "too", this works with xq=t, fa=o
# From word 7 "ml fa xq" = "not", this works with ml=n, fa=o, xq=t
# From word 19 "xg wa" = "as" (xg=a, wa=s) - makes perfect sense

# Let me re-examine word 0 with this new understanding:
# wb fa ml ji bj xg xq jq qe xg xq on fa ml wa ix
# c  o  n  g  r  a  t  u  l  a  t  ?  o  n  s  !
# = "congratulat?ons!"
# The 12th letter (on) is the one we don't know.
# "congratulations" would need on='i' -> "congratulati ons!"
# Wait, "congratulations" is c-o-n-g-r-a-t-u-l-a-t-i-o-n-s
# So positions: 1-c,2-o,3-n,4-g,5-r,6-a,7-t,8-u,9-l,10-a,11-t,12-i,13-o,14-n,15-s
# Our word has 16 characters. So it could be "congratulations!" where the 16th is '!'
# Then: wb=c, fa=o, ml=n, ji=g, bj=r, xg=a, xq=t, jq=u, qe=l, on=i, wa=s, ix=!

# WAIT. Let me re-read word 0 carefully:
# wb-fa-ml-ji-bj-xg-xq-jq-qe-xg-xq-on-fa-ml-wa-ix
#  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
#  c  o  n  g  r  a  t  u  l  a  t  ?  o  n  s  !

# Position 12 is 'on', and position 13 is 'fa'=o.
# In "congratulations!": positions are:
# c(1) o(2) n(3) g(4) r(5) a(6) t(7) u(8) l(9) a(10) t(11) i(12) o(13) n(14) s(15) !(16)

# So position 12 = 'i' = on. That works!
# on = i

# And now "congratulations!" becomes "congratulatio ns!"? No:
# "congratulations!" has letters at positions 13-15 as o, n, s.
# Our word has fa(13)=o, ml(14)=n, wa(15)=s, ix(16)=!
# Yes! o-n-s at positions 13-15.

# So on='i' is correct!

# Now word 10: ij on xq io ij bj la
# ij ? t ? ij r ?
# If on = i: ij i t ? ij r ?
# "little r?" wait...
# ij='l' -> l i t ? l r ?
# "literal" = l-i-t-e-r-a-l (7 letters)
# ij=l, on=i, xq=t, io=e, ij=l, bj=r, la=a
# That gives us: io=e, la=a

# Let me check this!
print("\n\nLet me try: ij=l, on=i, io=e, la=a")
mapping['ij'] = 'l'
mapping['on'] = 'i'
mapping['io'] = 'e'
mapping['la'] = 'a'
print(decrypt(tokens, mapping))

