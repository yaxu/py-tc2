#!/usr/bin/python3

import paho.mqtt.publish as publish
import json

publish.single("/pattern/json", json.dumps([True, False, False, True, False]), hostname="slab.org", auth={"username":"tue","password":"runningwithscissors"})
#publish.single("/tc2/stop", "", hostname="slab.org", auth={"username":"tue","password":"runningwithscissors"})
