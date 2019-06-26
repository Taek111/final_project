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
        self.inputfuc = threading.Thread(target= self.input_check)
        self.inputfuc.start()
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

    def input_check(self):
        raw = input()
        if raw == "1": #상황1: 단계별알림시스템 1단계, 보여주고 사용자의 응답"괜찮아"까지 보여준다.
            e_one = threading.Thread(target=self.SafeCare.Emergency_one)
            e_one.start()
            self.SafeCare.isEmergency = True
        elif raw == "2": #상황2: 단계별알림시스템 2단계, 보여주고 문자, 휴대폰의 알림까지
            e_two = threading.Thread(target=self.SafeCare.Emergency_two)
            e_two.start()
        elif raw == "3": #상황3: 단계별알림시스템 3단계, 보여주고 ppt화면으로 119에 가는 문자
            self.SafeCare.audio.load("data/alarm_3.wav")
            self.SafeCare.audio.play()

        self.input_check()
if __name__ == '__main__':
    app = main()


