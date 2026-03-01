#!/usr/bin/env python3

from PIL import Image
import numpy as np

# 1. 解析图片并提取真正的像素矩阵，而不是盲目读取 raw bytes
img_flag = np.array(Image.open("./flag.png"))
img_lemur = np.array(Image.open("./lemur.png"))

# 2. 确保两张图片尺寸一致 (Arch 哲学：不要假设，要验证)
if img_flag.shape != img_lemur.shape:
    print("Kernel Panic: Image dimensions do not match!")
    exit(1)

# 3. 使用底层的 C 扩展库 (numpy) 进行高速矩阵位运算
result_matrix = np.bitwise_xor(img_flag, img_lemur)

# 4. 重新打包成合法的图片格式并保存
Image.fromarray(result_matrix).save("./result.png")

print("XOR complete.")
