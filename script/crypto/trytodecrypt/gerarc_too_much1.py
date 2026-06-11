from hard4 import decrypt

def prepare(phrase: str):
    split_point = len(phrase) // 5
    cipher_text = phrase [split_point:]
    return [cipher_text[i:i + 4] for i in range(0, len(cipher_text), 4)]

def app():
    phrase = input('Phrase to decrypt: ')
    res = decrypt(prepare(phrase))
    print(''.join(res))


if __name__ == '__main__':
    app()
