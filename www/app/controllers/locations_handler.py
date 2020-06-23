import web
import json
# import pprint
from . import db, regionDistricts, districtSubcounties
from app.tools.utils import get_webhook_msg_old
# from settings import config


class SubRegionDistricts:
    def POST(self, region):
        # params = web.input()
        web.header("Content-Type", "application/json; charset=utf-8")
        if region in regionDistricts:
            return json.dumps(regionDistricts[region])

        return json.dumps({})


class DistrictSubcounties:
    def POST(self, district):
        # params = web.input()
        web.header("Content-Type", "application/json; charset=utf-8")
        if district in districtSubcounties:
            x = json.dumps(districtSubcounties[district])
            # print(x)
            # print(len(x))
            web.header("Content-Length", len(x))
            return x
        return json.dumps({})
