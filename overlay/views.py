import re
import urllib
import json
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from overlay.models import Manager, Server, Peer
from overlay.overlay_utils import *
from overlay.ping import *
from video.video_utils import *

# Create your views here.
# The page returned for the request: http://cache_agent_ip:port/overlay/
def index(request):
	lastManager = Manager.objects.order_by('-pk')[0]
	return HttpResponse("The latest manager obtained is :" + lastManager.ip + ". Please check if the manager is on!")

def initManager(request):
	# Get the centralized manager and save it to Overlay Model.
	url = request.get_full_path()
	params = url.split('?')[1]
	print("Got manager ip address as: ", params)
	newManager = Manager(ip=params)
	newManager.save()
	num_manager = Manager.objects.all().count()
	return HttpResponse('Successfully update monitored new manager ip ' + params + "; Now Manager has " + str(num_manager) + " used managers!")

@csrf_exempt
def initServer(request):
	isSuccess = init_overlay_table()

	if not isSuccess:
		return HttpResponse("Not able to obtain the cache agent list. Please initialize the centralized manager first!")

	return query(request)

def connect(request):
	# Delete all objects in the table Peer
	existing_peers = Peer.objects.all()
	if existing_peers.count() > 0:
		existing_peers.delete()
	isSuccess = connect_overlay()
	if isSuccess:
		peer_list = Peer.objects.all()
		peer_dict = {}
		for peer in peer_list:
			peer_dict[peer.name] = peer.ip
		rsp_str = "Successfully connected to the overlay network with peers: " + json.dumps(peer_dict)
	else:
		rsp_str = "Failed to connect to the overlay network!"
	return HttpResponse(rsp_str)


@csrf_exempt
def query(request):
	# Return the initialized servers
	srv_list = Server.objects.all()
	cur_srv = Server.objects.filter(isLocal=True)
	peer_list = Peer.objects.all()
	# print("The current host is:", cur_srv[0].name)
	templates = loader.get_template('overlay/servers.html')
	#context = RequestContext(request, {
	#				'curSrv' : cur_srv[0],
	#				'srvs' : srv_list,
	#				'peers' : peer_list,
	#})
	rsp = HttpResponse(templates.render({'curSrv' : cur_srv[0], 'srvs' : srv_list, 'peers' : peer_list}, request))
	rsp['agens-peers'] = ', '.join(peer.name for peer in peer_list)
	return rsp

@csrf_exempt
def update(request):
	url = request.get_full_path()
	params = url.split('?')[1]
	print("Got url with params: ", params)
	update_dict = urllib.parse.parse_qs(params)
	if 'srv' in update_dict.keys():
		srv = update_dict['srv'][0]
		print("Parse update_dict with server, ", srv)
		srv_obj = Server.objects.filter(name=srv)[0]
		if 'bw' in update_dict.keys():
			srv_obj.bw = float(update_dict['bw'][0])
		elif 'load' in update_dict.keys():
			srv_obj.load = int(update_dict['load'][0])
		elif 'qoe' in update_dict.keys():
			srv_obj.exp_sqs = float(update_dict['qoe'][0])
		else:
			print('Unrecognized update parameters in ', params)
		srv_obj.save()
	else:
		print('Update messages needs to denote the server name in ', params)
		raise Http404
	return HttpResponse('Successfully update monitored value in overlay table!')

@csrf_exempt
def peer(request):
	# Answer the peer request from an node
	if request.method == "POST":
		print("overlay/peer request:", request.POST)
		print("overlay/peer request keys:", request.POST.keys())
		peer_node = request.POST.get("node", "")
		print("node info in request:", peer_node)
		peer_id  = int(re.findall(r'\d+', peer_node)[0])
		peer_ip = request.POST.get("ip", "")
		print("ip info in request:", peer_ip)
		new_peer = Peer(id=peer_id, name=peer_node, ip=peer_ip)
		new_peer.save()
		return HttpResponse("Successfully peering with agent " + get_host_name() + ".")
	elif request.method == "GET":
		print("The requested url is: ", request.get_full_path())
		return HttpResponse("Please use POST method to peer with an agent when using http://cache_agent:port/overlay/peer/.")

# ===========================================================================================================
# Remove a certain item from overlay table or from peer list
# @input: request ---- http://cache_agent_ip:8615/overlay/remove?srv=srvName
#	  		remove server item named srvName from current overlay table
# 		       http://cache_agent_ip:8615/overlay/remove?peer=peerName
#	  		remove peer item named peerName from current peer list
# ===========================================================================================================
@csrf_exempt
def delete_obj(request):
	http_rsp_str = ""
	url = request.get_full_path()
	params = url.split('?')[1]
	print("Got url with params: ", params)
	to_delete_dict = urllib.parse.parse_qs(params)
	if 'peer' in to_delete_dict.keys():
		to_del_peer = to_delete_dict['peer'][0]
		del_peer(to_del_peer)
	if 'srv' in to_delete_dict.keys():
		to_del_srv = to_delete_dict['srv'][0]
		del_srv(to_del_srv)
		
	num_peers = Peer.objects.all().count()
	if num_peers <= 0:
		connect_overlay()
	
	return query(request)

@csrf_exempt
def delete(request):
	delete_node()
	return HttpResponse("Successfully delete current node from all peers' peer list and server list! The node is free to be destroyed!")

@csrf_exempt
def add(request):
	url = request.get_full_path()
	params = url.split('?')[1]
	print("Got url with params: ", params)
	to_add_dict = urllib.parse.parse_qs(params)
	if 'srv' in to_add_dict.keys():
		to_add_srv = to_add_dict['srv'][0]
		add_srv(to_add_srv)
	
	return query(request)
