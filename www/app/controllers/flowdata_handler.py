import web
import json
from . import db
from app.tools.utils import get_basic_auth_credentials, auth_user
from tasks import save_flow_data
from settings import USE_OLD_WEBHOOK


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
