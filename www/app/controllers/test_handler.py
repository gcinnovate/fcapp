import web
import json
# from . import db
# from app.tools.utils import get_basic_auth_credentials, auth_user
# from settings import config


class Test:
    def GET(self):
        params = web.input()
        web.header("Content-Type", "application/json; charset=utf-8")

        return json.dumps({'success': 'true'})
