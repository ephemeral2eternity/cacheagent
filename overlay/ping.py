'''
PING a server with count times and get the RTT list
'''
from subprocess import Popen, PIPE
import string
import re
import socket
import time

def extract_number(s,notfound='NOT_FOUND'):
    regex=r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'
    return re.findall(regex,s)

def getRTT(ip, count):
	'''
	Pings a host and return True if it is available, False if not.
	'''
	cmd = ['ping', '-c', str(count), ip]
	process = Popen(cmd, stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	rttList = parsePingRst(stdout, count)
	print(rttList)
	return rttList

def getMnRTT(ip, count):
	rttList = getRTT(ip, count)
	if len(rttList) > 0:
		mnRTT = sum(rttList) / float(len(rttList))
	else:
		mnRTT = 500.0
	return mnRTT

def parsePingRst(pingString, count):
	rtts = []
	lines = pingString.splitlines()
	for line in lines:
		curline = str(line)
		# print(curline)
		if "time=" in curline:
			curDataStr = curline.split(':', 2)[1]
			curData = extract_number(curDataStr)
			rtts.append(float(curData[-1]))
	return rtts
