from utils import original_dict

def encrypt(phrase: list[str], shift: int) -> list[str]:
    encryption_dict = {key: val + shift for key, val in original_dict.items()}
    result = [hex(encryption_dict[letter])[2:] for letter in phrase]
    return result

def decrypt(phrase: list[str]) -> list[str]:
    shift = int(phrase[0], 16)
    decryption_dict = {val + shift: key for key, val in original_dict.items()}
    result = [decryption_dict[int(letter, 16)] for letter in phrase[1:]]
    return result

def app():
    res = ''
    if input('What do you wanna do? -> ') == 'yes':
        shift = int(input('encryption shift: '), 16)
        phrase = [*input('Phrase to encrypt: ')]
        res = encrypt(phrase, shift)
    else:
        code = input('Phrase to decrypt: ')
        phrase = [code[i:i+2] for i in range (0, len(code), 2)]
        res = decrypt(phrase)
    print(phrase)
    print(''.join(res))

if __name__ == '__main__':
    app()

# 101A1B1C1D1E1F2021222324
# 1034
# 131D1E1F2021222324252627
# 111112131415161718191A1B '0123456789a'
# 202A2B2C2D2E2F3031323334
# 303A3B3C
# 30303132333435363738393A3B3C '0123456789a'
# 333D3E3F4041424344454647

# 50737496 'zA '
