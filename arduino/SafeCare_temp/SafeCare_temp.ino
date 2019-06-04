#include <DallasTemperature.h>

#include <OneWire.h>

#define ONE_WIRE_BUS D4

/********************************************************************/
// Setup a oneWire instance to communicate with any OneWire devices  
// (not just Maxim/Dallas temperature ICs) 
OneWire oneWire(ONE_WIRE_BUS); 
 
/********************************************************************/
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);
/********************************************************************/ 

#include <SPI.h>  
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Update these with values suitable for your network.

const char* ssid = "Ka";
const char* password = "skkulove";
const char* mqtt_server = "192.168.0.8";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;
int tmp;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266_out";
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe("Buzz"); //Buzz topic subscribe
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  pinMode(D4, INPUT);
  Serial.begin(9600);
  sensors.begin(); 
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  Serial.print("Client State : ");
  Serial.println(client.state());
  delay(10000);
  
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  sensors.requestTemperatures(); // Send the command to get temperature readings 
  int T = sensors.getTempCByIndex(0);
  unsigned short *temp_ptr = (unsigned short*)&T;
  char temp[2] = {temp_ptr[0], temp_ptr[1]};
  client.publish("temperature", temp);
  Serial.print("temperature is ");
  Serial.println(T);
  
 /*
  if( T<29 ) {
    client.publish("Temper is below 29");
    Serial.println("IR detected");
  }*/
}
