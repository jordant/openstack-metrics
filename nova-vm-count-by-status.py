#!/usr/bin/env python
import re
import os
import time
import sys
import socket
import novaclient.v1_1


STATS_PREFIX = "openstack.nova"

if not re.match(".$", STATS_PREFIX):
	STATS_PREFIX += "."

USER=os.environ['OS_USERNAME']
PASS=os.environ['OS_PASSWORD']
TENANT_NAME=os.environ['OS_TENANT_NAME']
OS_AUTH_URL=os.environ['OS_AUTH_URL']
GRAPHITE_HOST="10.64.140.42"



def novaConnect():
	return novaclient.v1_1.Client(USER, PASS, TENANT_NAME, OS_AUTH_URL, timeout="600", service_type="compute", no_cache=True)

def collect_metric(name, value, timestamp):
	sock = socket.socket()
	sock.settimeout(5)
	sock.connect( (GRAPHITE_HOST, 2003) )
	print "%s %s %d" % (STATS_PREFIX + name, value, timestamp)
	sock.send("%s %s %d\n" % (STATS_PREFIX + name, value, timestamp))
	sock.close()

def now():
	return int(time.time())

def total_time(timings):
	total = 0
	for url, start, end in timings:
		total += round(end - start,2)
	return total


#main
nova = novaConnect()
status_count = {}

# servers timings/counts
try:
	servers = nova.servers.list(True, {'all_tenants': '1'})
	for server in servers:
		status = server.status
		if status not in status_count:
			status_count[status] = 1
		else:
			status_count[status] += 1

except Exception as e:
	print "servers.list failed %s" % e

for status in status_count:
	print "%s %d", (status, status_count[status])
	collect_metric("counts.servers.status." + status, status_count[status], now())


# exit cleanly
sys.stdout.flush()
sys.stderr.flush()
sys.exit(0)
