import paho.mqtt.client as mqtt
import time
import struct
import HomeCare
import threading
import config



def on_connect(client, userdata, rc):
    print("connected")
    client.subscribe("connected")

def on_message(client, userdata, msg):
    
    topic = str(msg.topic)
    print(topic)
    if topic == "cds":
        id,con = struct.unpack('<BB', msg.payload[0:2])
    elif topic == "pir":
        id,con = struct.unpack('<BB', msg.payload[0:2])

    elif topic == "isOpen":
        id = "isOpen"
        con = struct.unpack('b', msg.payload[0:2])[0]
    elif topic == "help":
        id = "helpcall"
        con = struct.unpack('B', msg.payload)[0]
        if not con:#voice "help"
            while not app.isEmergency:
                app.isEmergency = True
                Eapp = threading.Thread(target=app.Emergency_one)
                Eapp.start()
        else: # voice "ok"
            if app.audio.get_busy():
                app.audio.stop()
            app.isEmergency = False
    elif topic == "temperature":
        id = "temp_mini"
        con = struct.unpack('B',msg.payload)[0]
   # elif topic == "realcds":
    #    id = "value"
     #   con=struct.unpack('<Bh',msg.payload[0:3])



    print(topic, id, con)
    app.data_in(id, topic, con)
    
	
	
    #print("topic:%s id:%d con:%d"%(topic, id, con))
    #print("Topic:" + str(msg.topic.decode("utf-8")) + \
    #        '\nMessage: '+ str(struct.unpack('h', msg.payload)[0]))
def client_setup():
    client = mqtt.Client()
    client.connect("192.168.0.8", 1883, 60)
    client.subscribe("cds")
    client.subscribe("pir")
    client.subscribe("help")
    client.subscribe("isOpen")
    client.subscribe("temperature")
    client.subscribe("realcds")
    client.on_message = on_message
    print("client connected")
    client.loop_forever()


if __name__ == "__main__":

    username = config.username
    room_list = config.username
    appUser_num = config.appUser_num
    app = HomeCare.HomeCare(room_list, username, appUser_num)

    client_setup()
