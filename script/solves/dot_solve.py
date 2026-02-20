import matplotlib.pyplot as plt

x_coords = []
y_coords = []

with open("secret_map.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line:
            parts = line.split()
            x_coords.append(int(parts[0], 16))
            y_coords.append(-int(parts[1], 16))

plt.scatter(x_coords, y_coords, s=1, color="black")
plt.axis("equal")
plt.axis("off")

plt.show()
