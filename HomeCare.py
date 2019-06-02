import time
import Queue as queue
from firebase import firebase
import threading
import matplotlib.pyplot as plt
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage
import pygame

room_list = ["room1", "room2", "room3"] #id 1,2

class HomeCare():

    def __init__(self,room_list, username):

        #firebase 
        self.db = firebase.FirebaseApplication("https://pracs-be3b0.firebaseio.com/", None)
        #room 
        self.rooms = {}
        for id in range(1,len(room_list)+1):
            self.rooms[id] = Room(self, id)

        #setting variable
        self.username = username
        self.EmergencyCall = False
        self.isEmergency = False
        self.temperature = queue.Queue(80)
        self.indoor = True
        self.isOpen = False 
        self.active_log = int(time.time())
        pygame.init()
        pygame.mixer.init()
        self.audio = pygame.mixer.music
        self.detectEmergentcy()




    def data_in(self, id, topic, value):
        if topic == "cds":
            if value:
                lightOn = True
            else:
                lightOn = False
            if not self.rooms[id].light == lightOn:
                self.updateDB(id, topic, lightOn)

                self.active_log = time.time()
            self.rooms[id].light = lightOn

        elif topic == "pir":
            self.rooms[id].pir = int(time.time())
            self.updateDB(id, topic, self.rooms[id].pir)
            self.active_log = self.rooms[id].pir

        elif topic == "temperature":
            qsize = self.temperature.qsize()
            if qsize == 80:
                self.temperature.get()
            self.temperature.put(value)
            if qsize > 2:
                self.drawTemperatureGraph()


        elif topic == "ir":
            if value:  # if ir value is HIGH
                self.isOpen = True
                self.check_indoor()
                check_10m = threading.Thread(target=self.check_indoor, arguments=(time.time()))
                check_10m.start()


    def detectEmergentcy(self):
        print("detect Emergency")
        if (int(time.time()) - self.active_log) > 3600: #1 hour
            self.isEmergency = True
            self.Emergency_one()
        threading.Timer(600, self.detectEmergentcy()).start()

    def updateDB(self,id, topic, value):
        #cds lightlog = int(time.time())

        if topic == "cds":
            self.db.patch('/user/'+self.username+'/'+ room_list[id-1], {'Light': value})
            self.db.patch('/user/'+self.username+, {'Lightlog': int(time.time())})

        if topic == "pir":
            self.db.patch('/user/'+self.username+'/'+ room_list[id-1], {'PIR': value})
            self.db.patch('/user/'+self.username, {'Lightlog_room': "room"+str(id)})
    def check_indoor(self, time_start):
        while(time.time() - time_start < 600):
            if self.active_log > time_start:
                self.indoor = True
                return
            time.sleep(30)
        self.indoor = False

    def drawTemperatureGraph(self):
        cur_time = int(time.time())
        qsize = self.temperature.qsize()
        start, middle, end = time.localtime(cur_time - (qsize-1) * 600),\
                             time.localtime(cur_time - (qsize-1) * 300),\
                             time.localtime(cur_time)
        tlist = np.linspace(cur_time-(qsize-1)*600, cur_time, qsize)
        plt.plot(tlist, list(self.temperature.queue))
        plt.xticks([cur_time-(qsize-1)*600, cur_time-(qsize-1)*300, cur_time],
                   [str(start.tm_hour) + ':' + str(start.tm_min),
                    str(middle.tm_hour) + ':' + str(middle.tm_min),
                    str(end.tm_hour) + ':' + str(end.tm_min)])
        plt.xlabel("Time")
        plt.ylabel('Temperature ($^\circ$C)')
        plt.title(str(end.tm_year) + ". " + str(end.tm_mon) + ". " + str(end.tm_mday))
        plt.ylim(10,50)
        plt.savefig("data/yellowdog.png", dpi=350)
        cred = credentials.Certificate("pracs-be3b0-firebase-adminsdk-yqgu4-f92fb008fe.json")
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'pracs-be3b0.appspot.com'})
        bucket = storage.bucket()
        zebraBlob = bucket.blob("yellowdog.png")
        zebraBlob.upload_from_filename(filename="data/yellowdog.png")


    #ir sensor -> immediate state -> find indoor 
    def Emergency_one(self):
        self.audio.load("data/alarm_1.wav")
        self.audio.play()
        while self.audio.get_busy():
            time.sleep(5)
        time.sleep(30)
        if self.isEmergency == True:
            self.Emergency_two()

    def Emergency_two(self):
        self.audio.load("data/alarm_2.wav")
        self.audio.play()
        while self.audio.get_busy():
            time.sleep(5)
        time.sleep(30)
        if self.isEmergency == True:
            self.EmergencyCall()
            self.audio.load("data/alarm_3.wav")
            self.audio.play()

    #stage 1 speaker on, 
    def EmergencyCall(self):
        print("Emergency Call")


    def print_all(self):
        for id in range(1, len(self.rooms)+1):
            self.rooms[id].print_state()

class Room():
    def __init__(self, parent, id):
        self.parent = parent
        self.id = id
        self.light = None
        self.pir = 0
    def print_state(self):
        print("room%d light:%s pir:%s"%(self.id, self.light, self.pir))


if __name__ == '__main__':

    app = HomeCare(room_list)
    n = time.time()
    app.data_in(2,"cds",0)
    app.data_in(2, "cds", 400)
    app.data_in(2, "cds", 0)
    app.data_in(1, "pir", 1)
    app.data_in(3, "cds", 500)
    app.print_all()
    a = time.time()
    print(a-n)
