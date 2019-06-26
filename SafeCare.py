import time
import queue
from firebase import firebase
import threading
import matplotlib
matplotlib.use("Pdf")
import matplotlib.pyplot as plt
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage
import pygame
import send


room_list = ["room1", "room2", "room3"]
class SafeCare():

    def __init__(self, parent, room_list, username,appUser):

        #firebase 
        self.db = firebase.FirebaseApplication("https://pracs-be3b0.firebaseio.com/", None)
        #room 
        self.rooms = {}
        for id in range(1,len(room_list)+1):
            self.rooms[id] = Room(self, id)

        #setting variable
        self.parent = parent
        self.username = username
        self.appUser = appUser
        self.isEmergency = False
        self.temperature = queue.Queue(80)
        self.indoor = True
        self.active_log = int(time.time())
        pygame.init()
        pygame.mixer.init()
        self.audio = pygame.mixer.music
        self.detectEmergency()
        self.callEmergency = False
        self.onBed = False




    def data_in(self, id, topic, value):
        if topic == "cds":
            if value:
                light_status = True
            else:
                light_status = False
            if not self.rooms[id].light == light_status:
                self.updateDB(id, topic, light_status)

                self.active_log = time.time()
            self.rooms[id].light = light_status

        elif topic == "pir":
            self.rooms[id].pir = int(time.time())
            self.updateDB(id, topic, self.rooms[id].pir)
            self.active_log = self.rooms[id].pir

        elif topic == "temperature":
            if value > 30:
                self.onBed = True
            qsize = self.temperature.qsize()
            if qsize == 80:
                self.temperature.get()
            self.temperature.put(value)
            if qsize > 2:
                self.drawTemperatureGraph()

        elif topic == "help":
            if not value:  # voice "help"
                while not self.isEmergency:
                    self.isEmergency = True
                    Eapp = threading.Thread(target=self.EmergencyCall())
                    Eapp.start()
            else:  # voice "ok"
                if self.audio.get_busy():
                    self.audio.stop()
                if self.isEmergency:
                    Ecancel = threading.Thread(target=self.Emergency_cancel)
                    Ecancel.start()


        elif topic == "isOpen":
            print(topic, id, value)
            if value:  # if ir value is HIGH
                
                cur_time = int(time.time())
                print(cur_time)
                check_10m = threading.Thread(target=self.check_indoor, args=(cur_time,))
                check_10m.start()
                


    def detectEmergency(self):
        print("detect Emergency")
        if self.indoor:
            if (int(time.time()) - self.active_log) > 3600 * 6 and not self.onBed: #6 hour
                self.isEmergency = True
                self.Emergency_one()
        threading.Timer(3600 * 6, self.detectEmergency).start()

    def updateDB(self,id, topic, value):
        #cds lightlog = int(time.time())

        if topic == "cds":
            self.db.patch('/user/'+self.username+'/'+ room_list[id-1], {'Light': value})
            self.db.patch('/user/'+self.username, {'Lightlog': int(time.time())})
            self.db.patch('/user/' + self.username, {'Lightlog_room': id})

        if topic == "pir":
            self.db.patch('/user/'+self.username+'/'+ room_list[id-1], {'PIR': value})
            self.db.patch('/user/'+self.username, {'PIRlog_room': id})

        if topic == "isEmergency":
            self.db.patch('/user/' + self.username, {'Emergency': value})
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
        plt.ylim(20,40)
        plt.savefig("data/"+self.username+".png", dpi=350)
        cred = credentials.Certificate("pracs-be3b0-firebase-adminsdk-yqgu4-f92fb008fe.json")
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'pracs-be3b0.appspot.com'})
        bucket = storage.bucket()
        tempBlob = bucket.blob(self.username+".png")
        tempBlob.upload_from_filename(filename="data/"+self.username+".png")


    #ir sensor -> immediate state -> find indoor 
    def Emergency_one(self):
        print("Emergency_one")
        self.audio.load("data/alarm_1.wav")
        self.audio.play()
        while self.audio.get_busy():
            time.sleep(5)
        time.sleep(10 * 60)
        if self.isEmergency == True:
            self.Emergency_two()

    def Emergency_two(self):
        self.updateDB("help", "isEmergency", True)

        self.audio.load("data/alarm_2.wav")
        self.audio.play()
        while self.audio.get_busy():
            time.sleep(5)
        send.send_to_appUser(self.appUser, 1)
        time.sleep(30 * 60)
        if self.isEmergency == True:
            send.send_to_119(1)
            self.audio.load("data/alarm_3.wav")
            self.audio.play()

    def Emergency_cancel(self):
        self.isEmergency = False
        self.data_in("help", "isEmergency", False)
        self.audio.load("data/alarm_cancle.wav")
        self.audio.play()
        while self.audio.get_busy():
            time.sleep(5)
        self.parent.client.publish("Buzz", '0')

    #stage 1 speaker on, 
    def EmergencyCall(self):
        print("EmergencyCall")
        send.send_to_119(2)
        self.audio.load("data/alarm_3.wav")
        self.audio.play()
        while self.audio.get_busy():
            time.sleep(5)
        self.parent.client.publish("Buzz", '1')



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
    room_list = ["room1", "room2", "room3"] #id 1,2,3
    app = SafeCare(room_list)
    n = time.time()
    app.data_in(2,"cds",0)
    app.data_in(2, "cds", 400)
    app.data_in(2, "cds", 0)
    app.data_in(1, "pir", 1)
    app.data_in(3, "cds", 500)
    app.print_all()
    a = time.time()
    print(a-n)
