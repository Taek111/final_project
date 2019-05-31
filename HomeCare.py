import time
import Queue as queue
from firebase import firebase
import threading

room_list = ["room1", "room2", "room3"] #id 1,2

class HomeCare():

    def __init__(self,room_list):

        #firebase 
        self.db = firebase.FirebaseApplication("https://test-4ac24.firebaseio.com/", None)
        #room 
        self.rooms = {}
        for id in range(1,len(room_list)+1):
            self.rooms[id] = Room(self, id)

        #setting variable 
        self.EmergencyCall = False
        self.isEmergency = False
        self.temperature = 0.0
        self.indoor = True
        self.isOpen = False 
        self.active_log = time.time()


    def data_in(self, id, topic, value):
        if topic == "cds":
            if value < 100:
                lightOn = True
            else:
                lightOn = False
            if not self.rooms[id].light == lightOn:
                self.updateDB(id, topic, lightOn)
                self.active_log = time.time()
            self.rooms[id].light = lightOn

        elif topic == "pir":
            if not value:
                self.rooms[id].pir = int(time.time())
                self.updateDB(id, topic, self.rooms[id].pir)
                self.active_log = self.rooms[id].pir

        elif topic == "temperature":
            self.temperature = value
            #todo:firebase
        elif topic == "ir":
			if value: # if ir value is HIGH
				self.isOpen = True
				self.check_indoor()

        elif topic == "ir":
            if not value: #check which value is right
                check_10m = threading.Thread(target=self.check_indoor, arguments=(time.time()))
                check_10m.start()


    def detectEmergentcy(self):
        self.cur_time = int(time.time())
        if (self.cur_time - self.active_log) > 3600: #1 hour
            self.isEmergency = True

    def updateDB(self,id, topic, value):
        #cds lightlog = int(time.time())

        if topic == "cds":
            self.db.patch('/user/test/'+ room_list[id-1], {'Light': value})
            self.db.patch('/user/test', {'Lightlog': int(time.time())})

        if topic == "pir":
            self.db.patch('/user/test/'+ room_list[id-1], {'PIR': value})

    def check_indoor(self, time_start):
        while(time.time() - time_start < 600):
            log_list = list()
            for id in range(1, len(room_list) + 1):
                log_list.append(self.rooms[id].pir)
            log_list.append(self.active_log)
            if max(log_list) > time_start:
                self.indoor = True
                return
        self.indoor = False

    def check_indoor(self, interval = 60):
		if not self.isOpen:
			return
		log_list = list()
        for id in range(1,len(room_list)+1):
            log_list.append(self.rooms[id].pir)
		if time.time() - max(log_list) > 600:
			self.indoor = False
         else:
			self.indoor = True
		threading.Timer(interval, self.check_indoor()).start() 
		
			
			
>>>>>>> 701a51aea384bde20a1448e33bb30b132da059f6
    #ir sensor -> immediate state -> find indoor 
    def Emergency_state(self):
        pass
    #stage 1 speaker on, 

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
