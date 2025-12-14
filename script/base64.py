import sys
import base64

for i in sys.stdin:
    i=i.strip()
    print(base64.b64encode(i.encode()).decode())

