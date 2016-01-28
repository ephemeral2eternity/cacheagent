import os
import ntpath
import socket
import time
import json
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from monitor.models import Load, BW, RTTS, SYS_STAT
from monitor.cache_monitor import *

# Create your views here.
def index(request):
	return HttpResponse("Please come back later!")

# Create videos for recent load request
@csrf_exempt
def view_load(request):
	local_host = get_host_name()
	load_list = Load.objects.order_by('-pk')[:30]
	template = loader.get_template('monitor/load.html')
	context = RequestContext(request, {
					'cur_host':local_host,
					'load_list':load_list,
	})
	return HttpResponse(template.render(context))

@csrf_exempt
def view_bw(request):
	local_host = get_host_name()
	bw_list = BW.objects.order_by('-pk')[:30]
	template = loader.get_template('monitor/bw.html')
	context = RequestContext(request, {
					'cur_host':local_host,
					'bw_list':bw_list,
	})
	return HttpResponse(template.render(context))

# Show the recent system status monitored
@csrf_exempt
def view_sys_stat(request):
	local_host = get_host_name()
	sys_stat_list = SYS_STAT.objects.order_by('-pk')[:30]
	template = loader.get_template('monitor/sys_stats.html')
	context = RequestContext(request, {
					'cur_host':local_host,
					'sys_stat_list':sys_stat_list,
	})
	return HttpResponse(template.render(context))

@csrf_exempt
def view_rtts(request):
	local_host = get_host_name()
	rtts_list = RTTS.objects.order_by('-pk')[:30]
	template = loader.get_template('monitor/rtts.html')
	context = RequestContext(request, {
					'cur_host':local_host,
					'rtts' : rtts_list,
	})
	return HttpResponse(template.render(context))

@csrf_exempt
def dump(request):
	ts = dump_monitor()
	return HttpResponse("Dump Load and BW files successfully to gs://agens-data/ with timestamp " + str(ts) + "!!!")
