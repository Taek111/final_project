import paho.mqtt.client as mqtt
import time
import struct
import SafeCare
import threading
import config

cname = "Client_"
topics = ["cds", "pir", "help", "isOpen", "temperature"]

class main():
    def __init__(self):
        self.SafeCare = SafeCare.SafeCare(self, config.room_list, config.username, config.appUser_num)
        self.clients = list()
        for topic in topics:
            self.client = mqtt.Client(cname+topic)
            self.client.connect("192.168.0.8", 1883, 60)
            self.client.subscribe(topic)
            self.client.on_message = self.on_message
            self.clients.append(self.client)
            self.client.loop_start()

        print("Clients connected")

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

if __name__ == '__main__':
    app = main()

