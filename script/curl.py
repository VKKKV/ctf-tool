import requests
import sys

for j in sys.stdin:
        j=j.strip()
        response=requests.get(f"http://192.168.0.109/shehatesme{j}")
        # print(f"http://192.168.0.109/shehatesme{j}")
        print(response.text)


