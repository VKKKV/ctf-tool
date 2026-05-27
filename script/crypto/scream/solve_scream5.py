import sys
from collections import Counter

ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

unique = sorted(set(ciphertext))
print(f"Unique characters: {len(unique)}")
for c in unique:
    count = ciphertext.count(c)
    pct = count / len(ciphertext) * 100
    print(f"  {c} U+{ord(c):04X}: {count:3d} ({pct:.1f}%)")

# Let me try the mapping from the official scream cipher implementation
# The rust crate uses A + combining marks. Let me match precomposed equivalents.
# Based on Unicode decomposition:
# Let me try the mapping from dcode.fr or Seth's blog

# First, let's try dcode.fr mapping
# From dcode: A->A, B->Ȧ, C->A̧(not in my set), D->A̱(not), E->Á, F->A̮(not), G->A̋(not),
# H->A̰(not), I->Ả, J->A̓(not), K->Ạ, L->Ă, M->Ǎ, N->Â(not), O->Å(not),
# P->A̯(not), Q->A̤(not), R->Ȃ, S->Ã(not), T->Ā, U->Ä, V->À, W->Ȁ, X->A̽(not), Y->A̦(not), Z->Ⱥ(not)

# My ciphertext has chars: A, À, Á, Ä, Ā, Ă, Ą, Ǎ, Ȁ, Ȃ, Ȧ, Ạ, Ả, Ấ, Ầ, Ẩ, Ẫ, Ậ, Ắ, Ằ, Ẳ, Ẵ, Ặ
# The ones from dcode that match: A, À, Á, Ä, Ā, Ă, Ǎ, Ȁ, Ȃ, Ȧ, Ạ, Ả

# Unicode decomposition of my chars:
# Ấ = A + U+0302 (circumflex) + U+0301 (acute) 
# Ầ = A + U+0302 (circumflex) + U+0300 (grave)
# Ẩ = A + U+0302 (circumflex) + U+0309 (hook above)
# Ẫ = A + U+0302 (circumflex) + U+0303 (tilde)
# Ậ = A + U+0302 (circumflex) + U+0323 (dot below)
# Ắ = A + U+0306 (breve) + U+0301 (acute)
# Ằ = A + U+0306 (breve) + U+0300 (grave)
# Ẳ = A + U+0306 (breve) + U+0309 (hook above)
# Ẵ = A + U+0306 (breve) + U+0303 (tilde)
# Ặ = A + U+0306 (breve) + U+0323 (dot below)

# These are Vietnamese characters combining a base diacritic (circumflex or breve) 
# with a tone mark (acute, grave, hook, tilde, dot below)

# In the Rust implementation:
# circumflex (U+0302) = N
# breve (U+0306) = L
# acute (U+0301) = E
# grave (U+0300) = V
# hook above (U+0309) = I
# tilde (U+0303) = S
# dot below (U+0323) = K

# So maybe the Vietnamese-style characters encode TWO letters? Like Ấ = circumflex(N) + acute(E) = "NE"?
# But that seems unlikely for a simple substitution.

# OR maybe the challenge uses a different mapping where 
# Vietnamese A characters (circumflex + tone) map to specific letters

# Let me try a completely different approach - use an automated substitution solver
# with known English word patterns

# The challenge says "Punctuation has been removed" - so it's a continuous string
# of English text. Common words like "THE", "AND", "THAT", "THIS" would appear.

# Let me try to identify "THE" - the most common trigram in English
# Most common trigram in ciphertext
trigrams = Counter()
for i in range(len(ciphertext)-2):
    trigrams[ciphertext[i:i+3]] += 1
print("\nTop 10 trigrams:")
for tg, cnt in trigrams.most_common(10):
    print(f"  {repr(tg)}: {cnt}")

# The most common trigram is ĄẦẨ (5 times)
# If this = "THE", then Ą=T, Ầ=H, Ẩ=E
mapping = {'Ą': 'T', 'Ầ': 'H', 'Ẩ': 'E'}
decoded = ''.join(mapping.get(c, '?') for c in ciphertext)
print(f"\nWith ĄẦẨ = THE:")
print(decoded)

