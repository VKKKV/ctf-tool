import requests

URL = "http://localhost/"

# HEAD = {
#     "Host": "challenge.localhost:80",
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
# }


def step():
    s = requests.Session()
    # 第一步，即使不自动跳转，Session 也会把 Cookie 记住
    s.get("http://localhost/")
    # 第二步，带着刚才记住的 Cookie 去访问目标
    print(s.get("http://localhost/").text)


def main():
    res = requests.post(URL)
    print(res.text.strip())


if __name__ == "__main__":
    main()
    main()
    main()
    main()
