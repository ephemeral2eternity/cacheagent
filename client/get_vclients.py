import re
import apache_log_parser
import datetime
import socket
from django.utils.timezone import utc
from pprint import *
from client.models import VClient

def get_vclients():
	fileName = '/var/log/apache2/access.log'
	line_parser = apache_log_parser.make_parser("%h %l %u %t \"%r\" %>s %O")
	line_count = 100
	curLn = 0
	for line in reversed(open(fileName).readlines()):
		if curLn <= line_count:
			## print(line)
			log_line_data = line_parser(line)
			## pprint(log_line_data)
			cur_ip = log_line_data['remote_host']

			## Get name for the client
			cur_name_obj = socket.gethostbyaddr(cur_ip)
			if len(cur_name_obj) > 0:
				cur_name = cur_name_obj[0]
			else:
				cur_name = cur_ip

			## Get recent client to database
			cur_request = log_line_data['request_url']
			cur_time = log_line_data['time_received_datetimeobj'].replace(tzinfo=utc)
			if "m4f" in cur_request:
				# print(cur_ip + ", " + cur_request + ", " + str(cur_time))
				num_results = VClient.objects.filter(ip=cur_ip).count()
				if num_results > 0:
					cur_obj = VClient.objects.filter(ip=cur_ip)[0]
					if cur_obj.last_visit < cur_time:
						cur_obj.last_visit = cur_time
						cur_obj.name = cur_name
						print("[UPDATE]:" + cur_ip + ", " + cur_request + ", " + str(cur_time))
				else:
					cur_obj = VClient(name=cur_name, ip=cur_ip, last_visit=cur_time)
				cur_obj.save()
				
		else:
			break
		curLn = curLn + 1 
