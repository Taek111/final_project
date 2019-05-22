import time
import queue
from firebase import firebase

room_list = ["room1", "room2", "room3"] #id 1,2

class HomeCare():

    def __init__(self,room_list):

        #firebase 연결
        self.db = firebase.FirebaseApplication("https://test-4ac24.firebaseio.com/", None)
        #room 객체 생성
        self.rooms = {}
        for id in range(1,len(room_list)+1):
            self.rooms[id] = Room(self, id)

        #변수 설정
        self.EmergencyCall = False
        self.isEmergency = False
        self.temperature = 0.0
        self.indoor = True  #초기상태는 재실상태라고 가정
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
            if value:
                self.rooms[id].pir = int(time.time())
                self.updateDB(id, topic, self.rooms[id].pir)
                self.active_log = self.rooms[id].pir

        elif topic == "temperature":
            self.temperature = value
            #firebase에 업로드할 방식 생각해야함.

    def detectEmergentcy(self):
        self.cur_time = int(time.time())
        if (self.cur_time - self.active_log) > 3600: #1시간 동안 활동 미감지시
            self.isEmergency = True

    def updateDB(self,id, topic, value):
        #cds 바뀔때 lightlog = int(time.time())

        if topic == "cds":
            self.db.patch('/user/test/'+ room_list[id-1], {'Light': value})
            self.db.patch('/user/test', {'Lightlog': int(time.time())})

        if topic == "pir":
            self.db.patch('/user/test/'+ room_list[id-1], {'PIR': value})

    def check_indoor(self):
        pass
    #ir 센서를 읽고 판단상태에 돌입한 뒤 일정 시간 후 최근 감지 시간 확인
    def Emergency_state(self):
        pass
    #1단계 speaker on, 사용자 음성 확인 일정시간 후 2단계 어플리케이션 알람, 3단계 119 call


    def print_all(self):
        for id in range(1, len(self.rooms)+1):
            self.rooms[id].print_state()

class Room():
    def __init__(self, parent, id):
        self.parent = parent
        self.id = id
        self.light = None
        self.pir = None
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