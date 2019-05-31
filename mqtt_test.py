import paho.mqtt.client as mqtt
import time
import struct
import HomeCare

room_list = ["room1", "room2"] #id 1,2
app = HomeCare.HomeCare(room_list)


def on_connect(client, userdata, rc):
    print("connected")
    client.subscribe("connected")

def on_message(client, userdata, msg):
	
	topic = str(msg.topic.decode("utf-8"))
	if topic == "cds":
		id,con = struct.unpack('<Bh', msg.payload[0:3])
	elif topic == "pir":
		id,con = struct.unpack('<BB', msg.payload[0:2])
<<<<<<< HEAD
	# if topic == "ir":
    #     id ="outdoor"

=======
	elif topic == "ir":
		id = "outdoor"
		con = struct.unpack('B', msg.payload)
	
>>>>>>> 701a51aea384bde20a1448e33bb30b132da059f6
	print(topic, id, con)
	app.data_in(id, topic, con)
	app.print_all()
	
    #print("topic:%s id:%d con:%d"%(topic, id, con))
    #print("Topic:" + str(msg.topic.decode("utf-8")) + \
    #        '\nMessage: '+ str(struct.unpack('h', msg.payload)[0]))

def main():
    client = mqtt.Client()
    client.connect("192.168.43.146", 1883, 60)
    client.subscribe("cds")
    client.subscribe("pir")
    client.on_message = on_message		
    print("client connected")
    client.loop_forever()

if __name__ == "__main__":
    main()
