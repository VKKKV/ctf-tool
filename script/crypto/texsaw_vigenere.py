def vigenere_decrypt(ct, key, offset=0):
    res = ""
    k_idx = offset
    key = key.lower()
    for char in ct:
        if "a" <= char <= "z":
            shift = ord(key[k_idx % len(key)]) - ord("a")
            res += chr((ord(char) - ord("a") - shift) % 26 + ord("a"))
            k_idx += 1
        elif "A" <= char <= "Z":
            shift = ord(key[k_idx % len(key)]) - ord("a")
            res += chr((ord(char) - ord("A") - shift) % 26 + ord("A"))
            k_idx += 1
        else:
            res += char
            # k_idx is NOT incremented for non-alpha
    return res


key = "askanditshallbegivenyouseekandyeshallfind"

ct1 = "twhsnz{tngqmqdhqqygxrloyehuvxtwwvxklkiiudpxqcvqhbmkepledu}"
ct2 = "brassg{lhrrfxzgxvrpzmierkrkdbkdyeibpredxbrflvvvotgvfisacb}"

# just loop and try offset
print("CT1:", vigenere_decrypt(ct1, key, 0))

print("CT2:", vigenere_decrypt(ct2, key, 38))

msg1 = """zpzc xlcq aq lorr, dlh aas zyqg n paldee rn mate mpgsxm olrw tcfh set jkm m st.
tpwq buh gwxeedt pzht esf jrib mf yg mgsr ks crqwailp.
ejty whw qeahztd ieqzsi zpzc sgbx gyx ghruc me oiotso!
vi adv gbha pwsl, t'wm qkmo cbs on gyv pievr qwlttyl tbfalsoa wwfgyrzh bx sqyrvevn.
eeoo shuc cgb'rp ytb srldywrg

x.l. loe xzwmk "qhmgyhcgr kkmr" lq zwyy rztl. lru krohol psacs tu anmi cbs quf.
- nsrn pdgvfjrzdx
"""

print("\nMessage 1:")
print(vigenere_decrypt(msg1, key, 15))
