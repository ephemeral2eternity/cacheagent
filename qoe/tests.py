from django.test import TestCase
import urllib.request
import urllib.parse

def update_qoe(srv_ip, qoe_dict):
	url = 'http://%s:8615/qoe/update?'%cache_agent_ip
	params = urllib.parse.urlencode(qoe_dict)
	url = url + params

	req = urllib.request.Request(url)
	rsp = urllib.request.urlopen(req)
	rsp_data = rsp.read()
	print(rsp_data)

# QoE dict
qoe_dict = {}
qoe_dict['srv'] = 'cache-08'
qoe_dict['qoe'] = '4.5'
qoe_dict['alpha'] = 0.5

## The cache agent to update qoe 
cache_agent_ip = '130.211.95.77'
update_qoe(cache_agent_ip, qoe_dict)
