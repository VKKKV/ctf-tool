#!/usr/bin/env python3

import requests

BASE_URL = "http://localhost/mission"

HEAD = {"Host": "net-force.nl"}


def main():
    res = requests.get(BASE_URL, headers=HEAD)
    print(res.text)
    print(res.text.strip())


if __name__ == "__main__":
    main()
