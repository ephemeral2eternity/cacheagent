## Read locally cached videos from folder vidlist
import socket
import os
import ntpath
import re
import urllib.request
import urllib.parse
import random
from overlay.models import Server, Peer
from video.models import Video

# ==============================================================
# Retrieve cache table from local file lists
# ==============================================================
def get_local_videos():
	full_path = os.path.realpath(__file__)
	cur_folder, cur_file = ntpath.split(full_path)
	vidlist_folder = cur_folder + '/vidlists/'
	hostname = get_local_name()

	vidlist_file = vidlist_folder + hostname
	f = open(vidlist_file, 'r')

	vidlist = []
	for line in f:
		vid_id = int(line)
		vidlist.append(vid_id)

	# print(vidlist)
	return vidlist

# ==============================================================
# Get the local host name
# ==============================================================
def get_local_name():
	return str(socket.gethostname())

# ==============================================================
# Get real videos cached in local host
# ==============================================================
def get_real_local_videos():
	cached_videos = []
	abspath = os.path.expanduser("~/videos/")
	dirs = filter(os.path.isdir, [os.path.join(abspath, f) for f in os.listdir(abspath)]) # ; print flist
	# print "Locally cached videos are: ", dirs
	for video in dirs:
		cached_videos.append(ntpath.basename(video))

	cached_videos.sort(key=str.lower)
	return cached_videos

# ================================================================================
# Update the list of locally cached videos to peers every hour
# ================================================================================
def periodic_discover():
	caching_list = {}
	cur_host = get_local_name()
	local_videos = Video.objects.filter(isLocal=True).values_list('id')
	local_video_id_str = ', '.join(str(vid[0]) for vid in local_videos)
	caching_list[cur_host] = local_video_id_str
	peers = Peer.objects.all()
	for peer in peers:
		update_videos(peer.ip, caching_list)

# ================================================================================
# Forward updated video info to other peers
# @input : rcv_host --- the peer that updates come from
#          video_updates --- updates made on local host
# ================================================================================
def forward_updates(rcv_host, video_updates):
	if len(video_updates) > 0:
		all_peers = Peer.objects.all()
		for peer in all_peers:
			if rcv_host != peer.name:
				#print("Forward video updates to cache agent:", peer.name, " with ip:", peer.ip)
				update_videos(peer.ip, video_updates)
				#print("Forward video updates successfully to", peer.name)

# ================================================================================
# Update the videos in caching_list to a peer
# ================================================================================
def update_videos(peer_ip, caching_list):
	local_host = get_local_name()
	url = 'http://%s:8615/video/add/'%peer_ip
	print(url)
	update_data = urllib.parse.urlencode(caching_list)
	data = update_data.encode('utf-8')

	print('Send a video/add request to ', peer_ip, '!')
	req = urllib.request.Request(url, data)
	req.add_header('agens-remote', local_host)
	rsp = urllib.request.urlopen(req)
	rspData = rsp.read()
	print(rspData)

# ================================================================================
# Change the dictionary of list for video updates to the string version
# @input : update_list --- the dictionary of video updates with keys as servers and
#			values as list of video ids.
# @return: update_str --- the dictionary of video updates in string version. Keys
#			are servers and values are strings of the list of video ids.
# ================================================================================
def update_list2str(update_list):
	update_str = {}
	for srv in update_list.keys():
		vid_list = update_list[srv]
		if len(vid_list) > 0:
			vid_list_str = ', '.join(str(vid) for vid in vid_list)
			update_str[srv] = vid_list_str
	return update_str

# ================================================================================
# Get the server for a video request based on method denoted by the user
# @input : vidID ---- the ID of the video user is requesting
#          method ---- the method that the agent selects the server
#                      available methods include 'qoe', 'load', 'rtt'
#                      'qoe' : always selects the server with best QoE
#		       'load' : always selects the server with the lightest load
#                      'rtt' : always selects the server with the smallest rtt
# ================================================================================
def get_server(vidID, method):
	curVid = Video.objects.get(pk=vidID)
	vidName = curVid.name
	srvs = curVid.srvs.split(',')
	srvs.pop()
	srvs_vals = {}
	selected_srv = {}
	
	# Read the load/rtt/qoe from the overlay table
	for srv in srvs:
		srv_id = int(re.findall(r'\d+', srv)[0])
		print("Check Server", srv, 'with srv_id', srv_id)
		srv_obj = Server.objects.get(pk=srv_id)
		if method == 'qoe':
			srvs_vals[srv_id] = 5.0 - float(srv_obj.qoe)
		elif method == 'load':
			srvs_vals[srv_id] = int(srv_obj.load)
		elif method == 'rtt':
			srvs_vals[srv_id] = float(srv_obj.rtt)
		elif method == 'hop':
			srvs_vals[srv_id] = int(srv_obj.hop)
		elif method == 'random':
			srvs_vals[srv_id] = random.random()
		else:
			print('Unrecognized method: ', method, ". Returning empty server!")
			return selected_srv
	# print(srvs_vals)

	# Select the server with the least value in srvs_vals
	selected_srv_id = min(srvs_vals, key=lambda k : srvs_vals[k])
	selected_srv_obj = Server.objects.get(pk=selected_srv_id)
	selected_srv['srv'] = selected_srv_obj.name
	selected_srv['ip'] = selected_srv_obj.ip
	selected_srv['vidName'] = vidName
	return selected_srv

#cached_videos = get_real_local_videos()
#print(cached_videos)

# ==============================================================
# Initialize the cache table for current node
# ==============================================================
def init_cache_table():
	existing_videos = Video.objects.all()
	if existing_videos.count() > 0:
		existing_videos.delete()
	cached_videos = get_local_videos()
	real_cached_videos = get_real_local_videos()
	hostname = get_local_name()
	for vid in cached_videos:
		vid_id = vid
		vid_name = real_cached_videos[vid_id%3]
		# vid_name = random.choice(real_cached_videos)
		vid_srvs = hostname + ', '
		cur_vid = Video(id=vid_id, name=vid_name, srvs=vid_srvs)
		cur_vid.save()
