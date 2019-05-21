# -*- coding: utf-8 -*-

"""Mako template options which are used, basically, by all handler modules in
controllers of the app.
"""

# from web.contrib.template import render_mako
import web
import datetime
from web.contrib.template import render_jinja
from settings import (absolute, config)
import pprint

db_host = config['db_host']
db_name = config['db_name']
db_user = config['db_user']
db_passwd = config['db_passwd']
db_port = config['db_port']

db = web.database(
    dbn='postgres',
    user=db_user,
    pw=db_passwd,
    db=db_name,
    host=db_host,
    port=db_port
)

SESSION = ''
APP = None

regionDistricts = {}
rs = db.query("SELECT name FROM fcapp_regions")
for r in rs:
    region = r['name']
    ret = db.query(
        "SELECT name from fcapp_locations where id in (select unnest(districts) "
        "FROM fcapp_regions WHERE name = $region) ORDER BY name", {'region': region})
    payload = {'districts': {}}
    dlist = []
    screen_1 = ""
    screen_2 = ""
    for idx, d in enumerate(ret, 1):
        dlist.append(d["name"])
        if idx < 10:
            screen_1 += "%s. %s\n" % (idx, d['name'])
            payload['districts']['%s' % idx] = d['name']

        elif idx > 10 and idx < 20:
            screen_2 += "%s. %s\n" % ((idx + 1), d['name'])
            payload['districts']['%s' % idx] = d['name']

    payload['district_list'] = ','.join(dlist)
    if screen_2:
        screen_1 += "11. More\n"
        screen_2 += "0. Back"

    payload['screen_1'] = screen_1
    payload['screen_2'] = screen_2

    if region not in regionDistricts:
        regionDistricts['%s' % region] = payload

districtSubcounties = {}
rs = db.query("SELECT id, name FROM fcapp_locations WHERE level = 2 ORDER BY name")
for r in rs:
    district = r['name']
    payload = {'subcounties': {}}
    ret = db.query(
        "SELECT name FROM fcapp_locations WHERE tree_parent_id = $id", {'id': r['id']})
    slist = []
    screen_1 = ""
    screen_2 = ""
    screen_3 = ""
    for idx, s in enumerate(ret, 1):
        if idx in (11, 21):
            slist.append('#')
            slist.append(s['name'])
        else:
            slist.append(s['name'])
        if idx < 11:
            screen_1 += "%s. %s\n" % (idx, s['name'])
            payload['subcounties']['%s' % idx] = s['name']

        elif idx > 10 and idx < 21:
            screen_2 += "%s. %s\n" % ((idx + 1), s['name'])
            payload['subcounties']['%s' % (idx + 1)] = s['name']
        elif idx > 20 and idx < 31:
            screen_3 += "%s. %s\n" % ((idx + 2), s['name'])
            payload['subcounties']['%s' % (idx + 2)] = s['name']

    if screen_2:
        screen_1 += "11. More\n"
        screen_2 += "0. Back"
    if screen_3:
        screen_2 += "21. More\n"
        screen_3 += "0. Back"

    payload['subcounty_list'] = ','.join(slist)
    payload['s_screen_1'] = screen_1
    payload['s_screen_2'] = screen_2
    payload['s_screen_3'] = screen_3

    if district not in districtSubcounties:
        districtSubcounties['%s' % district] = payload

pprint.pprint(regionDistricts)
# pprint.pprint(districtSubcounties)


def put_app(app):
    global APP
    APP = app


def get_app():
    global APP
    return APP


def get_session():
    global SESSION
    return SESSION


def datetimeformat(value, fmt='%Y-%m-%d'):
    if not value:
        return ''
    return value.strftime(fmt)


myFilters = {
    'datetimeformat': datetimeformat,
}

# Jinja2 Template options
render = render_jinja(
    absolute('app/views'),
    encoding='utf-8'
)

render._lookup.globals.update(
    ses=get_session(),
    year=datetime.datetime.now().strftime('%Y'),
)
render._lookup.filters.update(myFilters)


def put_session(session):
    global SESSION
    SESSION = session
    render._lookup.globals.update(ses=session)


def csrf_token():
    session = get_session()
    if 'csrf_token' not in session:
        from uuid import uuid4
        session.csrf_token = uuid4().hex
    return session.csrf_token


def csrf_protected(f):
    def decorated(*args, **kwargs):
        inp = web.input()
        session = get_session()
        if not ('csrf_token' in inp and inp.csrf_token == session.pop('csrf_token', None)):
            raise web.HTTPError(
                "400 Bad request",
                {'content-type': 'text/html'},
                """Cross-site request forgery (CSRF) attempt (or stale browser form).
<a href="/"></a>.""")  # Provide a link back to the form
        return f(*args, **kwargs)
    return decorated

render._lookup.globals.update(csrf_token=csrf_token)


def require_login(f):
    """usage
    @require_login
    def GET(self):
        ..."""
    def decorated(*args, **kwargs):
        session = get_session()
        if not session.loggedin:
            session.logon_err = "Please Logon"
            return web.seeother("/")
        else:
            session.logon_err = ""
        return f(*args, **kwargs)

    return decorated
