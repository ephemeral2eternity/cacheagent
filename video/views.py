import random
import urllib.parse
import json
from collections import defaultdict
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from video.models import Video
from video.video_utils import *

# Create your views here.

# The page returned for the request: http://cache_agent_ip:port/videos/
def index(request):
	return query(request)

@csrf_exempt
def initVideo(request):
	# Delete all objects in the table first
	init_cache_table()
	return query(request)

@csrf_exempt
def query(request):
	# Return the initialized servers
	vid_list = Video.objects.all()
	cur_host = get_local_name()
	templates = loader.get_template('video/videos.html')
	context = RequestContext(request, {
					'videos' : vid_list,
					'host' : cur_host,
	})
	return HttpResponse(templates.render(context))

@csrf_exempt
def discover(request):
	periodic_discover()
	return HttpResponse("Broadcast local cached videos to all other nodes!")

@csrf_exempt
def add(request):
	cur_host = get_local_name()
	remote_host = request.META['HTTP_AGENS_REMOTE']
	print("The video/add request sent by", remote_host)
	if request.method == "POST":
		print(request.POST)
		new_updates = defaultdict(list)
		srvs = request.POST.keys()
		for srv in srvs:
			vid_list_str = request.POST.get(srv, "")
			vid_list = [int(s) for s in vid_list_str.split(',')]
			# print(vid_list)
			for vid in vid_list:
				vid_id = vid
				# print('Processing video ', vid_id, "!")
				vid_exist = Video.objects.filter(id=vid_id)
				if vid_exist.count() > 0:
					vid_obj = Video.objects.get(id=vid_id)
					# print("Video object with id = ", vid_id, " found in local cache table!")
					vid_srv_list = vid_obj.srvs.split(', ')
					# print("Video server list in cache table:", vid_srv_list)
					if srv not in vid_srv_list:
						vid_obj.srvs = vid_obj.srvs + srv + ', '
						new_updates[srv].append(vid)
						# print("New srvs for video ", vid, " is ", vid_obj.srvs)
						vid_obj.save()
					# print("Server ", srv, " has been added to Video ", vid, " in cache table!")
				else:
					vid_name = 'BBB'
					isLocal = False
					vid_srvs = srv + ', '
					# print("srvs for video ", vid, " is ", vid_srvs)
					new_vid_obj = Video(id=vid_id, name=vid_name, isLocal=isLocal, srvs=vid_srvs)
					new_vid_obj.save()
					new_updates[srv].append(vid)
					# print("Video ", vid, " on server ", srv," has been added to cache table!")
		# print('Start forwarding the updates on this agent from', remote_host)
		new_update_str = update_list2str(new_updates)
		# print('The updates are', new_update_str)
		forward_updates(remote_host, new_update_str)
		return HttpResponse("Successfully update video list cached on " + srv + "!")
	elif request.method == "GET":
		return HttpResponse("You should use POST method when calling http://cache_agent:port/video/add/ to add video lists!")

# ================================================================================
# Return the server name and ip address to the user
# ================================================================================
@csrf_exempt
def getSrv(request):
	url = request.get_full_path()
	params = url.split('?')[1]
	request_dict = urllib.parse.parse_qs(params)
	print(request_dict)
	if 'vidID' in request_dict.keys():
		vidID = int(request_dict['vidID'][0])
		if 'method' in request_dict.keys():
			method = request_dict['method'][0]
		else:
			method = 'qoe'
		# Call the get_server method 
		srv_dict = get_server(vidID, method)
	else:
		raise Http404
	response = HttpResponse(str(srv_dict))
	response['Params'] = json.dumps(srv_dict)
	return response	
