#!/usr/bin/env python3
from pathlib import Path

import matplotlib.pyplot as plt

DATA_FILE = Path(__file__).parent / "secret_map.txt"


def main():
    x_coords = []
    y_coords = []

    with open(DATA_FILE, "r") as f:
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


if __name__ == "__main__":
    main()
