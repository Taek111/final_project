
#include <SPI.h>  
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define IR    D6  // IR   -> D6 pin
#define Buzz  D0  // Buzz -> D0 pin

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

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
    if (!strcmp(topic, "Buzz")){ //topic이 Buzz이면 if문안으로 들어감
      if ((char)payload[0] == '1') {
        digitalWrite(Buzz, HIGH);   
    } else {
      digitalWrite(Buzz, LOW);  
    }
  }
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
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  pinMode(D6, INPUT);
  pinMode(D0, OUTPUT);
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  Serial.print("Client State : ");
  Serial.println(client.state());
  delay(1000);
  
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  int A = digitalRead(IR); // A가 0(LOW)이면 현관문이 닫힌 상태, 1(HIGH)면 열린 상태임
  char *ir_ptr = (char*)&A;
  if(A == 1 && A != tmp){
    client.publish("isOpen", ir_ptr);
    Serial.println("IR detected");
  }
  tmp = A;
  
}
