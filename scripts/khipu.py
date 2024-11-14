#!/usr/bin/python3

import serial
import paho.mqtt.client as mqtt
import json, math
from collections import deque

strands = {
  23: "function",
  26: 4,
  8:  2,
  6: 2,
  25: 3,
  3: 5,
  21: 5,
  22: 7,
  1: "function",
  17: "function",
  2: "function",
  19: "function",
  24: "function",
  29: 4,
  28: 8,
  33: 9,
  35: 7
}

s = serial.Serial("/dev/ttyACM0", 115200)

numbers = None
counter = 0

def parseBranch(tree, depth):
    if tree["id"] in strands:
        name = strands[tree["id"]]
    else:
        name = "<%d>" % tree["id"]
    top = { "name": name, "children": [] }
    children = []
    if tree["desc"] and len(tree["desc"]):
        maxslot = max(map(lambda x: x["order"], tree["desc"]))
        for i in range(0, maxslot+1):
            childtree = list(filter(lambda x: x["order"] == i, tree["desc"]))
            # print("childtree %d" % i, childtree)
            
            if len(childtree):
               child = parseBranch(childtree[0], depth + 1)
            else:
                child = { "name": "", "children": [] }
            children.append(child);
    if len(children) > 0:
        top["children"] =  children    
    return top

def parseTree(tree):
    khipu = { "name": "khipu", "children": [] }
    children = []
    for i in range(0, 4):
        if i in tree and tree[i]:
            child = parseBranch(tree[i][0], 0)
        else:
          child = { "name": "", "children": [] }
        children.append(child)
    if len(children) > 0:
        khipu["children"] = children
    return khipu


def bjorklund(steps, pulses):
    steps = int(steps)
    pulses = int(pulses)
    if pulses > steps:
        pulses = steps    
    pattern = []    
    counts = []
    remainders = []
    divisor = steps - pulses
    remainders.append(pulses)
    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level = level + 1
        if remainders[level] <= 1:
            break
    counts.append(divisor)
    
    def build(level):
        if level == -1:
            pattern.append(0)
        elif level == -2:
            pattern.append(1)         
        else:
            for i in range(0, counts[level]):
                build(level - 1)
            if remainders[level] != 0:
                build(level - 2)
    
    build(level)
    i = pattern.index(1)
    pattern = pattern[i:] + pattern[0:i]
    return pattern

def patternBjork(numbers, i):
    pulses = numbers[0][i % len(numbers[0])]
    steps = numbers[1][i % len(numbers[1])]
    rotation = numbers[2][i % len(numbers[2])]
    pat = bjorklund(steps, pulses)
    if pat:
        pat = deque(pat)
        pat.rotate(rotation)
        pat = list(pat)
    print(pat, "pulses %d steps %d rotation %d" % (pulses, steps, rotation))
    return(pat)

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("/tc2/footswitch")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global counter
    print("counter", counter)
    # print(msg.topic+" "+str(msg.payload))
    if msg.topic == '/tc2/footswitch':
        print("footswitch!")
        delta = json.loads(msg.payload)
        pattern = patternBjork(numbers, counter)
        pattern = pattern * (int(1320 / len(pattern))+1)
        pattern = pattern[:1320]
        pattern = "".join(map(lambda x: "1" if x else "0", pattern))
        print("sending", len(pattern))
        client.publish("/pattern", pattern)
        counter = counter + 1

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="tue",password="runningwithscissors")
#mqttc.tls_set()
mqttc.connect("slab.org", 1883, 60)
mqttc.publish("/pattern", "0")


counter = 0

while True:
    st = s.readline()
    k = eval(st)
    parsed = parseTree(k)
    for pendant in parsed["children"]:
        if pendant['name'] == 'function':
            numbers = []
            for strand in pendant['children']:
                if strand['name'] == 'function':
                    subnumbers = []
                    for substrand in strand['children']:
                        subnumbers.append(substrand['name'])
                    numbers.append(subnumbers)
                else:
                    numbers.append([strand['name']])
            print(numbers)
            break
    rc = mqttc.loop(timeout=0.01)
    if rc != 0:
        print("mqtt error")
        run = False
