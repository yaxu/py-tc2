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

# Related work:
# Shanel Wu, Xavier A Corr, Xi Gao, Sasha De Koninck, Robin Bowers,
# and Laura Devendorf. 2024. Loom Pedals: Retooling Jacquard Weaving
# for Improvisational Design Workflows. In Proceedings of the
# Eighteenth International Conference on Tangible, Embedded, and
# Embodied Interaction (TEI '24). Association for Computing Machinery,
# New York, NY, USA, Article 10,
# 1–16. https://doi.org/10.1145/3623509.3633358

# Lea Albaugh, Scott E. Hudson, Lining Yao, and Laura
# Devendorf. 2020. Investigating Underdetermination Through
# Interactive Computational Handweaving. In Proceedings of the 2020
# ACM Designing Interactive Systems Conference (DIS '20). Association for Computing Machinery, New York, NY, USA, 1033–1046. https://doi.org/10.1145/3357236.3395538

import socket, re, random, sys
import paho.mqtt.client as mqtt

import argparse
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

## mqtt connect

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/pattern")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username=mqtt_username, password=mqtt_password)
mqttc.connect(mqtt_host, mqtt_port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
run = True
while run:
    rc = mqttc.loop(timeout=1.0)
    if rc != 0:
        print("mqtt error")
        run = False



