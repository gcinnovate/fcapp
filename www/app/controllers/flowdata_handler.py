import web
import json
from . import db
from app.tools.utils import get_basic_auth_credentials, auth_user
from tasks import save_flow_data, call_command
from settings import USE_OLD_WEBHOOK, CONTACT_CACHE_COMMAND


class FlowData:
    def POST(self):
        params = web.input(
            report_type="", district="", facility="", subcounty="", village="", msisdn="")
        # web.header("Content-Type", "application/json; charset=utf-8")
        # username, password = get_basic_auth_credentials()
        # r = auth_user(db, username, password)
        # if not r[0]:
        #     web.header('WWW-Authenticate', 'Basic realm="Auth API"')
        #     web.ctx.status = '401 Unauthorized'
        #     return json.dumps({'detail': 'Authentication failed!'})

        request_args = {
            'msisdn': params.msisdn,
            'report_type': params.report_type,
            'district': params.district,
            'subcounty': params.subcounty,
            'facility': params.facility,
            'facilityuid': params.facilityuid,
        }
        if not USE_OLD_WEBHOOK:
            values = json.loads(web.data())
            results = values.get('results', {})
            save_flow_data.delay(request_args, results)
        else:
            values = json.loads(params['values'])
            save_flow_data.delay(request_args, values)

        return json.dumps({'message': 'success'})


class CacheContact:
    def GET(self, contact_uuid):

        def invalid_command(arg):
            import re
            unwanted_regex = r'(rm|sudo|mv|\||mkfs|>|cp\s|chmod|chown|wget|shred|dd|gunzip)'
            matches = re.match(unwanted_regex, arg)
            if matches:
                print("MATCHES")
                return True
            return False

        if len(contact_uuid) < 36 or invalid_command(contact_uuid):
            print("LEN:", len(contact_uuid), " ", invalid_command(contact_uuid))
            return json.dumps({"message": "failed"})

        cmd = CONTACT_CACHE_COMMAND + " -u {}".format(contact_uuid)
        print(cmd)
        call_command.delay(cmd)
        return json.dumps({"message": "success"})
