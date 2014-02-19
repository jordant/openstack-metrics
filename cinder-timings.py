#!/usr/bin/env python
import re
import os
import time
import sys
import socket
from cinderclient.v1 import client


STATS_PREFIX = "openstack.cinder"

if not re.match(".$", STATS_PREFIX):
	STATS_PREFIX += "."

USER=os.environ['OS_USERNAME']
PASS=os.environ['OS_PASSWORD']
TENANT_NAME=os.environ['OS_TENANT_NAME']
OS_AUTH_URL=os.environ['OS_AUTH_URL']
GRAPHITE_HOST="127.0.0.1"



def cinderConnect():
  return client.Client(USER, PASS, TENANT_NAME, OS_AUTH_URL, service_type="volume")

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
cinder = cinderConnect()

# volumes timings/counts
try:

  start = now()
  volumes = cinder.volumes.list()
  end = now()
  if volumes:
    volumestime = round(end - start, 4)
    collect_metric("timings.volumes.list", volumestime, now())
    collect_metric("counts.volumes.list", len(volumes), now())
except:
  print "volumes.list failed"

# exit cleanly
sys.stdout.flush()
sys.stderr.flush()
sys.exit(0)
