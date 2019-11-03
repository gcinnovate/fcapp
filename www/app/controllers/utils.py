import requests
import json
import web
import re
import base64
from celeryconfig import config, USE_OLD_WEBHOOK


def get_webhook_msg_old(params, label='msg'):
    """Returns value of given lable from rapidpro webhook data"""
    values = json.loads(params['values'])  # only way we can get out Rapidpro values in webpy
    msg_list = [v.get('value') for v in values if v.get('label') == label]
    if msg_list:
        msg = msg_list[0].strip()
        if msg.startswith('.'):
            msg = msg[1:]
        return msg
    return ""


def get_webhook_msg(payload, label='msg'):
    """Returns value of given lable from rapidpro webhook data"""
    results = payload.get('results', {})
    msg_list = results.get(label, {})
    if msg_list:
        msg = msg_list.get('value', '').strip()
        if msg.startswith('.'):
            msg = msg[1:]
            return msg
    return ""


def post_request(data, url=""):
    response = requests.post(url, data=data, headers={
        'Content-type': 'application/json',
        'Authorization': 'Token %s' % config['api_token']})
    return response


def auth_user(db, username, password):
    sql = (
        "SELECT a.id, a.firstname, a.lastname, b.name as role "
        "FROM fcapp_users a, fcapp_user_roles b "
        "WHERE username = $username AND password = crypt($passwd, password) "
        "AND a.user_role = b.id AND is_active = 't'")
    res = db.query(sql, {'username': username, 'passwd': password})
    if not res:
        return False, "Wrong username or password"
    else:
        return True, res[0]


def get_basic_auth_credentials():
    auth = web.ctx.env.get('HTTP_AUTHORIZATION')
    if not auth:
        return (None, None)
    auth = re.sub('^Basic ', '', auth)
    username, password = base64.b64decode(auth).split(b':')
    return username.decode("utf-8"), password.decode("utf-8")


def get_request(url):
    response = requests.get(url, headers={
        'Content-type': 'application/json',
        'Authorization': 'Token %s' % config['api_token']})
    return response


def get_indicators_from_rapidpro_results(results, indicator_conf={}, report_type=None):
    report_type_indicators = indicator_conf.get(report_type, [])
    flow_inidicators = {}

    if not USE_OLD_WEBHOOK:
        for k, v in results.items():
            if k in report_type_indicators:
                try:
                    flow_inidicators[k] = int(results[k]['value'])
                except:
                    flow_inidicators[k] = results[k]['value']
    else:
        results_json = {}
        for v in results:
            val = v.get('value')
            try:
                val = int(float(val))
            except:
                pass
            label = v.get('label')
            results_json[label] = val
        for k, v in results_json.items():
            if k in report_type_indicators:
                flow_inidicators[k] = results_json[k]

    return flow_inidicators
