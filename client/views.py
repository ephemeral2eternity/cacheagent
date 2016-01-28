from django.shortcuts import render
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
import json
import socket
from client.models import PClient, VClient

# Return all the clients that download videos from the current server.
def index(request):
	return HttpResponse("Please use http://cache_agent_ip:8615/client/pclient/ or http://cache_agent_ip:8615/client/vclient/ to get the proximate client ip addresses and video client ip addresses respectively!")

def query(request):
	pclients = PClient.objects.order_by('-last_visit')[:20]
	vclients = VClient.objects.order_by('-last_visit')[:20]
	cur_host = str(socket.gethostname())
	templates = loader.get_template('client/clients.html')
	context = RequestContext(request, {
					'localhost' : cur_host,
					'pclients' : pclients,
					'vclients' : vclients,
	})
	return HttpResponse(templates.render(context))

def add(request):
	client_ip = request.META['REMOTE_ADDR']
	url = request.get_full_path()
	if '?' in url:
		client_name = url.split('?')[1]
	else:
		client_name = request.META['REMOTE_HOST']
	num_results = PClient.objects.filter(ip=client_ip).count()
	if num_results > 0:
		cur_pclient = PClient.objects.filter(ip=client_ip)[0]
		cur_pclient.name = client_name
		cur_pclient.ip = client_ip
	else:
		cur_pclient = PClient(name=client_name, ip=client_ip)
	cur_pclient.save()
	return pclient(request)

def pclient(request):
	pclients = PClient.objects.order_by('-last_visit')[:20]
	pclient_ips = {}
	for pc in pclients:
		pclient_ips[pc.name] = pc.ip

	response = HttpResponse(str(pclient_ips))
	response['Params'] = json.dumps(pclient_ips)
	return response

# Create your views here.
def vclient(request):
	vclients = VClient.objects.order_by('-last_visit')[:20]
	vclient_ips = {}
	for vc in vclients:
		vclient_ips[vc.name] = vc.ip

	response = HttpResponse(str(vclient_ips))
	response['Params'] = json.dumps(vclient_ips)
	return response
