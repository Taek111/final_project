import paho.mqtt.client as mqtt
import time
import struct
import SafeCare
import threading
import config


class main():
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect("192.168.0.8", 1883, 60)
        self.client.subscribe("cds")
        self.client.subscribe("pir")
        self.client.subscribe("help")
        self.client.subscribe("isOpen")
        self.client.subscribe("temperature")
        self.client.on_message = self.on_message
        print("Client connected")
        self.SafeCare = SafeCare(self, config.room_list, config.username, config.appUser_num)
        self.client.loop_forever()

    def on_connect(self, client, userdata, rc):
        print("Connected")
        client.subscribe("connected")

    def on_message(self, client, userdata, msg):

        topic = str(msg.topic)
        if topic == "cds":
            id, con = struct.unpack('<BB', msg.payload[0:2])
        elif topic == "pir":
            id, con = struct.unpack('<BB', msg.payload[0:2])
        elif topic == "isOpen":
            id = "isOpen"
            con = struct.unpack('b', msg.payload[0:2])[0]
        elif topic == "help":
            id = "helpcall"
            con = struct.unpack('B', msg.payload)[0]
        elif topic == "temperature":
            id = "temp_mini"
            con = struct.unpack('B', msg.payload)[0]

        print(topic, id, con)
        self.SafeCare.data_in(id, topic, con)


