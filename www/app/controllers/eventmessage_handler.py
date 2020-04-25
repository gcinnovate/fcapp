import web
import json
from . import db
from app.tools.utils import get_basic_auth_credentials, auth_user
from settings import config


class EventMessageForLanguage:
    def GET(self):
        params = web.input(offset="", lang="eng", campaign_type="")
        web.header("Content-Type", "application/json; charset=utf-8")
        # username, password = get_basic_auth_credentials()
        # r = auth_user(db, username, password)
        # if not r[0]:
        #     web.header('WWW-Authenticate', 'Basic realm="Auth API"')
        #     web.ctx.status = '401 Unauthorized'
        #     return json.dumps({'detail': 'Authentication failed!'})
        try:
            offset = int(params.offset)
        except:
            offset = 10000
            print("Invalid Offset: {}, Campaign Type: {}".format(params.offset, params.campaign_type))
            return json.dumps({'message': ''})
        if params.campaign_type == 'prebirth':
            campaign_uuid = config['prebirth_campaign']
        else:
            campaign_uuid = config['postbirth_campaign']

        SQL = (
            "SELECT \"offset\", CASE WHEN exist(message, $lang) AND length(message->$lang) > 1 THEN "
            "message->$lang ELSE message->'eng' END AS message "
            "FROM campaigns_campaignevent WHERE "
            "campaign_id = (SELECT id FROM campaigns_campaign WHERE uuid=$campaign) "
            "AND \"offset\"=$offset AND is_active='t';")
        res = db.query(SQL, {'lang': params.lang, 'campaign': campaign_uuid, 'offset': offset})
        if res:
            ret = res[0]
            return json.dumps({'message': ret['message']})
        return json.dumps({'message': ''})
