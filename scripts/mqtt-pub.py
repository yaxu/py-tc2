#!/usr/bin/python3

import paho.mqtt.publish as publish
import json

# publish.single("/pattern", "1001101010", hostname="slab.org", auth={"username":"tue","password":"runningwithscissors"})
publish.single("/tc2/footswitch", "6", hostname="slab.org", auth={"username":"tue","password":"runningwithscissors"})

