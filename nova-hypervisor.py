#!/usr/bin/env python
import re
import os
import time
import sys
import socket
import novaclient.v1_1

STATS_PREFIX = "openstack.hypervisor"

if not re.match(".$", STATS_PREFIX):
	STATS_PREFIX += "."

USER=os.environ['OS_USERNAME']
PASS=os.environ['OS_PASSWORD']
TENANT_NAME=os.environ['OS_TENANT_NAME']
OS_AUTH_URL=os.environ['OS_AUTH_URL']
GRAPHITE_HOST="127.0.0.1"



def novaConnect():
	return novaclient.v1_1.Client(USER, PASS, TENANT_NAME, OS_AUTH_URL, timeout="600", service_type="compute", no_cache=True)

def collect_metric(name, value, timestamp):
	sock = socket.socket()
	sock.settimeout(5)
	sock.connect( (GRAPHITE_HOST, 2003) )
	#print "%s %s %d" % (STATS_PREFIX + name, value, timestamp)
	sock.send("%s %s %d\n" % (STATS_PREFIX + name, value, timestamp))
	sock.close()

def now():
	return int(time.time())

nova = novaConnect()
try:

	hypervisors = nova.hypervisors.list()
	if hypervisors:
		for h in hypervisors:
			hv = nova.hypervisors.get(h.id)
			stats = hv._info.copy()
			for k, v in sorted(stats.items()):
				if k in ('cpu_info','service','hypervisor_hostname','id'):
					continue
				hostname = h.hypervisor_hostname.split('.')
				collect_metric("%s.%s" % (hostname[0],k), v, now())

except:
	print "hypervisor.list failed"


# exit cleanly
sys.stdout.flush()
sys.stderr.flush()
sys.exit(0)
