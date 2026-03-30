#!/usr/bin/env python3
def decode_rail_fence(cipher, rails):
    # 构建栅栏矩阵
    fence = [["\n"] * len(cipher) for _ in range(rails)]
    rail, direction = 0, 1

    # 标记字符位置
    for i in range(len(cipher)):
        fence[rail][i] = "*"
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction

    # 填入密文字符
    index = 0
    for r in range(rails):
        for c in range(len(cipher)):
            if fence[r][c] == "*":
                fence[r][c] = cipher[index]
                index += 1

    # 按波浪路径读取明文
    rail, direction = 0, 1
    result = []
    for i in range(len(cipher)):
        result.append(fence[rail][i])
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    return "".join(result)


ciphertext = "Orrs r u uduxto'ue tt wyucea i.stnfustaoinceseo slio oeoget hyuntdch df het.Ori ooleoz  nriday i:reu. oe nptoih rnyeufyec nht oa  a eetwrrmelestes,ucdrgitesemetlI  anac,sipalf ne stcd oo rhe  nhwmetGz"

for rails in range(2, 12):
    plaintext = decode_rail_fence(ciphertext, rails)
    print(f"[-] Rails {rails}: {plaintext}"
