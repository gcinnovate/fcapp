import web
import json
import pprint
from . import db
from app.tools.utils import get_basic_auth_credentials, auth_user, get_webhook_msg_old
from settings import config
from temba_client.v2 import TembaClient


class StartBabyTriggerFlow:
    def POST(self):
        params = web.input()
        web.header("Content-Type", "application/json; charset=utf-8")
        username, password = get_basic_auth_credentials()
        r = auth_user(db, username, password)
        if not r[0]:
            web.header('WWW-Authenticate', 'Basic realm="Auth API"')
            web.ctx.status = '401 Unauthorized'
            return json.dumps({'detail': 'Authentication failed!'})

        client = TembaClient(config.get('familyconnect_uri', 'http://localhost:8000/'), config['api_token'])

        secreceivers = get_webhook_msg_old(params, 'secreceivers')
        pprint.pprint(secreceivers)
        payload = json.loads(secreceivers)

        optout_option = get_webhook_msg_old(params, 'OptOutOption')
        print("OptOutOption => ", optout_option)
        try:
            contact_details = payload['%s' % int(float(optout_option))]
        except:
            contact_details = None
        if not contact_details:
            return json.dumps({'success': 'False'})

        contact_id = contact_details['contact_id']
        contact_uuid = contact_details['uuid']
        print("contact_id=>", contact_id, " uuid => ", contact_uuid)

        try:
            client.create_flow_start(
                config['babytrigger_flow_uuid'],
                contacts=[contact_uuid],
                extra=None)
        except:
            pass

        return json.dumps({'success': 'True'})
