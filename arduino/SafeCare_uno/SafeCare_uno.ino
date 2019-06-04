#include <SPI.h>  
#include <SoftwareSerial.h>
#include "VoiceRecognitionV3.h"
/**        
  Connection
  Arduino    VoiceRecognitionModule
   2   ------->     TX
   3   ------->     RX
*/
VR myVR(2,3);    // 2:RX 3:TX, you can choose your favourite pins.

uint8_t records[7]; // save record
uint8_t buf[64];


#define off     (0)
#define help1   (1)
#define ok2     (2)
#define help3   (3)
#define ok4     (4)
#define help5   (5)
#define ok6     (6)
#define help7   (7)
#define ok8     (8)

#include <WiFiNINA.h>

#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiServer.h>
#include <WiFiUdp.h>
#include <PubSubClient.h>

#define SECRET_SSID "Ka" //Replace with your Wifi SSID
#define SECRET_PASS "skkulove"//Replace with your WPA2 password
int status = WL_IDLE_STATUS;
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
byte server[] = {192,168,0,8}; //Local Mosquitto server - please replace it with the IP of your local mosquitto server after running ipconfig
int port = 1883; //the port of the MQTT broker
const char* topicToSubscribe = "s_test";
unsigned char id = 1;

int prev_cds = 0;
int pir_pin = 4;

// Handles messages arrived on subscribed t `opic(s)
void callback(char* topic, byte* payload, unsigned int length) {
  String result;
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
    result += (char)payload[i];
  }
  Serial.println("");
}

WiFiClient wifiClient;
PubSubClient mqttClient(server, port, callback, wifiClient);//Local Mosquitto Connection

void setup() {
    /** initialize */
  myVR.begin(9600);
  
  pinMode(10, INPUT);
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
  myVR.load((uint8_t)off);
  myVR.load((uint8_t)help1);
  myVR.load((uint8_t)ok2);
  myVR.load((uint8_t)help3);
  myVR.load((uint8_t)ok4);
  myVR.load((uint8_t)help5);
  myVR.load((uint8_t)ok6);
  myVR.load((uint8_t)help7);
  myVR.load((uint8_t)ok8);
  pinMode(pir_pin, INPUT);
  pinMode(A0, INPUT);
  
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }


  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < "1.0.0") {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to Wifi network:
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("hi, Attempting to connect to WPA SSID: ");
    Serial.print(ssid);
    // Connect to WPA/WPA2 network:
    
    WiFi.begin(ssid,pass);
    Serial.println(" ");
    // wait 10 seconds for connection:
    delay(1000);
  }

  // you're connected now, so print out the data:
  Serial.print("You're connected to the network");
  printCurrentNet();
  printWifiData();
  //WiFi Connection -- End
  
  
  
  
  //Local Mosquitto Connection -- Start
  if (mqttClient.connect("myClientID_1")) {
    // connection succeeded
    Serial.println("Connection succeeded.");
    Serial.print("Subscribing to the topic [");
    Serial.print(topicToSubscribe);
    Serial.println("]");
    mqttClient.subscribe(topicToSubscribe);
    Serial.println("Successfully subscribed to the topic.");
    //Serial.println("Publishing...");
    
   } else {
      // connection failed
      // mqttClient.state() will provide more information
      // on why it failed.
      Serial.print("Connection failed. MQTT client state is: ");
      Serial.println(mqttClient.state());
   }
  //Local Mosquitto Connection -- End

}


void(* resetFunc) (void) = 0;//declare reset function at address 0


void loop() {
  int ret;
  ret = myVR.recognize(buf, 50);
  if(ret>0){
      switch(buf[1]){
      case off:
        /** turn on led */
        digitalWrite(8, LOW);
        break;
      case help1:
        /** turn off buzzer*/
        help_payload(true);
        digitalWrite(8, HIGH);
        break;
      case ok2:
        /** turn on buzzer*/
        help_payload(false);
        digitalWrite(8, LOW);
        break;
      case help3:
        /** turn off led*/
        help_payload(true);
        digitalWrite(8, HIGH);
        break;
      case ok4:
        /** turn on led */
        help_payload(false);
        digitalWrite(8, LOW);
        break;
      case help5:
        /** turn on led */
        help_payload(true);
        digitalWrite(8, HIGH);
        break;
      case ok6:
        /** turn off led */
        help_payload(false);
        digitalWrite(8, LOW);
        break;
      case help7:
        /** turn on led */
        help_payload(true);
        digitalWrite(8, HIGH);
        break;
      case ok8:
        /** turn off led */
        help_payload(false);
        digitalWrite(8, LOW);
        break;                
      default:
        Serial.println("Record function undefined");
        break;
    }
  }
  
  int pirValue = digitalRead(pir_pin);  
  int cdsValue = analogRead(A0);
  int cur_cds = cdsValue < 100 ? 1 : 0;
  if (cur_cds != prev_cds){
    byte *cds_ptr = (byte *)&cur_cds;
    byte cds[2] = {id, *cds_ptr};
    mqttClient.publish("cds", cds,2,false);
  }
  if (pirValue == 1){
    byte *pir_ptr = (byte*)&pirValue;
    byte  pir[2] = {id, *pir_ptr};
    mqttClient.publish("pir", pir,2,false);
  }
  
//  byte* realcds = (byte*)&cdsValue;
//  byte real_cds[3] = {id, realcds[0], realcds[1]};
//  mqttClient.publish("realcds", real_cds, 3, false);
  
  Serial.print("cds value: ");
  Serial.println(cdsValue);
  Serial.print("pir value: ");
  Serial.println(pirValue);  
  Serial.print("Client state: ");
  Serial.println(mqttClient.state());
  
  if(mqttClient.state() < 0) {
    Serial.print(mqttClient.state());
    Serial.print(WiFi.status());
    resetFunc(); //call reset 
    Serial.println("ReeeeSeeeett~~!!");
  }
  
  prev_cds = cur_cds;
  mqttClient.loop();
  delay(1000);
}



void printWifiData() {
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  Serial.println(ip);

  // print your MAC address:
  byte mac[6];
  WiFi.macAddress(mac);
  Serial.print("MAC address: ");
  printMacAddress(mac);
}

void printCurrentNet() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the MAC address of the router you're attached to:
  byte bssid[6];
  WiFi.BSSID(bssid);
  Serial.print("BSSID: ");
  printMacAddress(bssid);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);

  // print the encryption type:
  byte encryption = WiFi.encryptionType();
  Serial.print("Encryption Type:");
  Serial.println(encryption, HEX);
  Serial.println();
}

void printMacAddress(byte mac[]) {
  for (int i = 5; i >= 0; i--) {
    if (mac[i] < 16) {
      Serial.print("0");
    }
    Serial.print(mac[i], HEX);
    if (i > 0) {
      Serial.print(":");
    }
  }
  Serial.println();
}

byte help_payload(bool ishelp){
  byte *helpcall = (byte*)&ishelp;
  mqttClient.publish("help", *helpcall,1,false);
}
