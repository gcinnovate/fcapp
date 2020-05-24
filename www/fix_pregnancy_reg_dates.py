import requests
import json
import getopt
import sys
import pprint
from settings import config

cmd = sys.argv[1:]
opts, args = getopt.getopt(
    cmd, 'f:h',
    ['filepath', 'help'])

filename = ""
for option, parameter in opts:
    if option == '-f':
        filename = parameter
    if option == '-h':
        print(
            "python " + __file__ +
            " -f <file>\n\tfile should be a CSV of UUIDs and dates: UUID,DD-MM-YYYY HH24:MI")
        sys.exit(1)


def get_request(url):
    response = requests.get(url, headers={
        'Content-type': 'application/json',
        'Authorization': 'Token %s' % config['api_token']})
    return response


def post_request(url, data):
    response = requests.post(url, data=data, headers={
        'Content-type': 'application/json',
        'Authorization': 'Token %s' % config['api_token']})
    return response

contactsEndpoint = config["api_url"] + "contacts.json?"

with open(filename, 'r') as f:
    for l in f:
        uuid, regDate = l.strip().split(',')

        try:
            # Let's try getting the contact
            get_url = "{0}uuid={1}".format(contactsEndpoint, uuid)
            # print(get_url)
            resp = get_request(get_url)
            json_resp = resp.json()
            if json_resp['results']:
                print("Reporter exits: [URL:{0}]".format(get_url))
                pregRegDates = json_resp['results'][0]['fields'].get(
                    'dates_of_pregnancy_registrations')
                if pregRegDates and len(pregRegDates) >= 10:
                    registrationDates = pregRegDates + '|' + regDate
                else:
                    registrationDates = regDate

                updateParams = {
                    "fields": {'dates_of_pregnancy_registrations': registrationDates}
                }
                pprint.pprint(updateParams)
                post_data = json.dumps(updateParams)
                resp = post_request(get_url, post_data)
                print(resp.text)
        except Exception as e:
            print("FAILED to update contacts. Reason: {}".format(str(e)))
