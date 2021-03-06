import json
import socket
import re
import subprocess
import urllib.request
import urllib.parse
from overlay.models import Manager, Server, Peer
from video.video_utils import *
from qoe.qoe_utils import *
from monitor.cache_monitor import *
from overlay.ping import *

# ================================================================================
# Get the dictionary storing info about all cache agents
# @return : dictionary storing info of all cache agents
#	    keys are denoting name, zone, type, ip of all cache agents
# ================================================================================
def get_cache_agents():
	managers = Manager.objects.all()
	manager_count = managers.count()
	if manager_count > 0:
		lastManager = managers[manager_count - 1]
		manager_ip = lastManager.ip
		url = 'http://%s:8000/overlay/node/'%manager_ip
		try:
			req = urllib.request.Request(url)
			rsp = urllib.request.urlopen(req, timeout=10)
			rsp_headers = rsp.info()
			cache_agents = json.loads(rsp_headers['Params'])
			print(cache_agents)
			return cache_agents
		except:
			print("Cannot connect the manager ", manager_ip, " to obtain the cache agents!")
			return None
	else:
		print("There is no existing manager configured!")
		return None
	
# ================================================================================
# Get all cache agent names as a list
# ================================================================================
def get_cache_agent_names():
	nodes = get_cache_agents()
	agent_names = nodes.keys()
	return agent_names

# ================================================================================
# Get all IP addresses of all cache agents
# @return : dictionary storing ip addresses for all cache agents
# 	    key ---- the cache agent name
# 	    value ---- the cache agent ip
# ================================================================================
def get_cache_agent_ips():
        cache_agents = get_cache_agents()
        return cache_agents

# ================================================================================
# Get an IP addresses of one cache agent
# @input : the node name to get an IP address
# @return : IP address of node "node_name"
# ================================================================================
def get_node_ip(node_name):
	all_agent_ips = get_cache_agent_ips()
	return all_agent_ips[node_name]

# ================================================================================
# Get the local host name
# ================================================================================
def get_host_name():
	return str(socket.gethostname())

# ================================================================================
# Initialize the overlay table
# ================================================================================
def init_overlay_table():
	# Initialize the video cache table first
	# init_cache_table()
	

	# Delete all objects in the table
	existing_srvs = Server.objects.all()
	if existing_srvs.count() > 0:
		existing_srvs.delete()
	cache_srv_ips = get_cache_agents()
	print(cache_srv_ips)
	if not cache_srv_ips:
		return False
	hostname = get_host_name()
	print("Obtained cache_srv_ips are", cache_srv_ips)
	print("Current host name is :", hostname)
	for srv in cache_srv_ips.keys():
		srv_id = int(re.findall(r'\d+', srv)[0])
		srv_name = srv
		srv_ip = cache_srv_ips[srv]
		srv_rtt = getMnRTT(srv_ip, 5)
		srv_sqs = 4.00
		srv_load = 0
		srv_bw = 0.00
		isLocal = (srv == hostname)
		if isLocal:
			srv_rtt = 0.0
			srv_sqs = 5.00
		cur_srv = Server(id=srv_id, name=srv_name, ip=srv_ip, isLocal=isLocal, rtt=srv_rtt, ave_sqs=srv_sqs, exp_sqs=srv_sqs, load=srv_load, bw=srv_bw)
		cur_srv.save()
		print(srv_name, " is saved in the database!")
	
	# Initialize the qoe table
	initializeQoE()
	return True

# ================================================================================
# Query for available nodes in the overlay network
# ================================================================================
def get_overlay_nodes():
	print("Entering get_overlay_nodes() to get existing overlay nodes!")
	managers = Manager.objects.all()
	manager_count = managers.count()
	overlay_nodes = {}
	if manager_count > 0:
		lastManager = managers[manager_count - 1]
		manager_ip = lastManager.ip
		url = 'http://%s:8000/overlay/overlaynode/'%manager_ip
		try:
			req = urllib.request.Request(url)
			rsp = urllib.request.urlopen(req, timeout=10)
			rsp_headers = rsp.info()
			overlay_nodes = json.loads(rsp_headers['Params'])
			print(overlay_nodes)
		except:
			print("Cannot connect the manager ", manager_ip, " to obtain available overlay nodes!")
	else:
		print("There is no existing manager configured!")
	return overlay_nodes
	
	

# ================================================================================
# Notify the centralized manager
# ================================================================================
def add_overlay(node, to_connect=None):
	if to_connect is None:
		print("Entering add_overlay() to add " + node + " as the first node in the overlay!")
	else:
		print("Entering add_overlay() to connect" + node + " to " + to_connect + " in the overlay!")
	managers = Manager.objects.all()
	manager_count = managers.count()
	if manager_count > 0:
		lastManager = managers[manager_count - 1]
		manager_ip = lastManager.ip
		if to_connect is not None:
			url = 'http://%s:8000/overlay/add?src=%s&dst=%s' % (manager_ip, node, to_connect)
		else:
			url = 'http://%s:8000/overlay/add?src=%s' % (manager_ip, node)
		try:
			req = urllib.request.Request(url)
			rsp = urllib.request.urlopen(req, timeout=10)
			print(rsp)
			return True
		except:
			print("Cannot connect the manager ", manager_ip, " to add overlay nodes!")
	else:
		print("There is no existing manager configured!")
	return False
	


# ================================================================================
# Add the closest available agent as the peer agent
# ================================================================================
def connect_overlay():
	print("Entering connect_overlay()!")
	overlay_nodes = get_overlay_nodes()
	print("Back to connect_overlay()!")
	print("The current overlay nodes:" + str(overlay_nodes))
	myName = get_host_name()
	if overlay_nodes:
		other_srvs = []
		for node_name in overlay_nodes.keys():
			if node_name != myName:
				print("Read info for overlay node: " + node_name)
				cur_node_info = Server.objects.get(name=node_name)
				other_srvs.append(cur_node_info)
		other_srv_list = object2list(other_srvs)
		print("Overlay node detailed info: " + str(other_srv_list))
		# Find the closest node to peer with
	
		to_connect = find_closest(other_srv_list)
		while to_connect:
			if peer_with(to_connect):
				print("Successfull peer with agent: ", to_connect['name'])
				break
			else:
				other_srv_list = remove_dict_from_list(to_connect, other_srv_list)
				to_connect = find_closest(other_srv_list)
		
		if add_overlay(myName, to_connect['name']):
			for node in other_srvs:
				add_cur_node(node.ip)
			return True
	else:
		if add_overlay(myName):
			return True

	return False

# ================================================================================
# Remove a dict element from a dict list
# @input : to_del --- the dict element to delete
#          srv_list --- the server dict list
# ================================================================================
def remove_dict_from_list(to_del, srv_list):
	for i in range(len(srv_list)):
		if srv_list[i]['id'] == to_del['id']:
			del srv_list[i]
			break
	return srv_list

# ================================================================================
# Convert the list of objects to a list of dict
# ================================================================================
def object2list(srvs):
	srv_list = []
	for srv in srvs:
		cur_srv = {}
		cur_srv['id'] = srv.id
		cur_srv['name'] = srv.name
		cur_srv['ip'] = srv.ip
		cur_srv['rtt'] = srv.rtt
		srv_list.append(cur_srv)
	return srv_list

# ================================================================================
# Find the closest server to peer with
# ================================================================================
def find_closest(srvs):
	to_connect = None
	if len(srvs) > 0:
		to_connect = srvs[0]
	if len(srvs) > 1:
		for srv in srvs:
			if srv['rtt'] < to_connect['rtt']:
				to_connect = srv
	return to_connect

# ================================================================================
# Get the hop number from the current host to the IP adress
# @input : srv_ip ---- the ip address the traceroute is probing
# @return : the hop number to srv_ip
# ================================================================================
def get_hop_count(srv_ip):
	proc = subprocess.Popen(['traceroute', srv_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(stdout, stderr) = proc.communicate()
	hop_count = stdout.decode('ascii').count('\n') - 1
	return hop_count

# ================================================================================
# Peer with a peer node
# ================================================================================
def peer_with(peer):
	url = 'http://%s:8615/overlay/peer/'%peer['ip']
	cur_srv = Server.objects.filter(isLocal=True)[0]
	peer_data = {}
	peer_data['node'] = cur_srv.name
	peer_data['ip'] = cur_srv.ip
	encoded_peer_data = urllib.parse.urlencode(peer_data)
	data = encoded_peer_data.encode('utf-8')

	try:
		req = urllib.request.Request(url, data)
		rsp = urllib.request.urlopen(req,timeout=10)
		rsp_data = rsp.read()
		print(rsp_data)
		peer_name = peer['name']
		peer_id = peer['id']
		peer_ip = peer['ip']
		new_peer = Peer(id=peer_id, name=peer_name, ip=peer_ip)
		new_peer.save()
		print("Added new peer", peer_name, "to the agentPeer listi!")
		return True
	except:
		return False

# ================================================================================
# Delete a node from current Peer List
# ================================================================================
def del_peer(peer):
	to_del_peer_obj = Peer.objects.get(name=peer)
	if to_del_peer_obj:
		to_del_peer_obj.delete()

# ================================================================================
# Delete a server from current overlay table
# ================================================================================
def del_srv(srv):
	to_del_srv_obj = Server.objects.get(name=srv)
	if to_del_srv_obj:
		to_del_srv_obj.delete()

# ================================================================================
# Remove peering relationship with a remote node
# ================================================================================
def remove_peer_with(cur_node, peer_ip):
	url = 'http://%s:8615/overlay/remove?peer=%s'%(peer_ip, cur_node)
	try:
		req = urllib.request.Request(url)
		rsp = urllib.request.urlopen(req,timeout=10)
		print("Remove", cur_node, "from the remote peer agent's peer list!")
		return True
	except:
		return False

# ================================================================================
# Remove current node from a remote node's overlay table
# ================================================================================
def remove_srv(cur_node, remote_ip):
	url = 'http://%s:8615/overlay/remove?srv=%s'%(remote_ip, cur_node)
	try:
		req = urllib.request.Request(url)
		rsp = urllib.request.urlopen(req,timeout=10)
		print("Remove", cur_node, "from the remote peer agent's peer list!")
		return True
	except:
		return False

# ================================================================================
# Delete current node from all its peers
# ================================================================================
def delete_all_peers():
	# Get all peer nodes.
	all_peers = Peer.objects.all()
	cur_node_name = get_host_name()
	for peer in all_peers:
		remove_peer_with(cur_node_name, peer.ip)
		del_peer(peer.name)

# ================================================================================
# Delete current node from all other servers' overlay table
# ================================================================================
def delete_current_node():
	# Get all other nodes
	srvs = Server.objects.filter(isLocal=False)
	cur_node_name = get_host_name()
	for srv in srvs:
		remove_srv(cur_node_name, srv.ip)

# ================================================================================
# Delete current node from all other servers' overlay table and peer list
# ================================================================================
def delete_node():
	# Delete current node from all others' Server List
	delete_current_node()
	# Delete current node from all others peer list
	delete_all_peers()
	# Dump all monitored traces
	dump_monitor()
	# Dump all QoE traces
	dumpQoE()

# ================================================================================
# Add remote node to current overlay table
# @input : node_name ---- the name of remote node
# ================================================================================
def add_srv(node_name):
	if not Server.objects.filter(name=node_name).exists():
		hostname = get_host_name()
		srv_id = int(re.findall(r'\d+', node_name)[0])
		srv_name = node_name
		srv_ip = get_node_ip(node_name)
		srv_rtt = getMnRTT(srv_ip, 5)
		ave_sqs = 4.00
		exp_sqs = 4.00
		srv_load = 0
		srv_bw = 0.00
		isLocal = (node_name == hostname)
		if isLocal:
			srv_rtt = 0.0
			ave_sqs = 5.00
			exp_sqs = 5.00
		cur_srv = Server(id=srv_id, name=srv_name, ip=srv_ip, isLocal=isLocal, rtt=srv_rtt, qoe=srv_qoe, load=srv_load, bw=srv_bw)
		cur_srv.save()
	print(node_name, " is saved in the database!")

# ================================================================================
# Add current node to other servers' overlay table
# @input : srv_ip ---- the ip address of the remote agent to add current node on
# @return : True ---- Successfully add current node on remote agent's overlay table.
#	    False ---- Failed to add current node on remote agent's overlay table.
# ================================================================================
def add_cur_node(srv_ip):
	cur_node_name = get_host_name()
	url = 'http://%s:8615/overlay/add?srv=%s'%(srv_ip, cur_node_name)
	try:
		req = urllib.request.Request(url)
		rsp = urllib.request.urlopen(req,timeout=10)
		print("Add", cur_node, "to the remote server agent's overlay table!")
		return True
	except:
		return False
