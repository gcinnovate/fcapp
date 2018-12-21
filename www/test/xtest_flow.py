import requests
import time
import random
import getopt
import sys

cmd = sys.argv[1:]
opts, args = getopt.getopt(
    cmd, 'n:m:h',
    ['number', 'message'])


def usage():
    return """usage: python xtest_flow.py [-n <number>] [-m <message>] [-h]
    -n telephone number to test with
    -m message to test with
    -h Show this message
    """

telephone = "256753475676"
message = "leka"
for option, parameter in opts:
    if option == '-n':
        telephone = parameter
    if option == '-m':
        message = parameter.strip()
    if option == '-h':
        print(usage())
        sys.exit(1)

t = int(time.time())
i = random.randint(0, 10000)
URL = (
    "http://localhost:8000/handlers/kannel/receive/1e43787d-faf6-48ed-ad83-0fd1123738df/?"
    # "backend=yo&sender=256774225325&message=gc test&ts=%s&id=%s" % (t, i))
    "backend=yo&sender=%s&message=%s&ts=%s&id=%s" % (telephone, message, t, i))
print(URL)
res = requests.post(URL)
print(res.text)
