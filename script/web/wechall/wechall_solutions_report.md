# WeChall Training Challenges: Solution Methods

## 1. Training: Crypto - Digraphs

**URL:** https://www.wechall.net/en/challenge/training/crypto/digraph/index.php

### Challenge Description
A digraph substitution cipher where each plaintext letter is encrypted as exactly two characters. With 26 alphabet letters, up to 26*26 unique digraphs are possible. The message is in English, uses correct case and punctuation, and has no line breaks.

### Ciphertext (current version)
```
wbfamljibjxgxqjqqexgxqonfamlwaix eifajq pzijtvbjaecoxqijpz xqioonwa lzijwawaxgjiij wajqtvtvijwawaxhjqqeqeaeix ypxgwa mlfaxq xqfafa pzonxhxhontvjqqexq ijonxqioijbjla oyxgwa onxqym ypijqeqela jifafapz tefaoiix uzmlxqijbj xqioonwa qfijaeoyfabjpz xgwa wafaqejqxqonfamlxr xhxgmloitvxhonxhlzjijimlix
```

### Solution Method
1. **Tokenize** - Split ciphertext into pairs (digraphs), preserving spaces. Gives 22 words, 157 tokens total, 30 unique digraphs.

2. **Frequency Analysis** - Count digraph frequencies (fa=12, xq=12, wa=12, ij=10, on=9, ml=7, xg=7, qe=7, jq=6, xh=6, etc.) and compare to English letter frequencies.

3. **Known-Plainword Attack** - Look for common English words by their letter-count and pattern:
   - Word 7 = "ml fa xq" = 3 letters → likely "not" → ml=n, fa=o, xq=t
   - Word 8 = "xq fa fa" = 3 letters, A-B-B pattern → "too" → xq=t, fa=o (confirmed)
   - Word 19 = "xg wa" = 2 letters → "as" or "is" or "to" → with xg=a, wa=s gives "as"
   - Word 1 = "ei fa jq" = 3 letters → "you" → ei=y, jq=u
   - Word 0 = "wbfamljibjxgxqjqqexgxqonfamlwaix" = 16 letters → "congratulations!" → full mapping derived

4. **Iterative Refinement** - Build a digraph-to-letter mapping dictionary, decrypt partially, guess new words from context, add more mappings:
   - After partial decryption, words like "this", "decrypted", "message", "successfully", "difficult", "either", "well", "good", "job" become readable
   - Continue until the full plaintext is revealed

5. **Key Insight** - There are 30 unique digraphs for 26 letters; the extra digraphs represent uppercase letters and punctuation characters.

### Final Plaintext (typical pattern from similar challenges)
The decrypted message typically reads something like: "Congratulations! You decrypted this message successfully. It was not too difficult either, was it? Well good job. Enter this keyword as solution: [the_answer]."

---

## 2. Training: GPG

**URL:** https://www.wechall.net/en/challenge/training/crypto/gpg/index.php

### Challenge Description
Set up GPG encryption for emails sent by WeChall. Generate a GPG key pair locally, upload the public key to WeChall account settings, and receive encrypted emails to obtain the solution.

### Solution Method

#### Step 1: Generate GPG Key Pair
```bash
gpg --gen-key
```
Provide real name and email address (must match WeChall account email). Set a passphrase to protect the private key.

#### Step 2: Export Public Key
```bash
gpg --armor --output pubkey.asc --export [email-or-uid]
```

#### Step 3: Upload to WeChall
- Go to WeChall Account Settings
- Paste the entire public key block into the GPG key field
- Click "Upload Key"

#### Step 4: Verify the Key
- WeChall sends an encrypted verification email
- Copy the raw email content (ciphertext block)
- Format it properly as a PGP message with BEGIN/END PGP MESSAGE headers
- Save to file (e.g., auth.gpg)
- Decrypt:
  ```bash
  gpg --output auth.html --decrypt auth.gpg
  ```
- Open auth.html in a browser, click the verification link

#### Step 5: Get the Solution
- Return to the challenge page
- Click "Send me encrypted mail please"
- Receive another encrypted email
- Format and decrypt the same way:
  ```bash
  gpg --output flag.html --decrypt flag.gpg
  ```
- Open flag.html to reveal the solution/answer

### Key Commands Summary
| Command | Purpose |
|---------|---------|
| gpg --gen-key | Generate key pair |
| gpg --list-keys | List public keys |
| gpg --armor --export [uid] | Export public key in ASCII |
| gpg --output file --decrypt file.gpg | Decrypt a message |

### Notes
- The GPG challenge requires an authenticated WeChall session, a valid email address, and account-specific configuration to complete
- Both challenges are score-2 "Training" level challenges on WeChall
