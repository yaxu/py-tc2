#!/usr/bin/python3
import paho.mqtt.client as mqtt
import json, math
from collections import deque

counter = 0

blocks = [[
'x         ',
' x       x',
'x x     x ',
'xx x   x x',
'xxx x x xx',
'xxxx x xxx',
'xxx x x xx',
'xx x   x x',
'x x     x ',
' x       x',
],
[
' xxxxxxxxx',
'x xxxxxxx ',
' x xxxxx x',
'  x xxx x ',
'   x x x  ',
'    x x   ',
'   x x x  ',
'  x xxx x ',
' x xxxxx x',
'x xxxxxxx ',
]
]

blocksz = len(blocks[0][1])

def bjorklund(steps, pulses):
    steps = int(steps)
    pulses = int(pulses)
    if pulses > steps:
        raise ValueError    
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

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("/tc2/footswitch")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global counter
    print("counter", counter)
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == '/tc2/footswitch':
        delta = json.loads(msg.payload)
        pulses = min(int(math.log(delta) * 10),32)
        steps = 128
        print("delta", delta, "pulses", pulses)
        bjork = bjorklund(steps,pulses)
        # print(bjork)
        # seq = deque(bjork)
        # seq.rotate(counter)
        # bjork = list(seq)
        pattern = "".join(map(lambda x: blocks[0][counter % blocksz] if x else blocks[1][counter % blocksz], bjork))
        pattern = "".join(map(lambda x: "1" if x == 'x' else "0", pattern))
        pattern = pattern * 2
        pattern = pattern[:1320]
        # print("sending", pattern)
        client.publish("/pattern", pattern)
        counter = counter + 1


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="tue",password="runningwithscissors")
#mqttc.tls_set()
mqttc.connect("slab.org", 1883, 60)
mqttc.publish("/pattern", "0")

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
