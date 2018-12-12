from temba_client.v2 import TembaClient
from settings import config
import requests
import json


def post_request(data, url=config['default_api_uri']):
    response = requests.post(url, data=data, headers={
        'Content-type': 'application/json',
        'Authorization': 'Token %s' % config['api_token']})
    return response


def get_request(url=config['default_api_uri']):
    response = requests.get(url, headers={
        'Content-type': 'application/json',
        'Authorization': 'Token %s' % config['api_token']})
    return response

client = TembaClient('http://127.0.0.1:8000/api/v2', '4be1f40cd248071d729bfbb2865b357e219d5d82')
# client = TembaClient('https://rapidpro.hub.familyconnect.co.ug/api/v2', '52f43be31934a9861058352860895b4cf2400b7c')
contact = {'name': 'Anita Kamanzi', 'urns': ["tel:+256702409503"]}
# contact2 = {"fields": {"sex": "M"}, "urns": ["tel:+256783800008", "tel:+256782900009"], "name": "Jerimiah Kyazze", "groups": ["VHT"]}
contact2 = {
    "fields": {
        "parish": "Mugoju",
        "type": "VHT",
        "district": "Yumbe",
        "facility": "Abiriamajo HC II",
        "gender": "M",
        "village": "Aliba",
        "facilityuid": "RnXpcMWI5Zu",
        "sub_county": "Odravu"
    }, "urns": ["tel:+256702409503"], "name": "Anita Agabax"}

resp = post_request(json.dumps(contact2))
print resp.text,
print resp.status_code
if resp.status_code == 400:
    resp2 = get_request(config['default_api_uri'] + "urn=%s" % contact2['urns'][0])

    xx = json.loads(resp2.text)
    print xx
    results = xx.get('results', '')
    print len(results)
    if results and len(results) < 2:
        uuid = results[0].get('uuid', '')
        print uuid
        respx = post_request(json.dumps(contact2), config['default_api_uri'] + "uuid=%s" % uuid)
        print "XXX", respx.text
# client.create_contact(name='Anita Kamazi', urns=["tel:+256702409503"])
# extras = {
#     'fields': {
#         "district": "Kampala", "name": "Dorothy Jacksons",
#         "subcounty": "Central Division", "village": "Nakulabye",
#         "facility": "Nakulabye HC II", "facilityuid": "wITceG8YRXg",
#         "state": "Buganda", "Type": "VHT", "action": "create", "sex": "M"
#     }
# }
# client.create_contact(**contact2)
# contacts = client.get_contacts().all()
# for c in contacts:
#     print c.name
# client.create_flow_start("a974dae1-53bf-4eb6-bcd9-941c50b6b362", urns=[u'tel:+256702409222', u'tel:+256702409111'], extra=extras)
# contacts = client.get_contacts().all()
# for c in contacts:
#    print c.name, c.urns, c.uuid
