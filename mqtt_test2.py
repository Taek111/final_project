import paho.mqtt.client as mqtt
import time
import struct

def on_connect(client, userdata, rc):
    print("connected")
    client.subscribe("cds")

def on_message(client, userdata, msg):
    print(str(msg.topic.decode("utf-8")))
    print("Topic:" + str(msg.topic.decode("utf-8")) + \
            '\nMessage: '+ str(struct.unpack('h', msg.payload)[0]))

def main():
    print("Hi")
    client = mqtt.Client()
    print("connect")
    client.connect("192.168.43.146", 1883, 60)
    client.subscribe("cds")
    client.subscribe("pir")
    client.on_connect = on_connect
    client.on_message = on_message
    print("client connected")
    client.loop_forever()

if __name__ == "__main__":
    main()
