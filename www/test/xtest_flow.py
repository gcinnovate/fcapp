import requests
import time
import random

t = int(time.time())
i = random.randint(0, 10000)
URL = (
    "http://localhost:8000/handlers/kannel/receive/1e43787d-faf6-48ed-ad83-0fd1123738df/?"
    "backend=yo&sender=256774225325&message=gc test&ts=%s&id=%s" % (t, i))
print(URL)
res = requests.post(URL)
print(res.text)
