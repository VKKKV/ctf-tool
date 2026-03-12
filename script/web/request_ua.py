import requests

URL = "http://localhost/gate"

HEAD = {
    "Host": "challenge.localhost:80",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
}

POST = {"pin": "gdaabxwh"}


def main():
    res = requests.post(URL, headers=HEAD, data=POST)
    print(res.text.strip())


if __name__ == "__main__":
    main()
