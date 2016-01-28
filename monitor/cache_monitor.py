## This agent is used to monitor the load, outbound bw and user demand on current cache agent
# Chen Wang, Feb. 12, 2015
# chenw@cmu.edu
# cache_monitor.py
import json
import string,cgi,time
import sys
import os
import shutil
import socket
import ntpath
import codecs
import subprocess
import urllib.request, urllib.parse
from monitor.models import Load, BW, RTTS, SYS_STAT
from monitor.gcs_upload import *
from overlay.models import Server

# ================================================================================
# Monitor video server load in last 1 minute. 
# User load is monitored by the number of chunk requests in 1 minute
# ================================================================================
def load_monitor():
	load_list = Load.objects.all()
	load_list_len = load_list.count()
	if load_list_len <= 0:
		total_load = get_load()
		load_diff = 0
	else:
		print("[Django_crontab] Add load monitored!")
		previous_item = Load.objects.all()[load_list_len - 1]
		print("[Django_crontab] Previous Total Load: " + str(previous_item.total))
		total_load = get_load()
		print("[Django_crontab] Current Total Load: " + str(total_load))
		load_diff = total_load - previous_item.total
		print("[Django_crontab] Current Load: " + str(load_diff))
	cur_load = Load(load=load_diff, total=total_load)
	cur_load.save()
	update_overlay_load(load_diff)
	print("[Django_crontab] Finished updating new load to all other servers!")

# ================================================================================
# Monitor video server's system stats in last period. 
# System statistics include cpu_util, mem_util, io_tps, io_readblks, io_writeblks
# inbound_traffic, outbound_traffic, total_io_read, total_io_write, total_tx_bytes
# total_rx_bytes
# ================================================================================
def sys_monitor():
	sys_stat_list = SYS_STAT.objects.all()
	sys_stat_list_len = sys_stat_list.count()
	cpu_util = get_cpu()
	mem_util = get_mem()
	io_tps = get_io_tps()
	io_readblks = get_io_readblks()
	io_writeblks = get_io_writeblks()
	total_io_read = get_io_read_bytes()
	total_io_write = get_io_write_bytes()
	tx_bytes = get_tx_bytes()
	rx_bytes = get_rx_bytes()
	if sys_stat_list_len <= 0:
		inbound_traffic = 0.0
		outbound_traffic = 0.0
	else:
		previous_stat = SYS_STAT.objects.all()[sys_stat_list_len - 1]
		previous_ts = time.mktime(previous_stat.time.timetuple())
		seconds_elapsed = time.time() - previous_ts
		inbound_traffic = float(rx_bytes - previous_stat.total_rx_bytes) * 8 / float(seconds_elapsed * 1000.0)
		outbound_traffic = float(tx_bytes - previous_stat.total_tx_bytes) * 8 / float(seconds_elapsed * 1000.0)
	cur_sys_stat = SYS_STAT(cpu_util=cpu_util, mem_util=mem_util, io_tps=io_tps, io_readblks=io_readblks, io_writeblks=io_writeblks, \
				inbound_traffic=inbound_traffic, outbound_traffic=outbound_traffic, total_io_read=total_io_read, \
				total_io_write=total_io_write, total_tx_bytes=tx_bytes, total_rx_bytes=rx_bytes)
	cur_sys_stat.save()
	print("[Django_crontab] Finished updating new sys_stat in the database!")

# ================================================================================
# Save the updated load in the overlay table 
# ================================================================================
def update_overlay_load(load):
	cur_srv = get_host_name()
	print("[Django_crontab] It is inside update_overlay_load!")

	## Update load on local server
	cur_srv_obj = Server.objects.filter(isLocal=True)[0]
	cur_srv_obj.load = load
	cur_srv_obj.save()
	print("[Django_crontab] Finished saving new load to local server, ", cur_srv_obj.name)

	## Update other servers about local load
	load_dict = {}
	load_dict['srv'] = cur_srv
	load_dict['load'] = load

	## Send update url to all other servers
	other_srvs = Server.objects.filter(isLocal=False)
	for other_srv in other_srvs:
		other_srv_ip = other_srv.ip
		print('Update monitored load', load_dict, ' to server ', other_srv.name)
		update_overlay_obj(other_srv_ip, load_dict)

# ================================================================================
# Probe outbound traffic every 1 minutes. 
# ================================================================================
def bw_monitor():
	bw_list = BW.objects.all()
	bw_list_len = bw_list.count()
	if bw_list_len <= 0:
		cur_tx = get_tx_bytes()
		cur_bw = 0
	else:
		print("[Django_crontab] Add bw monitored!")
		previous_obj = BW.objects.all()[bw_list_len - 1]
		previous_ts = time.mktime(previous_obj.time.timetuple())
		seconds_elapsed = time.time() - previous_ts
		cur_tx = get_tx_bytes()
		cur_bw = float(cur_tx - previous_obj.tx) * 8 / seconds_elapsed
		print("[Django_crontab] Most Recent BW monitored:", str(cur_bw))
	cur_bw_obj = BW(bw=cur_bw, tx=cur_tx)
	cur_bw_obj.save()
	update_overlay_bw(cur_bw)

# ================================================================================
# Save the updated bw in the overlay table 
# ================================================================================
def update_overlay_bw(bw):
	cur_srv = get_host_name()

	## Update bw on local server
	cur_srv_obj = Server.objects.filter(isLocal=True)[0]
	cur_srv_obj.bw = bw
	cur_srv_obj.save()

	## Update other servers about local load
	bw_dict = {}
	bw_dict['srv'] = cur_srv
	bw_dict['bw'] = bw

	## Send update url to all other servers
	other_srvs = Server.objects.filter(isLocal=False)
	for other_srv in other_srvs:
		other_srv_ip = other_srv.ip
		print('Update monitored bw', bw_dict, ' to server ', other_srv.name)
		update_overlay_obj(other_srv_ip, bw_dict)

# ================================================================================
# Send most recent monitored value obj to remote server by overlay/update url
# @input : srv_ip ---- remote server ip
#	   monitored_dict ---- the dict of monitored value
#			       { 'srv' : cur_host, 'load/bw' : most recent monitored value}
# ================================================================================
def update_overlay_obj(srv_ip, monitored_dict):
	url = 'http://%s:8615/overlay/update?'%srv_ip
	params = urllib.parse.urlencode(monitored_dict)
	url = url + params

	try:
		req = urllib.request.Request(url)
		rsp = urllib.request.urlopen(req)
		rsp_data = rsp.read()
		print(rsp_data)
	except:
		return

# ================================================================================
# Dump the monitored load and bw to google cloud storage gs://agens-data/
# ================================================================================
def dump_monitor():
        ## Dump the load objects
        all_load = Load.objects.all()
        load_cnt = all_load.count()
        all_bw = BW.objects.all()
        bw_cnt = all_bw.count()
        all_rtts = RTTS.objects.all()
        rtts_cnt = all_rtts.count()

        # export load objects to json file and only leave the most 10 recent objects
        load = {}
        n = 0
        for load_obj in all_load:
                cur_ts = int(time.mktime(load_obj.time.timetuple()))
                load[cur_ts] = int(load_obj.load)
                if n < load_cnt - 10:
                        load_obj.delete()
                n = n + 1

        # export bw objects to json file and only leave the most 10 recent objects
        bw = {}
        n = 0
        for bw_obj in all_bw:
                cur_ts = int(time.mktime(bw_obj.time.timetuple()))
                bw[cur_ts] = float(bw_obj.bw)
                if n < bw_cnt - 10:
                        bw_obj.delete()
                n = n + 1

        # export rtt objects to json file and only leave the most 10 recent objects
        rtts = {}
        n = 0
        for rtt_obj in all_rtts:
                cur_ts = int(time.mktime(rtt_obj.time.timetuple()))
                ## reader = codecs.getreader("utf-8")
                rtts[cur_ts] = json.loads(str(rtt_obj.rtts))
                if n < rtts_cnt - 10:
                        rtt_obj.delete()
                n = n + 1

        cur_file_path = os.path.realpath(__file__)
        cur_path, cur_file_name = ntpath.split(cur_file_path)
        cur_host_name = str(socket.gethostname())
        ts = time.strftime('%m%d%H%M')
        
        try:
                os.stat(cur_path + '/tmp/')
        except:
                os.mkdir(cur_path + '/tmp/')

        load_file = cur_path + '/tmp/' + cur_host_name + '_' + ts + '_load.json'
        bw_file = cur_path + '/tmp/' + cur_host_name + '_' + ts + '_bw.json'
        rtts_file = cur_path + '/tmp/' + cur_host_name + '_' + ts + '_rtts.json'

        with open(load_file, 'w') as outfile:
                json.dump(load, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        with open(bw_file, 'w') as outfile:
                json.dump(bw, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        with open(rtts_file, 'w') as outfile:
                json.dump(rtts, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        gcs_upload('agens-data', load_file)
        gcs_upload('agens-data', bw_file)
        gcs_upload('agens-data', rtts_file)
        return ts

# ================================================================================
# Get the number of http chunk requests in every 1 minute
# ================================================================================
def get_load():
	ln_num = -1
	with open('/var/log/apache2/access.log') as f:
		ln_num = len(f.readlines())
	return ln_num

# ================================================================================
# Read cpu utilization every period
# ================================================================================
def get_cpu():
	get_cpu_cmd = "top -b -n 1  | grep -E 'Cpu' | awk -F ',' '{print $4}' | awk '{print $1}' | awk -F '%' '{print $1}'"
	cpu_idle = float(subprocess.Popen(get_cpu_cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
	cpu_util = 100 - cpu_idle
	return cpu_util

# ================================================================================
# Read memory utilization every period
# ================================================================================
def get_mem():
	get_used_mem_cmd = "top -b -n 1 | grep -E 'Mem:' | cut -d ',' -f 2 | awk '{print $1}'"
	get_total_mem_cmd = "top -b -n 1 | grep -E 'Mem:' | cut -d ',' -f 1 | cut -d ':' -f 2 | awk '{print $1}'"
	total_mem = float(subprocess.Popen(get_total_mem_cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
	used_mem = float(subprocess.Popen(get_used_mem_cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
	mem_util = total_mem/used_mem
	return mem_util

# ================================================================================
# Read the number of transfers per second from iostat every period
# ================================================================================
def get_io_tps():
	get_io_tps_cmd = "iostat -d |grep 'sda' |awk '{print $2}'"
	io_tps = float(subprocess.Popen(get_io_tps_cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
	return io_tps

# ================================================================================
# Read the number of blocks read per second from iostat every period
# ================================================================================
def get_io_readblks():
	get_io_readblks_cmd = "iostat -d |grep 'sda' |awk '{print $3}'"
	io_readblks = float(subprocess.Popen(get_io_readblks_cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
	return io_readblks

# ================================================================================
# Read the number of blocks write per second from iostat every period
# ================================================================================
def get_io_writeblks():
	get_io_writeblks_cmd = "iostat -d |grep 'sda' |awk '{print $4}'"
	io_writeblks = float(subprocess.Popen(get_io_writeblks_cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
	return io_writeblks

# ================================================================================
# Read the total bytes read from iostat every period
# ================================================================================
def get_io_read_bytes():
	get_io_read_bytes_cmd = "iostat -d |grep 'sda' |awk '{print $5}'"
	io_read_bytes = int(subprocess.Popen(get_io_read_bytes_cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
	return io_read_bytes

# ================================================================================
# Read the total bytes written from iostat every period
# ================================================================================
def get_io_write_bytes():
	get_io_write_bytes_cmd = "iostat -d |grep 'sda' |awk '{print $5}'"
	io_write_bytes = int(subprocess.Popen(get_io_write_bytes_cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
	return io_write_bytes

# ================================================================================
# Read outbound bytes every 1 minute. 
# ================================================================================
def get_tx_bytes():
	file_txbytes = open('/sys/class/net/eth0/statistics/tx_bytes')
	lines = file_txbytes.readlines()
	tx_bytes = int(lines[0])
	file_txbytes.close()
	return tx_bytes

# ================================================================================
# Read inbound bytes every 1 minute. 
# ================================================================================
def get_rx_bytes():
	file_rxbytes = open('/sys/class/net/eth0/statistics/rx_bytes')
	lines = file_rxbytes.readlines()
	rx_bytes = int(lines[0])
	file_rxbytes.close()
	return rx_bytes

# ================================================================================
# Get current host name 
# ================================================================================
def get_host_name():
	return str(socket.gethostname())
