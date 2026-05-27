ciphertext = "ÁẨĀǍẦĀẶẰẨǍĄẦẤĂẤĂĀȀẨȀẶǍẠẢĄẨÁÀẨĂĂĀȦẨẮĂẤȀȦĀĂẤÀẢẪẨĂẮẴĂĄẤĄẮĄẤẲȀẲAẶẲẮǍĂẨĄẦẤĂĂẦẲẮẪÁẴẨĂẮẢẨǍẨĀĂẠẴẮĄÀĀẠẴẨẠẲẮȦẨĄẦẨĀÁĀẶẦẨĂẨĄĄẤȀȦẮẢẠẲẮǍẶǍĀẶẰẨǍÁẲẤȀȦĄẦẤĂẴẠẦĀȀÁÀẤȦẦĄẴẨĀẪĂẲĀȀȀẲẠẤȀȦĄẦĀȀẰĂĄẲĄẦẨẪẲẲẰĀẪẤẰẨĂĄẦẨẶẦĀǍĀẶĄẨǍĂĀǍẨẮĄAĂẲẤĄĂĀẪĂẲĀẢǍẲẴẪẨÀĄẲẤÁẨȀĄẤAẠĄẦẨẴẠĄẨĂÀĀẠẴẨẪẨĄẮĂẰȀẲÄẤȀĄẦẨȂẲĄẨĂĀȀÁĂẲẪẮĄẤẲȀẴẲĀǍÁĀẴẲẮĄẠẲẮǍẨẬẢẨǍẤẨȀẶẨĀȀẠÄĀẠȀẴǍẦẲÁȀẶÁAÀẨẤĂẠẲẮǍĂẲẪẮĄẤẲȀ"

mapping = {'Ą': 'T', 'Ầ': 'H', 'Ẩ': 'E'}

print("Context around THE occurrences:")
for i in range(len(ciphertext)-2):
    if ciphertext[i:i+3] == 'ĄẦẨ':
        start = max(0, i-5)
        end = min(len(ciphertext), i+8)
        ctx = ciphertext[start:end]
        decoded_ctx = ''.join(mapping.get(c, f'[{ord(c):04X}]') for c in ctx)
        print(f"  Pos {i}: raw={repr(ctx)}")
        print(f"           decoded={decoded_ctx}")
