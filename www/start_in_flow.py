from settings import config
import sys
import requests
import json
import psycopg2
import psycopg2.extras
import getopt

cmd = sys.argv[1:]
opts, args = getopt.getopt(cmd, 'u:f:', [])
flowUUID = ''
filename = ''
for option, parameter in opts:
    if option == '-f':
        filename = parameter
    if option == '-u':
        flowUUID = parameter

conn = psycopg2.connect(
    "dbname=" + config["db_name"] + " host= " + config["db_host"] + " port=" + config["db_port"] +
    " user=" + config["db_user"] + " password=" + config["db_passwd"])
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def post_request(url, data):
    response = requests.post(url, data=data, headers={
        'Content-type': 'application/json',
        'Authorization': 'Token %s' % config['api_token']})
    return response


def get_request(url=config['default_api_uri']):
    response = requests.get(url, headers={
        'Content-type': 'application/json',
        'Authorization': 'Token %s' % config['api_token']})
    return response

# FLOW_DATA_API = 'http://localhost:9191/flowdata'
MAX_CHUNK_SIZE = 90
flowStartsUrl = config["api_url"] + "flow_starts.json?"

with open(filename, 'r') as f:
    contactUUIDs = ['%s' % u.strip() for u in f.readlines()]
    contacts_len = len(contactUUIDs)
    j = 0
    print("Starting {0} Contacts in Flow [uuid:{1}]".format(contacts_len, flowUUID))
    for i in range(0, contacts_len + MAX_CHUNK_SIZE, MAX_CHUNK_SIZE)[1:]:  # want to finsh batch right away
        chunk = contactUUIDs[j:i]
        params = {
            'flow': flowUUID,
            'contacts': chunk,
            'extra': {
            }
        }
        post_data = json.dumps(params)
        try:
            resp = post_request(flowStartsUrl, post_data)
            print(resp.text)
        except:
            print("ERROR Startig Flow [uuid: {0}]".format(flowUUID))
        j = i
    print("Finished Starting Contacts in Flow [uuid:{0}]".format(flowUUID))

    f.close()
conn.close()
