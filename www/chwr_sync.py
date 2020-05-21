import requests
import json
import getopt
import sys
import phonenumbers
import psycopg2
import psycopg2.extras
import pprint
from settings import config

cmd = sys.argv[1:]
opts, args = getopt.getopt(
    cmd, 'd:l:',
    ['district', 'list of districts'])

districtList = ""
for option, parameter in opts:
    if option == '-d':
        districtList = parameter
    if option == '-l':
        districtList = parameter


user = config['chwr_user']
passwd = config['chwr_password']


def format_msisdn(msisdn=None):
    """ given a msisdn, return in E164 format """
    assert msisdn is not None
    msisdn = msisdn.replace(' ', '')
    num = phonenumbers.parse(msisdn, getattr(config, 'country', 'UG'))
    is_valid = phonenumbers.is_valid_number(num)
    if not is_valid:
        return None
    return phonenumbers.format_number(
        num, phonenumbers.PhoneNumberFormat.E164)


def get_url(url, payload={}):
    res = requests.get(url, params=payload, auth=(user, passwd))
    return res.text


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

conn = psycopg2.connect(
    "dbname=" + config["db_name"] + " host= " + config["db_host"] + " port=" + config["db_port"] +
    " user=" + config["db_user"] + " password=" + config["db_passwd"])

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

districtNames = []
if districtList:
    for name in districtList.split(','):
        districtNames.append(name)

if not districtNames:
    cur.execute(
        "SELECT name FROM fcapp_locations WHERE type_id = (SELECT id FROM fcapp_locationtype "
        "WHERE name = 'district')")
    res = cur.fetchall()
    for district in res:
        districtNames.append(district['name'])

pprint.pprint(districtNames)
totalItems = 0
validItems = 0
invalidItems = 0

for item in districtNames:
    districtURL = config['chwr_baseurl'] + "&district={}".format(item.lower())
    response = get_url(districtURL)
    districtReportersJson = json.loads(response)
    records = districtReportersJson['entry']

    totalItems = len(records)

    for record in records:
        # print(record.keys())
        resource = record.get('resource')
        if resource:
            # print(resource)
            name = resource.get('name', [{}])[0].get('text')
            facilityName = resource.get('facility', {}).get('dhis_name', '')
            facilityUID = resource.get('facility', {}).get('dhis_uid', '')

            gender = resource.get('gender', '')
            district = resource.get('location', {}).get('district', '').title()
            subCounty = resource.get('location', {}).get('subCounty', '')
            parish = resource.get('location', {}).get('parish', '')
            village = resource.get('location', {}).get('village', '')

            dateOfBirth = resource.get('birthDate', '')
            telephone = ''
            urns = []
            altTelephone = ''
            for tel in resource.get('telecom', []):
                if tel.get('use') == 'mobile':
                    telephone = tel.get('value', '')
                    urns.append('tel:{}'.format(telephone))
                else:
                    altTelephone = tel.get('value')
                    urns.append('tel:{}'.format(altTelephone))

            nationalID = ''
            if resource.get('identifier', []):
                if resource.get('identifier')[0].get('id_type') == 'National ID':
                    nationalID = resource.get('identifier')[0].get('value')

            if not facilityName or not facilityUID or not urns or not district or \
                    not telephone or not format_msisdn(telephone):
                print("Missing Mandatory field")
                invalidItems += 1
                continue
            validItems += 1
            contact_params = {
                'urns': urns,
                'name': name.title(),
                'groups': [],
                'fields': {
                    'gender': gender,
                    'registered_by': 'mHeroAPI',
                    'type': 'VHT',
                    'facility': facilityName,
                    'facilityuid': facilityUID,
                    'district': district if district else '',
                    'sub_county': subCounty.title() if subCounty else '',
                    'parish': parish.title() if parish else '',
                    'village': village.title() if village else '',
                }
            }
            pprint.pprint(contact_params['urns'])

            contactsEndpoint = config['api_url'] + "contacts.json?"
            try:
                # Let's try getting the contact
                get_url = "{0}urn={1}".format(contactsEndpoint, "tel:" + telephone)
                # print(get_url)
                resp = get_request(get_url)
                json_resp = resp.json()
                if json_resp['results']:
                    url = "{0}uuid={1}".format(contactsEndpoint, json_resp['results'][0]['uuid'])
                    print("Reporter exits: [URL:{0}]".format(url))
                    post_data = json.dumps(contact_params)
                    resp = post_request(url, post_data)
                    # print(json_resp['results'])
                else:
                    print("Reporter missing in RapidPro: {}".format(contact_params['urns']))
                    post_data = json.dumps(contact_params)
                    resp = post_request(contactsEndpoint, post_data)
                    print(resp.text)
            except Exception as e:
                print("FAILED to call contacts API. Reason: {}".format(str(e)))
print("totalItems:{0} invalidItems:{1} validItems:{2}".format(totalItems, invalidItems, validItems))
conn.close()
