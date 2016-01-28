from django.test import TestCase
import urllib.request
import urllib.parse

# Create your tests here.
peer_ip = '130.211.63.102'
url = 'http://%s:8615/overlay/peer/'%peer_ip
peer_data = {}
peer_data['node'] = 'cache-07'
peer_data['ip'] = '130.211.95.77'
update_data = urllib.parse.urlencode(peer_data)
data = update_data.encode('utf-8')

req = urllib.request.Request(url, data)
rsp = urllib.request.urlopen(req)
rspData = rsp.read()
print(rspData)
