import web
import json
import pprint
from . import db
from app.tools.utils import get_basic_auth_credentials, auth_user
# from settings import config


class SecondaryReceivers:
    def GET(self):
        params = web.input(contact="")
        web.header("Content-Type", "application/json; charset=utf-8")
        username, password = get_basic_auth_credentials()
        r = auth_user(db, username, password)
        if not r[0]:
            web.header('WWW-Authenticate', 'Basic realm="Auth API"')
            web.ctx.status = '401 Unauthorized'
            return json.dumps({'detail': 'Authentication failed!'})
        print(params.contact)
        SQL = (
            "SELECT * FROM fcapp_get_secondary_receivers($contact)"
        )
        res = db.query(SQL, {'contact': params.contact})
        payload = {'secreceivers': {}}
        receivers_count = 0
        screen_1 = ""
        screen_2 = ""
        screen_3 = ""
        if res:
            for idx, r in enumerate(res, 1):
                receivers_count += 1
                if idx < 6:
                    screen_1 += "%s. %s\n" % (idx, r['name'])
                    payload['secreceivers']['%s' % idx] = {
                        'name': r['name'],
                        'uuid': r['uuid'],
                        'contact_field': r['contact_field']
                    }
                elif idx > 5 and idx < 11:
                    screen_2 += "%s. %s\n" % ((idx + 1), r['name'])
                    payload['secreceivers']['%s' % (idx + 1)] = {
                        'name': r['name'],
                        'uuid': r['uuid'],
                        'contact_field': r['contact_field']
                    }
                elif idx > 10 and idx < 16:
                    screen_3 += "%s. %s\n" % ((idx + 2), r['name'])
                    payload['secreceivers']['%s' % (idx + 2)] = {
                        'name': r['name'],
                        'uuid': r['uuid'],
                        'contact_field': r['contact_field']
                    }
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

        pprint.pprint(payload)

        return json.dumps(payload)
