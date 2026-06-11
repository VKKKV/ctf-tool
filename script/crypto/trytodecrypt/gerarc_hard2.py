from utils import original_dict

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
        result.append(decryption_dict[key])
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

# 6F5657 A6606B7D9C7480649D7A6B757D9C70816B6CB4 'Take the blue pill!'

# 012345abcdefxyzABCDEFXYZ-_.,;:

# 391A56 391B583C1E5B40225F4325624628655A3C795D3F7C60427F745693775996
#        0 1 2 3 4 5 7 8 9 a b c d e f x y z A B C D E F X Y Z - _ . 

# 19421C 19431E1C4621204A25234D2826502B3A643F3D6742406A45547E5957815C
#        0 1 2 3 4 5 7 8 9 a b c d e f x y z A B C D E F X Y Z - _ . 
