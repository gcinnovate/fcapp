import web
import json
import pprint
from . import db
from app.tools.utils import get_basic_auth_credentials, auth_user, get_webhook_msg_old
# from settings import config


class SecondaryReceivers:
    def GET(self):
        params = web.input(contact="", babytrigger="false")
        web.header("Content-Type", "application/json; charset=utf-8")
        username, password = get_basic_auth_credentials()
        r = auth_user(db, username, password)
        if not r[0]:
            web.header('WWW-Authenticate', 'Basic realm="Auth API"')
            web.ctx.status = '401 Unauthorized'
            return json.dumps({'detail': 'Authentication failed!'})
        print(params.contact)
        SQL = (
            "SELECT * FROM fcapp_get_secondary_receivers($contact) "
        )
        if params.babytrigger == "true":
            SQL += " WHERE has_msisdn = 'f'"

        res = db.query(SQL, {'contact': params.contact})
        payload = {'secreceivers': {}}
        receivers_count = 0
        screen_1 = ""
        screen_2 = ""
        screen_3 = ""
        # screen_1_len = 0
        # screen_2_len = 0
        # screen_3_len = 0
        if res:
            for idx, r in enumerate(res, 1):
                receivers_count += 1
                if idx < 6:
                    screen_1 += "%s. %s\n" % (idx, r['name'])
                    payload['secreceivers']['%s' % idx] = {
                        'name': r['name'],
                        'uuid': r['uuid'],
                        'contact_id': r['contact_id'],
                        'contact_field': r['contact_field']
                    }
                elif idx > 5 and idx < 11:
                    screen_2 += "%s. %s\n" % ((idx + 1), r['name'])
                    payload['secreceivers']['%s' % (idx + 1)] = {
                        'name': r['name'],
                        'uuid': r['uuid'],
                        'contact_id': r['contact_id'],
                        'contact_field': r['contact_field']
                    }
                elif idx > 10 and idx < 16:
                    screen_3 += "%s. %s\n" % ((idx + 2), r['name'])
                    payload['secreceivers']['%s' % (idx + 2)] = {
                        'name': r['name'],
                        'uuid': r['uuid'],
                        'contact_id': r['contact_id'],
                        'contact_field': r['contact_field']
                    }

        # screen_1_len = len(screen_1.strip().split('\n'))
        # screen_2_len = len(screen_2.strip().split('\n')) if screen_2 else 0
        # screen_3_len = len(screen_3.strip().split('\n')) if screen_3 else 0

        if screen_2:
            screen_1 += "6. More\n"
            screen_2 += "0. Back"
        if screen_3:
            screen_2 += "12. More\n"
            screen_3 += "0. Back"

        payload['receivers_count'] = receivers_count
        payload['screen_1'] = screen_1
        payload['screen_2'] = screen_2
        payload['screen_3'] = screen_3
        # payload['screen_1_len'] = screen_1_len
        # payload['screen_2_len'] = screen_2_len
        # payload['screen_3_len'] = screen_3_len

        pprint.pprint(payload)

        return json.dumps(payload)


class OptOutSecondaryReceiver:
    def POST(self):
        params = web.input(optoutall="false")
        web.header("Content-Type", "application/json; charset=utf-8")
        username, password = get_basic_auth_credentials()
        r = auth_user(db, username, password)
        if not r[0]:
            web.header('WWW-Authenticate', 'Basic realm="Auth API"')
            web.ctx.status = '401 Unauthorized'
            return json.dumps({'detail': 'Authentication failed!'})

        secreceivers = get_webhook_msg_old(params, 'secreceivers')
        pprint.pprint(secreceivers)
        payload = json.loads(secreceivers)
        if params.optoutall == "true":
            for k, v in payload.iteritems():
                contact_id = v['contact_id']
                contact_field = v['contact_field']
                db.query(
                    "UPDATE values_value SET (string_value, decimal_value) = ('', NULL) "
                    "WHERE contact_id = $contact_id AND contact_field_id = $contact_field_id", {
                        'contact_id': contact_id, 'contact_field_id': contact_field})
            return json.dumps({'success': 'true'})

        optout_option = get_webhook_msg_old(params, 'OptOutOption')
        print("OptOutOption => ", optout_option)

        try:
            contact_details = payload['%s' % int(float(optout_option))]
        except:
            contact_details = None
        if not contact_details:
            return json.dumps({'success': 'False'})

        contact_id = contact_details['contact_id']
        contact_field = contact_details['contact_field']
        print("contact_id=>", contact_id, " fields => ", contact_field)

        db.query(
            "UPDATE values_value SET (string_value, decimal_value) = ('', NULL) "
            "WHERE contact_id = $contact_id AND contact_field_id = $contact_field_id", {
                'contact_id': contact_id, 'contact_field_id': contact_field})

        return json.dumps({'success': 'True'})
