from django.test import TestCase
import urllib.parse, urllib.request

# ================================================================================
# Send most recent monitored value obj to remote server by overlay/update url
# @input : srv_ip ---- remote server ip
#          monitored_dict ---- the dict of monitored value
#                              { 'srv' : cur_host, 'load/bw' : most recent monitored value}
# ================================================================================
def update_overlay_obj(srv_ip, monitored_dict):
        url = 'http://%s:8615/overlay/update?'%srv_ip
        params = urllib.parse.urlencode(monitored_dict)
        url = url + params

        req = urllib.request.Request(url)
        rsp = urllib.request.urlopen(req)
        rsp_data = rsp.read()
        print(rsp_data)

# Test update_overlay_obj defined in cache_monitor.py
srv = 'cache-09'
bw = 2.0

bw_dict = {}
bw_dict['srv'] = srv
bw_dict['bw'] = bw

## send update to cache-08
srv_ip = '130.211.63.102'

update_overlay_obj(srv_ip, bw_dict)
