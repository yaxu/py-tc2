#!/usr/bin/python3

# (c) 2024 Alex McLean and Pei-Ying Lin

# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# <http://www.gnu.org/licenses/>.

import socket, re, random, sys
import paho.mqtt.client as mqtt

import argparse, json
import tc2

tc2 = tc2.TC2()

parser=argparse.ArgumentParser()
parser.add_argument("--host")
parser.add_argument("--port")
parser.add_argument("--username")
parser.add_argument("--password")
args=parser.parse_args()

mqtt_host = args.host or "slab.org"
mqtt_username = args.username or "tue"
mqtt_password = args.password
mqtt_port = 1883

subscribe_topics = ["/pattern", "/tc2/connect"]

## mqtt connect

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    for topic in subscribe_topic:
        client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    match topic:
        case "/pattern":
            tc2.queue(json.loads(userdata))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username=mqtt_username, password=mqtt_password)
mqttc.connect(mqtt_host, mqtt_port, 60)

print("Connecting to TC/2")
tc2.connect()

print("Waiting for data..")
run = True
while run:
    rc = mqttc.loop(timeout=0)
    if rc != 0:
        print("mqtt error")
        run = False
    # blocks for up to 1/20th of a second
    tc2.poll(0.05)
    print("tick")


