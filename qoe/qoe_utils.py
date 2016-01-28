## Implement QoE related methods used in qoe.views etc.
# Chen Wang, Feb. 16, 2015
# chenw@cmu.edu
import json
import re
import subprocess
import os
import time
import socket
import ntpath
from qoe.models import QoE
from overlay.models import Server

# ================================================================================
# Initialize the QoE vector for all servers on current agent
# ================================================================================
def initializeQoE():
	existingQoE = QoE.objects.all()
	if existingQoE.count() > 0:
		existingQoE.delete()
	srvs = Server.objects.all()
	for s in srvs:
		print("Initialize QoE for server", s.name)
		if s.isLocal:
			q = 5.0
		else:
			q = 4.0
		cur_qoe = QoE(qoe=q, srv=s.name)
		cur_qoe.save()
		s.qoe = q
		s.save()
		# update_overlay_qoe(s.name, q)

# ================================================================================
# Return the dict of QoE traces with key defined as server name
# ================================================================================
def getQoEStr():
	qoe_dict = {}
	srvs = Server.objects.all()
	for s in srvs:
		qoe_dict[s.name] = []
		srv_qoes = QoE.objects.filter(srv=s.name)
		for q in srv_qoes:
			ts_str = q.time.strftime('%Y-%m-%d %H:%M:%S')
			qoe_out_str = ts_str + " ------- " + str(q.qoe)
			qoe_dict[s.name].append(qoe_out_str)
	return qoe_dict

# ================================================================================
# Update QoE for a server with given new QoE value and an alpha value
# @input : srv ---- the server to update qoe
#	   qoe ---- new qoe value received for the srv
#          alpha ---- the weight to be given to the new QoE value
# ================================================================================
def updateQoE(srv, qoe, alpha):
	## Revision by chenw-2015-0317, read QoE updated to overlay not the previous sample.
	# last_qoe = QoE.objects.filter(srv=srv).order_by('-time')[0]
	# print('Last qoe value for server ', srv, ' is ', last_qoe.qoe)
	# previous_qoe = float(last_qoe.qoe)
	
	## Read QoE updated to the overlay last time
	srv_id = int(re.findall(r'\d+', srv)[0])
	srv_obj = Server.objects.get(pk=srv_id)
	previous_qoe = float(srv_obj.qoe)
	new_qoe = (1 - alpha) * previous_qoe + alpha * qoe
	print('New qoe is ', new_qoe)
	new_qoe_obj = QoE(qoe=new_qoe, srv=srv)
	new_qoe_obj.save()
	update_overlay_qoe(srv, new_qoe)

# ================================================================================
# Dump all the QoE data
# ================================================================================
def dumpQoE():
        ## Dump the qoe objects
        all_qoe = QoE.objects.all()
        qoes = {}
        qoes_id = {}

        for qoe_obj in all_qoe:
                if qoe_obj.srv not in qoes.keys():
                        qoes[qoe_obj.srv] = {}
                cur_ts = int(time.mktime(qoe_obj.time.timetuple()))
                qoes[qoe_obj.srv][cur_ts] = float(qoe_obj.qoe)
                qoes_id[qoe_obj.srv] = int(qoe_obj.id)

        cur_file_path = os.path.realpath(__file__)
        cur_path, cur_file_name = ntpath.split(cur_file_path)
        cur_host_name = str(socket.gethostname())
        ts = time.strftime('%m%d%H%M')

        try:
                os.stat(cur_path + '/tmp/')
        except:
                os.mkdir(cur_path + '/tmp/')

        qoes_file = cur_path + '/tmp/' + cur_host_name + '_' + ts + '_QoE.json'

        with open(qoes_file, 'w') as outfile:
                json.dump(qoes, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        gcs_upload('agens-data', qoes_file)

        for qoe_obj in all_qoe:
                if int(qoe_obj.id) < qoes_id[qoe_obj.srv] - 10:
                        qoe_obj.delete()

        return ts

# ================================================================================
# Update QoE value for a server in the overlay table
# @input : srv ---- the server to update qoe
#	   qoe ---- new qoe value to be updated in overlay table
# ================================================================================
def update_overlay_qoe(srv, qoe):
	srv_id = int(re.findall(r'\d+', srv)[0])
	srv_obj = Server.objects.get(pk=srv_id)
	srv_obj.qoe = qoe
	srv_obj.save()
	print('Successfully update qoe for server, ', srv, ' in the overlay table!')

# ================================================================================
# Define a function to update a file to a google cloud storage bucket
# ================================================================================
def gcs_upload(bucketName, uploadFile):
	# Execute gsutil command to upload the file "uploadFile"
	# authFile = "./info/auth.json"
	# gcs_authenticate(authFile)
	subprocess.call(["gsutil", "cp", uploadFile, "gs://" + bucketName])

