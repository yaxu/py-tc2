import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("/pattern/json")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client(client_id="pythontest", transport="websockets")
client.username_pw_set(username="tue",password="runningwithscissors")

client.on_connect = on_connect
client.on_message = on_message

client.tls_set()
client.connect("slab.org", 8083, 55)
client.publish("/bingo", "hello")
client.loop_forever()
