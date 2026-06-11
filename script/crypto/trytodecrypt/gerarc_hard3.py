original_dict = {
    '0': 0x2A, '1': 0x1B, '2': 0x43, '3': 0x17,
    '4': 0x2B, '5': 0x01, '6': 0x2E, '7': 0x09,
    '8': 0x33, '9': 0x39, 'a': 0x27, 'b': 0x0B,
    'c': 0x41, 'd': 0x45, 'e': 0x0E, 'f': 0x10,
    'g': 0x11, 'h': 0x05, 'i': 0x2f, 'j': 0x1c,
    'k': 0x16, 'l': 0x18, 'm': 0x04, 'n': 0x35,
    'o': 0x3E, 'p': 0x37, 'q': 0x1D, 'r': 0x1F,
    's': 0x15, 't': 0x21, 'u': 0x1A, 'v': 0x23,
    'w': 0x00, 'x': 0x0C, 'y': 0x3B, 'z': 0x30,
    'A': 0x1E, 'B': 0x13, 'C': 0x25, 'D': 0x3C,
    'E': 0x39, 'F': 0x29, 'G': 0x7A, 'H': 0x7B,
    'I': 0x7C, 'J': 0x7D, 'K': 0x7E, 'L': 0x7F,
    'M': 0x70, 'N': 0x71, 'O': 0x72, 'P': 0x73,
    'Q': 0x74, 'R': 0x75, 'S': 0x76, 'T': 0x77,
    'U': 0x78, 'V': 0x79, 'W': 0x7A, 'X': 0x7B,
    'Y': 0x7C, 'Z': 0x7D, '-': 0x7E, '_': 0x7F,
    '.': 0x03, ',': 0x71, ';': 0x72, ':': 0x73,
    '?': 0x74, '!': 0x75, ' ': 0x12, '&': 0x77,
    '|': 0x78, '¿': 0x79, '=': 0x7A, '/': 0x7B,
}

def encrypt(phrase: list[str], shift: list[int]) -> list[str]:
    result = []
    count = 0
    for letter in phrase:
        result.append(hex(original_dict[letter] + shift[count % 3])[2:])
        count += 1
    return result

def decrypt(phrase: list[str]) -> list[str]:
    decryption_dict = {val: key for key, val in original_dict.items()}
    result = []
    count = 0
    for letter in phrase[3:]:
        shift = int(phrase[count % 3], 16)
        key = int(letter,  16) - shift
        try:
            result.append(decryption_dict[key])
        except: pass
        count += 1
    return result


def app():
    res = ''
    if input('What do you wanna do? -> ') == 'yes':
        inp = input('shift: ')
        shift = [int(inp[i:i+2], 16) for i in range (0, len(inp), 2)]
        phrase = [*input('Phrase to encrypt: ')]
        res = ''.join(encrypt(phrase, shift))
    else:
        inp = input('Phrase to decrypt: ')
        phrase = [inp[i:i+2] for i in range (0, len(inp), 2)]
        res = ''.join(decrypt(phrase))
    print(''.join(res))

if __name__ == '__main__':
    app()

# 574168 755997984F7A7E76AD6954A662538F764F7A5C4F876544
# 574168 75 59 97 98 4F 7A 7E 76 AD 69 54 A6 62 53 8F 76 4F 7A 5C 4F 87 65 44

# 0123456789abcdefxyzABCDEFXYZ-_.

# 872B85 B1 46C89E5686B534B8C05290C870939737C0B74998AC67AEB36A9E9B6BAB8A
# 0123456789abcdefxyzABCDEFXYZ-_.

# 161C324037752D47334425654F433D57614026286D463A453B585B425B4B2A5C5819
# 0123456789abcdefxyzABCDEFXYZ-_.

# 715354 9B 7D 7E 9B 6E 6F 8C 6E
#        0  0  0  0  1  1  1  1 

# 872B85 B1 46 C8 9E 56 86 B5 34 B8 C0 52 90 C8 70 93 97 37 C0 B7 49 98 AC 67 AE B3 6A 9E 9B 6B AB 8A
#        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f  x  y  z  A  B  C  D  E  F  X  Y  Z  -  _  .
# 161C32 40 37 75 2D 47 33 44 25 65 4F 43 3D 57 61 40 26 28 6D 46 3A 45 3B 58 5B 42 5B 4B 2A 5C 58 19

#        2a 1b 43 17 2b 01 2e 09 33 39 27 0b 41 45 0e 10 0c 3b 30 1e 13 25 3c 39
#        1  2  3  1  2  3  1  2  3  1  2  3  1  2  3  1  2  3  1
