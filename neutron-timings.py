#!/usr/bin/env python
import re
import os
import time
import sys
import socket
from neutronclient.v2_0 import client as neutronclient


STATS_PREFIX = "openstack.neutron"

if not re.match(".$", STATS_PREFIX):
	STATS_PREFIX += "."

USER=os.environ['OS_USERNAME']
PASS=os.environ['OS_PASSWORD']
TENANT_NAME=os.environ['OS_TENANT_NAME']
OS_AUTH_URL=os.environ['OS_AUTH_URL']
GRAPHITE_HOST="10.64.140.42"



def neutronConnect():
  return neutronclient.Client(username=USER, password=PASS, tenant_name=TENANT_NAME, auth_url=OS_AUTH_URL)

def collect_metric(name, value, timestamp):
  sock = socket.socket()
  sock.settimeout(5)
  sock.connect( (GRAPHITE_HOST, 2003) )
  print "%s %s %d" % (STATS_PREFIX + name, value, timestamp)
  sock.send("%s %s %d\n" % (STATS_PREFIX + name, value, timestamp))
  sock.close()

def now():
  return time.time()


#main
neutron = neutronConnect()

# network timings/counts
try:

  start = now()
  networks = neutron.list_networks()
  end = now()
  if networks:
    networkstime = round(end - start, 4)
    collect_metric("timings.networks.list", networkstime, now())
except:
  print "networks.list failed"

# exit cleanly
sys.stdout.flush()
sys.stderr.flush()
sys.exit(0)
