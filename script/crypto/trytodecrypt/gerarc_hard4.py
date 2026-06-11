from utils import original_dict

def encrypt(phrase: list[str], shift: list[int]) -> list[str]:
    pass

def decrypt(phrase: list[str]) -> list[str]:
    result = []
    decryption_dict = {val: key for key, val in original_dict.items()}
    for letter in phrase:
        first = int(letter[:2], 16)
        second = int(letter[2:], 16)
        delta = second - first
        result.append(decryption_dict[delta])
    return result


def app():
    cipher_text = input('Phrase to decrypt: ')
    phrase = [cipher_text[i:i + 4] for i in range(0, len(cipher_text), 4)]
    res = decrypt(phrase)
    print(''.join(res))

if __name__ == '__main__':
    app()


# 3263 2E31 4984 4B82 1157 94BA 78AD 87C3 6DA0 1148 7070 80C6 5459 255C 2C64 87B0 2851

# 3939 7879 797B 474A 1216 797E 4B52 151D 525B 414B 3641 8E9A 5663 5C6A667572936789547750746A8F5E8452792C542F586AA591CD58956BA952915696
# 012345789abcdefxyzABCDEFXYZ-_.

# 3535 6666 4141 8E8E 7475 1011 3435 6869
# 00001111
