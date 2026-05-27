ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

# Hypothesis: "ĄẦẨ" = "THE" (most common trigram)
# Ą -> T
# Ầ -> H
# Ẩ -> E

mapping = {
    'Ą': 'T',
    'Ầ': 'H', 
    'Ẩ': 'E',
}

# Let's also map some other common ones based on English letter frequencies
# English: E(12.7) T(9.1) A(8.2) O(7.5) I(7.0) N(6.7) S(6.3) H(6.1) R(6.0) D(4.3) L(4.0) C(2.8) U(2.8) M(2.5) W(2.4) F(2.2) G(2.0) Y(2.0) P(1.9) B(1.5) V(1.0) K(0.8) J(0.15) X(0.15) Q(0.10) Z(0.07)
# Cipher freq: Ẩ(10.9) Ą(8.8) Ă(8.5) Ẳ(8.2) Ā(7.9) Ấ(6.4) Ȁ(6.4) Ǎ(5.2) Ắ(5.2) Ầ(4.9) Ạ(4.3) Ẵ(3.6) Á(3.3) Ặ(3.0) Ẫ(3.0) À(2.1) Ȧ(2.1) Ằ(1.8) Ả(1.8) A(1.2) Ä(0.6) Ȃ(0.3) Ậ(0.3)

# So basic mapping based on frequency:
# Ẩ(10.9) -> E (12.7)  ✓
# Ą(8.8) -> T (9.1)  ✓ 
# Ă(8.5) -> A (8.2) 
# Ẳ(8.2) -> O (7.5)
# Ā(7.9) -> I (7.0)
# Ấ(6.4) -> N (6.7)
# Ȁ(6.4) -> S (6.3)
# Ǎ(5.2) -> H (6.1)  -- wait, but Ầ is already mapped to H...
# Let me re-examine

# Since we mapped "ĄẦẨ" = "THE":
# Ą -> T, Ầ -> H, Ẩ -> E
# Ą is 2nd most frequent -> T (9.1%) ✓
# Ầ is 10th most frequent -> H (6.1%) - possible
# Ẩ is most frequent -> E (12.7%) ✓

# Now let's look at bigrams and trigrams to verify
# Most common bigrams: ĄẦ (T-H = "TH") appears 9 times - very common in English ✓
# ẨĂ (E?) - 7 times. If Ă = A, then "EA" - common bigram ✓
# ẲẮ (??) - 7 times

# Let's look at the text and see if we can identify "THE" patterns
print("Ciphertext with tentative 'THE' mapping:")
decoded = ''.join(mapping.get(c, '?') for c in ciphertext)
print(decoded)
print()

# Now let's look for "THAT" - another very common word
# "THE" at positions...
for i in range(len(ciphertext)-2):
    if ciphertext[i:i+3] == 'ĄẦẨ':
        print(f"  Position {i}: THE (cipher: {repr(ciphertext[max(0,i-1):i+5])})")

