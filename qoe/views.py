import urllib.parse
import socket
import time
import ntpath
import json
import os
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from qoe.qoe_utils import *

# Create your views here.
# The page returned for the request: http://cache_agent_ip:port/overlay/
def index(request):
	return HttpResponse("Please come back later. The site is under construction.")

@csrf_exempt
def initQoE(request):
	initializeQoE()
	return query(request)

@csrf_exempt
def query(request):
	cur_host = str(socket.gethostname())
	qoe_dict = getQoEStr()
	print(qoe_dict)
	templates = loader.get_template('qoe/qoes.html')
	context = RequestContext(request, {
					'localhost' : cur_host,
					'qoes' : qoe_dict,
	})
	return HttpResponse(templates.render(context))

@csrf_exempt
def update(request):
	url = request.get_full_path()
	params = url.split('?')[1]
	update_dict = urllib.parse.parse_qs(params)
	print(update_dict)
	if 'srv' in update_dict.keys():
		srv = update_dict['srv'][0]
		if 'qoe' in update_dict.keys():
			qoe = float(update_dict['qoe'][0])
			if 'alpha' in update_dict.keys():
				alpha = float(update_dict['alpha'][0])
			else:
				alpha = 0.1
			updateQoE(srv, qoe, alpha)
		else:
			print('QoE update message needs to denote the qoe in request ', params)
			raise Http404
	else:
		print('QoE update message needs to denote the server name in request ', params)
		raise Http404
	return HttpResponse('Successfully update QoE value!')

@csrf_exempt
def dump(request):
	ts = dumpQoE()
	return HttpResponse("Dump QoE files successfully to gs://agens-data/ with timestamp " + ts + "!!!!")
