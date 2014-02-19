#!/usr/bin/env python
import os
import time
import sys
import socket
from keystoneclient.v2_0 import client

STATS_PREFIX = "openstack.keystone.timings"

USER=os.environ['OS_USERNAME']
PASS=os.environ['OS_PASSWORD']
TENANT_NAME=os.environ['OS_TENANT_NAME']
KEYSTONE_URL=os.environ['OS_AUTH_URL']
GRAPHITE_HOST="127.0.0.1"


def keystoneConnect():
	return client.Client(username=USER,
			     password=PASS,
			     tenant_name=TENANT_NAME,
			     auth_url=KEYSTONE_URL,
			     timeout=10)
def collect_metric(name, value, timestamp):
	try:
   	    sock = socket.socket()
	    sock.settimeout(5)
	    sock.connect( (GRAPHITE_HOST, 2003) )
	    print "%s %s %d\n" % (name, value, timestamp)
	    sock.send("%s %s %d\n" % (name, value, timestamp))
	    sock.close()
	except:
		print "Put to graphite failed"

def now():
	return int(time.time())


t0 = time.time()
try:
	keystone = keystoneConnect()
except:
	print "Keystone connection failed"
	sys.exit()

t1 = time.time()
total = round(t1-t0,2)

KMETRIC = STATS_PREFIX + ".token_get." + USER
collect_metric(KMETRIC, total, now())
