from settings import config
import sys
import requests
# import json
import simplejson
import psycopg2
import psycopg2.extras
import datetime
import getopt

cmd = sys.argv[1:]
opts, args = getopt.getopt(cmd, 'g:f:', [])
group = ''
filename = ''
for option, parameter in opts:
    if option == '-g':
        group = parameter
    if option == '-f':
        filename = parameter

conn = psycopg2.connect(
    "dbname=" + config["db_name"] + " host= " + config["db_host"] + " port=" + config["db_port"] +
    " user=" + config["db_user"] + " password=" + config["db_passwd"])
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


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


def get_year_month_quarter(dtime_obj):
        current_quarter = int(round((dtime_obj.month - 1) / 3 + 1))
        year = dtime_obj.year
        month = '{0}-{1:02}'.format(year, dtime_obj.month)
        qt_str = '{0}Q{1}'.format(year, current_quarter)
        return year, month, qt_str

year, month, quarter = get_year_month_quarter(datetime.datetime.now())
requestArgsFields = ['msisdn', 'district', 'facility', 'facilityuid', 'sub_county', 'parish', 'village']
requiredFields = [
    'lmp', 'edd', 'name', 'dob_child_1', 'dob_child_2', 'dob_child_3', 'facility', 'secreceiver_msisdn', 'hoh_msisdn',
    'last_baby_trigger', 'optout_date', 'optout_reason', 'type', 'secreceivertype', 'registered_by',
    'preferred_language', 'gender', 'uuid', 'mother_name', 'last_baby_trigger', 'self_registerd'
]

allDistrictsByName = {}
cur.execute("SELECT id, name FROM  fcapp_locations WHERE level = 2 ORDER BY name")
rs = cur.fetchall()
for r in rs:
    allDistrictsByName[r['name']] = r['id']

# FLOW_DATA_API = 'http://localhost:9191/flowdata'
contactsUrl = config["api_url"] + "contacts.json?"
if group:
    contactsUrl += "group={}".format(group)
print(contactsUrl)

with open(filename, 'r') as f:
    for l in f:
        uuid = l.strip()
        if '&' not in contactsUrl:
            contactsUrl += '&uuid={}'.format(uuid)
        response = get_request(contactsUrl)
        contacts = response.json()
        for contact in contacts["results"]:
            request_args = {}
            values = {}

            values["name"] = contact["name"]
            values["created_on"] = contact["created_on"]
            values["modified_on"] = contact["modified_on"]

            request_args["contact_uuid"] = contact["uuid"]
            request_args["report_type"] = "contacts"
            request_args["msisdn"] = ''
            request_args["call_from_script"] = True

            if (len(contact["urns"]) > 0):
                request_args["msisdn"] = contact["urns"][0].replace('tel:', '')

            for key, val in contact["fields"].items():
                if key in requestArgsFields:
                    request_args[key] = '{}'.format(val) if val else ''
                if key in requiredFields:
                    values[key] = '{}'.format(val) if val else ''
            # print(values)
            # print(request_args)
            print("======>", request_args)
            # requests.post(FLOW_DATA_API, params=request_args, data=json.dumps(values))

            district_id = allDistrictsByName.get(request_args.get('district'), None)
            district_operater = '=' if district_id else 'IS'
            SQL = ("SELECT id FROM fcapp_flow_data WHERE district %s " % district_operater)
            SQL += (
                " %s AND facilityuid = %s AND msisdn=%s "
                "AND report_type = %s AND contact_uuid = %s"
            )
            cur.execute(SQL, [
                district_id, request_args.get('facilityuid'),
                request_args.get('msisdn'), 'contacts', request_args.get('contact_uuid')])
            res = cur.fetchone()
            if res:
                rpt_id = res['id']
                cur.execute(
                    "UPDATE fcapp_flow_data SET values=%s, updated= NOW() WHERE id = %s", [
                        psycopg2.extras.Json(values, dumps=simplejson.dumps), rpt_id])
            else:
                cur.execute(
                    "INSERT INTO fcapp_flow_data (msisdn, contact_uuid, district, facility, facilityuid, subcounty, parish,"
                    "village, report_type, values, year, month) "
                    "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)", [
                        request_args['msisdn'], request_args['contact_uuid'],
                        district_id, request_args['facility'], request_args['facilityuid'],
                        request_args['sub_county'], request_args['parish'], request_args['village'],
                        'contacts', psycopg2.extras.Json(values, dumps=simplejson.dumps),
                        year, month
                    ]
                )
            conn.commit()
conn.close()
