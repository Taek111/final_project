import paho.mqtt.client as mqtt
import time
import struct
import HomeCare

room_list = ["room1", "room2", "room3"] #id 1,2
app = HomeCare.HomeCare(room_list)


def on_connect(client, userdata, rc):
    print("connected")
    client.subscribe("connected")

def on_message(client, userdata, msg):
	
	topic = str(msg.topic.decode("utf-8"))
	if topic == "cds":
		id,con = struct.unpack('<BB', msg.payload[0:2])
	elif topic == "pir":
		id,con = struct.unpack('<BB', msg.payload[0:2])

	# if topic == "ir":
    #     id ="outdoor"

	elif topic == "ir":
		id = "outdoor"
		con = struct.unpack('B', msg.payload)

	print(topic, id, con)
	app.data_in(id, topic, con)
	
	
    #print("topic:%s id:%d con:%d"%(topic, id, con))
    #print("Topic:" + str(msg.topic.decode("utf-8")) + \
    #        '\nMessage: '+ str(struct.unpack('h', msg.payload)[0]))

def main():
    client = mqtt.Client()
    client.connect("192.168.0.8", 1883, 60)
    client.subscribe("cds")
    client.subscribe("pir")
    client.on_message = on_message		
    print("client connected")
    client.loop_forever()

if __name__ == "__main__":
    main()
