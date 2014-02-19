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
GRAPHITE_HOST="127.0.0.1"



def novaConnect():
	return novaclient.v1_1.Client(USER, PASS, TENANT_NAME, OS_AUTH_URL, timeout="600", service_type="compute", no_cache=True)

def novaVolConnect():
	return novaclient.v1_1.Client(USER, PASS, TENANT_NAME, OS_AUTH_URL, timeout="600", service_type="volume", no_cache=True, volume_service_name="cinder")

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
nova_vol = novaVolConnect()

# volumes timings/counts
try:

	volumes = nova_vol.volumes.list()
	if volumes:
		volumesetime = total_time(nova_vol.get_timings())
		nova_vol.reset_timings()
		collect_metric("timings.volumes.list", flavortime, now())
		collect_metric("counts.volumes.list", len(volumes), now())
except:
	print "volumes.list failed"

# flavor timings/counts
try:

	flavors = nova.flavors.list()
	if flavors:
		flavortime = total_time(nova.get_timings())
		nova.reset_timings()
		collect_metric("timings.flavors.list", flavortime, now())
		collect_metric("counts.flavors.list", len(flavors), now())
except:
	print "flavors.list failed"

# net timings/counts
try:
	networks = nova.networks.list()
	if networks:
		networkstime = total_time(nova.get_timings())
		nova.reset_timings()
		collect_metric("timings.networks.list", networkstime, now())
		collect_metric("counts.networks.list", len(networks), now())
except:
	print "networks.list failed"

# servers timings/counts
try:
	servers = nova.servers.list(True, {'all_tenants': '1', 'status': "ACTIVE"})

except:
	print "servers.list failed"

serverstime = total_time(nova.get_timings())
collect_metric("counts.servers.list", len(servers), now())
collect_metric("timings.servers.list", serverstime, now())
nova.reset_timings()


# exit cleanly
sys.stdout.flush()
sys.stderr.flush()
sys.exit(0)
